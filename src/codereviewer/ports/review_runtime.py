from __future__ import annotations

from typing import Protocol

from codereviewer.core.models import Finding, RuntimeProfile
from codereviewer.services.context_budget import FileChangeContext


class ReviewRuntime(Protocol):
    def analyze(
        self,
        changes: list[FileChangeContext],
        profile: RuntimeProfile | None = None,
        *,
        tenant_id: str,
        agent_id: str | None,
        run_id: str,
    ) -> list[Finding]:
        ...
