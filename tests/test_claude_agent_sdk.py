from __future__ import annotations

import pytest

from codereviewer.core.models import FileChangeContext, RuntimeProfile
from codereviewer.services.claude_agent_sdk import ClaudeAgentSDKReviewer


def test_local_fallback_finds_todo(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "false")
    reviewer = ClaudeAgentSDKReviewer()
    findings = reviewer.analyze([FileChangeContext(path="a.py", change_type="modified", patch="@@\n+# TODO fix later")])
    assert findings
    assert any("TODO" in finding.title for finding in findings)


def test_sdk_path_parses_findings(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.setenv("CLAUDE_API_KEY", "sk-ant-test")
    reviewer = ClaudeAgentSDKReviewer()

    def fake_call(api_key: str, model: str, payload: str) -> str:
        assert api_key == "sk-ant-test"
        assert model == "claude-sonnet-4"
        assert "changes" in payload
        return (
            '{"findings":[{"title":"Secret leak","description":"Hardcoded secret","severity":"critical",'
            '"category":"security","file_path":"app.py","line_start":10,"line_end":10,"confidence":0.9,'
            '"evidence":"password=123","remediation":"Move secret to env"}]}'
        )

    monkeypatch.setattr(reviewer, "_call_claude_api", fake_call)
    findings = reviewer.analyze([FileChangeContext(path="app.py", change_type="modified", patch="@@\n+password=123")])
    assert len(findings) == 1
    assert findings[0].file_path == "app.py"
    assert findings[0].provenance == "claude-agent-sdk"


def test_sdk_uses_profile_key_and_model(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
    reviewer = ClaudeAgentSDKReviewer()

    captured: dict[str, str] = {}

    def fake_call(api_key: str, model: str, payload: str) -> str:
        captured["api_key"] = api_key
        captured["model"] = model
        return '{"findings":[]}'

    monkeypatch.setattr(reviewer, "_call_claude_api", fake_call)
    profile = RuntimeProfile(
        name="p1",
        provider="anthropic",
        model_id="claude-sonnet-4",
        auth_reference="sk-ant-profile-key",
    )
    findings = reviewer.analyze([FileChangeContext(path="app.py", change_type="modified", patch="@@\n+print('ok')")], profile=profile)
    assert findings == []
    assert captured["api_key"] == "sk-ant-profile-key"
    assert captured["model"] == "claude-sonnet-4"


def test_sdk_strict_mode_raises(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.setenv("CLAUDE_AGENT_SDK_STRICT", "true")
    monkeypatch.setenv("CLAUDE_API_KEY", "sk-ant-test")
    reviewer = ClaudeAgentSDKReviewer()

    def fake_call(*_args, **_kwargs):
        raise RuntimeError("sdk unavailable")

    monkeypatch.setattr(reviewer, "_call_claude_api", fake_call)
    with pytest.raises(RuntimeError):
        reviewer.analyze([FileChangeContext(path="a.py", change_type="modified", patch="@@\n+TODO")])


def test_litellm_path_parses_findings(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.setenv("LITELLM_ENABLED", "true")
    reviewer = ClaudeAgentSDKReviewer()

    def fake_call(model: str, payload: str) -> str:
        assert model == "anthropic/claude-sonnet-4"
        assert "changes" in payload
        return (
            '{"findings":[{"title":"Gateway finding","description":"from litellm","severity":"medium",'
            '"category":"quality","file_path":"b.py","line_start":2,"line_end":2,"confidence":0.7,'
            '"evidence":"x","remediation":"y"}]}'
        )

    monkeypatch.setattr(reviewer, "_call_litellm_api", fake_call)
    findings = reviewer.analyze([FileChangeContext(path="b.py", change_type="modified", patch="@@\n+x=1")])
    assert len(findings) == 1
    assert findings[0].title == "Gateway finding"
    assert findings[0].provenance == "claude-agent-sdk"


def test_litellm_model_uses_profile_conversion(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.setenv("LITELLM_ENABLED", "true")
    reviewer = ClaudeAgentSDKReviewer()
    profile = RuntimeProfile(
        name="p2",
        provider="anthropic",
        model_id="claude-sonnet-4",
        auth_reference="ignored",
    )
    assert reviewer._resolve_litellm_model(profile) == "anthropic/claude-sonnet-4"


def test_litellm_model_uses_provider_prefix_map(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.setenv("LITELLM_ENABLED", "true")
    reviewer = ClaudeAgentSDKReviewer()
    profile = RuntimeProfile(
        name="p3",
        provider="vertex",
        model_id="claude-sonnet-4",
        auth_reference="ignored",
    )
    assert reviewer._resolve_litellm_model(profile) == "vertex_ai/claude-sonnet-4"


def test_litellm_model_uses_metadata_override(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.setenv("LITELLM_ENABLED", "true")
    reviewer = ClaudeAgentSDKReviewer()
    profile = RuntimeProfile(
        name="p4",
        provider="anthropic",
        model_id="claude-sonnet-4",
        auth_reference="ignored",
        metadata={"litellm_model": "bedrock/anthropic.claude-sonnet-4"},
    )
    assert reviewer._resolve_litellm_model(profile) == "bedrock/anthropic.claude-sonnet-4"


def test_litellm_model_uses_custom_provider_map(monkeypatch) -> None:
    monkeypatch.setenv("CLAUDE_AGENT_SDK_ENABLED", "true")
    monkeypatch.setenv("LITELLM_ENABLED", "true")
    monkeypatch.setenv("LITELLM_PROVIDER_PREFIX_MAP", '{"google":"vertex_ai","aws":"bedrock/"}')
    reviewer = ClaudeAgentSDKReviewer()
    profile = RuntimeProfile(
        name="p5",
        provider="anthropic",
        model_id="claude-sonnet-4",
        auth_reference="ignored",
        metadata={"litellm_provider": "google"},
    )
    assert reviewer._resolve_litellm_model(profile) == "vertex_ai/claude-sonnet-4"
