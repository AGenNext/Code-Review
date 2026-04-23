from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request

from codereviewer.core.logic import recommendation_for_severity
from codereviewer.core.models import FileChangeContext, Finding, FindingCategory, RuntimeProfile, Severity


def _is_enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _default_litellm_provider_prefixes() -> dict[str, str]:
    return {
        "anthropic": "anthropic/",
        "vertex": "vertex_ai/",
        "bedrock": "bedrock/",
        "foundry": "azure/",
    }


class ClaudeAgentSDKReviewer:
    """Claude Agent SDK adapter boundary.

    Behavior:
    - If `CLAUDE_AGENT_SDK_ENABLED=true`, runs a real Claude API review call.
    - Otherwise falls back to deterministic local rules for tests/dev.
    """

    def __init__(self) -> None:
        self.sdk_enabled = _is_enabled(os.getenv("CLAUDE_AGENT_SDK_ENABLED"))
        self.strict_mode = _is_enabled(os.getenv("CLAUDE_AGENT_SDK_STRICT"))
        self.default_model = os.getenv("CLAUDE_AGENT_SDK_MODEL", "claude-sonnet-4")
        self.max_tokens = int(os.getenv("CLAUDE_AGENT_SDK_MAX_TOKENS", "2048"))
        self.temperature = float(os.getenv("CLAUDE_AGENT_SDK_TEMPERATURE", "0.1"))
        self.litellm_enabled = _is_enabled(os.getenv("LITELLM_ENABLED"))
        self.litellm_base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:4000").rstrip("/")
        self.litellm_api_key = os.getenv("LITELLM_API_KEY", "")
        self.litellm_model = os.getenv("LITELLM_MODEL", "anthropic/claude-sonnet-4")
        self.litellm_provider_prefixes = self._load_litellm_provider_prefixes()

    def analyze(self, changes: list[FileChangeContext], profile: RuntimeProfile | None = None) -> list[Finding]:
        if self.sdk_enabled:
            try:
                return self._analyze_with_sdk(changes, profile)
            except Exception:
                if self.strict_mode:
                    raise

        return self._analyze_with_local_rules(changes)

    def _analyze_with_local_rules(self, changes: list[FileChangeContext]) -> list[Finding]:
        findings: list[Finding] = []
        for change in changes:
            findings.extend(self._analyze_added_lines(change))
        return self._dedupe(findings)

    def _analyze_with_sdk(self, changes: list[FileChangeContext], profile: RuntimeProfile | None = None) -> list[Finding]:
        payload = self._build_review_payload(changes)
        if self.litellm_enabled:
            model = self._resolve_litellm_model(profile)
            response_text = self._call_litellm_api(model=model, payload=payload)
        else:
            api_key = self._resolve_api_key(profile)
            model = profile.model_id if profile and profile.model_id else self.default_model
            response_text = self._call_claude_api(api_key=api_key, model=model, payload=payload)
        parsed = self._parse_sdk_findings(response_text)
        return self._dedupe(parsed)

    def _resolve_litellm_model(self, profile: RuntimeProfile | None = None) -> str:
        if profile and profile.metadata.get("litellm_model"):
            return str(profile.metadata["litellm_model"])

        if profile and profile.model_id:
            if "/" in profile.model_id:
                return profile.model_id
            provider_key = str(profile.metadata.get("litellm_provider") or profile.provider.value).strip().lower()
            prefix = self.litellm_provider_prefixes.get(provider_key, "anthropic/")
            return f"{prefix}{profile.model_id}"
        return self.litellm_model

    def _load_litellm_provider_prefixes(self) -> dict[str, str]:
        configured = os.getenv("LITELLM_PROVIDER_PREFIX_MAP", "").strip()
        prefixes = _default_litellm_provider_prefixes()
        if not configured:
            return prefixes
        try:
            parsed = json.loads(configured)
        except json.JSONDecodeError:
            return prefixes
        if not isinstance(parsed, dict):
            return prefixes
        for key, value in parsed.items():
            if not isinstance(key, str) or not isinstance(value, str):
                continue
            normalized = value if value.endswith("/") else f"{value}/"
            prefixes[key.strip().lower()] = normalized
        return prefixes

    def _resolve_api_key(self, profile: RuntimeProfile | None = None) -> str:
        if profile and profile.auth_reference.startswith("sk-ant-"):
            return profile.auth_reference
        key = os.getenv("CLAUDE_API_KEY", "")
        if not key:
            raise ValueError("Claude SDK integration enabled but CLAUDE_API_KEY is not configured")
        return key

    def _build_review_payload(self, changes: list[FileChangeContext]) -> str:
        serialized = []
        for change in changes:
            serialized.append(
                {
                    "path": change.path,
                    "change_type": change.change_type,
                    "patch": change.patch,
                }
            )
        return json.dumps({"changes": serialized}, ensure_ascii=True)

    def _call_claude_api(self, api_key: str, model: str, payload: str) -> str:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        system = (
            "You are a strict code review agent. Return only valid JSON with shape: "
            '{"findings":[{"title":"...","description":"...","severity":"critical|high|medium|low|info",'
            '"category":"security|quality|maintainability","file_path":"...","line_start":1,"line_end":1,'
            '"confidence":0.0,"evidence":"...","remediation":"..."}]}.'
        )
        message = client.messages.create(
            model=model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"Review these code changes and emit findings JSON only:\n{payload}",
                }
            ],
        )
        return self._extract_text(message.content)

    def _call_litellm_api(self, model: str, payload: str) -> str:
        system = (
            "You are a strict code review agent. Return only valid JSON with shape: "
            '{"findings":[{"title":"...","description":"...","severity":"critical|high|medium|low|info",'
            '"category":"security|quality|maintainability","file_path":"...","line_start":1,"line_end":1,'
            '"confidence":0.0,"evidence":"...","remediation":"..."}]}.'
        )
        body = {
            "model": model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Review these code changes and emit findings JSON only:\n{payload}"},
            ],
        }
        endpoint = f"{self.litellm_base_url}/v1/chat/completions"
        raw = self._post_json(endpoint, body, self.litellm_api_key)
        data = json.loads(raw)
        choices = data.get("choices", []) if isinstance(data, dict) else []
        if not choices:
            raise ValueError("LiteLLM gateway response did not include choices")
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, list):
            return "\n".join(str(part.get("text", "")) for part in content if isinstance(part, dict)).strip()
        return str(content)

    def _post_json(self, url: str, payload: dict[str, object], bearer_token: str | None = None) -> str:
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        request = urllib.request.Request(url=url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LiteLLM gateway request failed: HTTP {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LiteLLM gateway request failed: {exc.reason}") from exc

    def _extract_text(self, content: object) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: list[str] = []
            for part in content:
                text = getattr(part, "text", None)
                if isinstance(text, str):
                    chunks.append(text)
                elif isinstance(part, dict) and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
            return "\n".join(chunks).strip()
        return str(content)

    def _parse_sdk_findings(self, response_text: str) -> list[Finding]:
        raw = self._extract_json_block(response_text)
        data = json.loads(raw) if raw else {}
        items = data.get("findings", []) if isinstance(data, dict) else []
        findings: list[Finding] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            severity = self._severity_from_value(item.get("severity"))
            category = self._category_from_value(item.get("category"))
            finding = Finding(
                title=str(item.get("title", "Unnamed finding")),
                description=str(item.get("description", "")),
                severity=severity,
                recommendation=recommendation_for_severity(severity),
                file_path=str(item.get("file_path", "unknown")),
                category=category,
                confidence=float(item.get("confidence", 0.5)),
                evidence=str(item.get("evidence", "")) or None,
                remediation=str(item.get("remediation", "")) or None,
                line_start=self._to_int(item.get("line_start")),
                line_end=self._to_int(item.get("line_end")),
                provenance="claude-agent-sdk",
            )
            findings.append(finding)
        return findings

    def _extract_json_block(self, text: str) -> str:
        candidate = text.strip()
        if candidate.startswith("```"):
            lines = candidate.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            candidate = "\n".join(lines).strip()
        first = candidate.find("{")
        last = candidate.rfind("}")
        if first != -1 and last != -1 and last >= first:
            return candidate[first : last + 1]
        return candidate

    def _to_int(self, value: object) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _severity_from_value(self, value: object) -> Severity:
        raw = str(value or "").strip().lower()
        mapping = {
            "critical": Severity.critical,
            "high": Severity.high,
            "medium": Severity.medium,
            "low": Severity.low,
            "info": Severity.info,
        }
        return mapping.get(raw, Severity.low)

    def _category_from_value(self, value: object) -> FindingCategory:
        raw = str(value or "").strip().lower()
        mapping = {
            "security": FindingCategory.security,
            "quality": FindingCategory.quality,
            "maintainability": FindingCategory.maintainability,
        }
        return mapping.get(raw, FindingCategory.quality)

    def _analyze_added_lines(self, change: FileChangeContext) -> list[Finding]:
        result: list[Finding] = []
        for line_no, line in self._iter_added_lines(change.patch):
            line_lower = line.lower()
            if "todo" in line_lower:
                severity = Severity.low
                result.append(
                    Finding(
                        title="TODO left in code",
                        description="Detected TODO in newly added code.",
                        severity=severity,
                        recommendation=recommendation_for_severity(severity),
                        file_path=change.path,
                        line_start=line_no,
                        line_end=line_no,
                        category=FindingCategory.maintainability,
                        subtype="todo",
                        confidence=0.8,
                        evidence=line.strip(),
                        remediation="Convert TODO to a tracked ticket or complete implementation before merge.",
                        provenance="policy:maintainability/todo",
                    )
                )
            if "password" in line_lower or "secret" in line_lower:
                severity = Severity.critical
                result.append(
                    Finding(
                        title="Potential credential exposure",
                        description="Potential secret-like value found in added lines.",
                        severity=severity,
                        recommendation=recommendation_for_severity(severity),
                        file_path=change.path,
                        line_start=line_no,
                        line_end=line_no,
                        category=FindingCategory.security,
                        subtype="secret_exposure",
                        confidence=0.9,
                        evidence=line.strip(),
                        remediation="Use secure secret injection and remove plaintext credentials from source and history.",
                        provenance="policy:security/secret-scan",
                    )
                )
        return result

    def _iter_added_lines(self, patch: str) -> list[tuple[int, str]]:
        lines: list[tuple[int, str]] = []
        current_line = 1
        for raw in patch.splitlines():
            if raw.startswith("@@"):
                # fallback hunk handling: reset unknown; keep relative increment
                continue
            if raw.startswith("+") and not raw.startswith("+++"):
                lines.append((current_line, raw[1:]))
                current_line += 1
            elif raw.startswith("-") and not raw.startswith("---"):
                continue
            else:
                current_line += 1
        return lines

    def _dedupe(self, findings: list[Finding]) -> list[Finding]:
        unique: dict[str, Finding] = {}
        for finding in findings:
            key = f"{finding.file_path}:{finding.line_start}:{finding.subtype}:{finding.evidence}"
            finding.fingerprint = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
            unique[finding.fingerprint] = finding
        return list(unique.values())
