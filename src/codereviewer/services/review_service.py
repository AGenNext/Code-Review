from codereviewer.core.logic import summarize_findings
from codereviewer.core.models import ReviewJob, ReviewJobStatus
from codereviewer.infra.repositories import InMemoryReviewJobRepository, InMemoryRuntimeProfileRepository
from codereviewer.services.claude_agent_sdk import ClaudeAgentSDKReviewer


class ReviewService:
    def __init__(
        self,
        job_repo: InMemoryReviewJobRepository,
        profile_repo: InMemoryRuntimeProfileRepository,
        reviewer: ClaudeAgentSDKReviewer,
    ) -> None:
        self.job_repo = job_repo
        self.profile_repo = profile_repo
        self.reviewer = reviewer

    def submit(self, job: ReviewJob) -> ReviewJob:
        job.status = ReviewJobStatus.running
        self.job_repo.save(job)
        profile = self.profile_repo.get(job.runtime_profile_id)
        if profile is None:
            job.status = ReviewJobStatus.failed
            job.error = "Runtime profile not found"
            return self.job_repo.save(job)

        findings = self.reviewer.analyze(job.changes)
        job.findings = findings
        job.summary = summarize_findings(findings)
        job.status = ReviewJobStatus.completed
        return self.job_repo.save(job)

    def get(self, job_id: str) -> ReviewJob | None:
        return self.job_repo.get(job_id)

    def list(self) -> list[ReviewJob]:
        return list(self.job_repo.list())
