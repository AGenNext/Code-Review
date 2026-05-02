from __future__ import annotations

from codereviewer.core.models import Finding, RuntimeProfile
from codereviewer.services.claude_agent_sdk import ClaudeAgentSDKReviewer
from codereviewer.services.context_budget import FileChangeContext


class LocalRulesReviewRuntime:
    def __init__(self) -> None:
        self._reviewer = ClaudeAgentSDKReviewer()

    def analyze(
        self,
        changes: list[FileChangeContext],
        profile: RuntimeProfile | None = None,
        *,
        tenant_id: str,
        agent_id: str | None,
        run_id: str,
    ) -> list[Finding]:
        del profile, tenant_id, agent_id, run_id
        return self._reviewer._analyze_with_local_rules(changes)
