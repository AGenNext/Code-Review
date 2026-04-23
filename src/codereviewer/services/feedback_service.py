from codereviewer.core.models import ReviewFeedbackEvent
from codereviewer.infra.repositories import ReviewFeedbackRepository


class FeedbackService:
    """Guarded feedback ingestion for future improvement pipelines."""

    def __init__(self, repo: ReviewFeedbackRepository) -> None:
        self.repo = repo

    def record(self, event: ReviewFeedbackEvent) -> ReviewFeedbackEvent:
        return self.repo.save(event)

    def list(self, review_job_id: str | None = None) -> list[ReviewFeedbackEvent]:
        return self.repo.list(review_job_id=review_job_id)
