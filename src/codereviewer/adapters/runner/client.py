from __future__ import annotations

import os

from codereviewer.core.models import Finding, RuntimeProfile
from codereviewer.services.context_budget import FileChangeContext


class RunnerReviewRuntime:
    """Runner-backed runtime placeholder.

    This skeleton keeps runtime selection model-agnostic and can be expanded
    to submit AGen CP tasks to AGenNext-Runner.
    """

    def __init__(self) -> None:
        self.enabled = (os.getenv("AGENNEXT_RUNNER_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"})

    def analyze(
        self,
        changes: list[FileChangeContext],
        profile: RuntimeProfile | None = None,
        *,
        tenant_id: str,
        agent_id: str | None,
        run_id: str,
    ) -> list[Finding]:
        del changes, profile, tenant_id, agent_id, run_id
        raise NotImplementedError("RunnerReviewRuntime skeleton: implement Runner task submission")
