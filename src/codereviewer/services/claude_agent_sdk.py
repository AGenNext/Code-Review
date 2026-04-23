from __future__ import annotations

import hashlib

from codereviewer.core.logic import recommendation_for_severity
from codereviewer.core.models import FileChangeContext, Finding, FindingCategory, Severity


class ClaudeAgentSDKReviewer:
    """Claude Agent SDK adapter boundary.

    This implementation keeps deterministic local rules for tests/dev.
    Production integration should replace `_analyze_added_lines` with real Claude Agent SDK calls.
    """

    def analyze(self, changes: list[FileChangeContext]) -> list[Finding]:
        findings: list[Finding] = []
        for change in changes:
            findings.extend(self._analyze_added_lines(change))
        return self._dedupe(findings)

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
