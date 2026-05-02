from datetime import datetime, timezone

from codereviewer.core.logic import summarize_findings
from codereviewer.core.models import MemoryRecord, ReviewJob, ReviewJobStatus
from codereviewer.infra.repositories import MemoryRepository, ReviewJobRepository, RuntimeProfileRepository
from codereviewer.ports.review_runtime import ReviewRuntime
from codereviewer.services.context_budget import ContextBudgetManager
from codereviewer.services.notification_service import NotificationService, should_notify_for_status


class ReviewService:
    def __init__(
        self,
        job_repo: ReviewJobRepository,
        profile_repo: RuntimeProfileRepository,
        memory_repo: MemoryRepository,
        reviewer: ReviewRuntime,
        context_budget: ContextBudgetManager,
        notification_service: NotificationService | None = None,
    ) -> None:
        self.job_repo = job_repo
        self.profile_repo = profile_repo
        self.memory_repo = memory_repo
        self.reviewer = reviewer
        self.context_budget = context_budget
        self.notification_service = notification_service

    def submit(self, job: ReviewJob) -> ReviewJob:
        job.queued_at = datetime.now(timezone.utc)
        job.status = ReviewJobStatus.queued
        self.job_repo.save(job)

        job.started_at = datetime.now(timezone.utc)
        job.status = ReviewJobStatus.running
        self.job_repo.save(job)

        profile = self.profile_repo.get(job.runtime_profile_id, tenant_id=job.tenant_id)
        if profile is None:
            job.status = ReviewJobStatus.failed
            job.error = "Runtime profile not found"
            job.completed_at = datetime.now(timezone.utc)
            saved = self.job_repo.save(job)
            self._notify(saved)
            return saved

        try:
            budget = min(profile.max_tokens * 4, 48_000)
            selected_chunks = self.context_budget.select_chunks(job.changes)
            compressed = [change.model_copy(update={"patch": chunk.content}) for change, chunk in zip(job.changes, selected_chunks, strict=False)]
            findings = self.reviewer.analyze(
                compressed,
                profile=profile,
                tenant_id=job.tenant_id,
                agent_id=job.agent_id,
                run_id=job.id,
            )
            job.findings = findings
            job.summary = summarize_findings(findings)
            job.status = ReviewJobStatus.completed
            self.memory_repo.save(
                MemoryRecord(
                    tenant_id=job.tenant_id,
                    agent_id=job.agent_id,
                    repository_name=job.repository.name,
                    memory_type="review_history",
                    key=f"review:{job.id}",
                    value=f"status={job.status.value}; findings={len(findings)}; budget_chars={budget}",
                )
            )
        except Exception as exc:  # deliberate boundary for worker failures
            job.status = ReviewJobStatus.failed
            job.error = str(exc)
        finally:
            job.completed_at = datetime.now(timezone.utc)

        saved = self.job_repo.save(job)
        self._notify(saved)
        return saved

    def get(self, job_id: str, tenant_id: str | None = None) -> ReviewJob | None:
        return self.job_repo.get(job_id, tenant_id=tenant_id)

    def list(self, tenant_id: str | None = None) -> list[ReviewJob]:
        return list(self.job_repo.list(tenant_id=tenant_id))

    def _notify(self, job: ReviewJob) -> None:
        if not self.notification_service:
            return
        if not should_notify_for_status(job.status):
            return
        self.notification_service.notify_review_result(job)
