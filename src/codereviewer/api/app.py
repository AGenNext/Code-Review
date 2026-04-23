from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from codereviewer.core.models import MemoryRecord, Provider, ReviewFeedbackEvent, ReviewJob, RuntimeProfile
from codereviewer.infra.repositories import (
    MemoryRepository,
    ReviewFeedbackRepository,
    ReviewJobRepository,
    RuntimeProfileRepository,
    SQLiteRepository,
)
from codereviewer.services.claude_agent_sdk import ClaudeAgentSDKReviewer
from codereviewer.services.context_budget import ContextBudgetManager
from codereviewer.services.feedback_service import FeedbackService
from codereviewer.services.review_service import ReviewService
from codereviewer.services.runtime_service import RuntimeProfileService
from codereviewer.web.ui import INDEX_HTML

app = FastAPI(title="CodeReviewer")

storage = SQLiteRepository()
job_repo = ReviewJobRepository(storage)
profile_repo = RuntimeProfileRepository(storage)
memory_repo = MemoryRepository(storage)
feedback_repo = ReviewFeedbackRepository(storage)
review_service = ReviewService(job_repo, profile_repo, memory_repo, ClaudeAgentSDKReviewer(), ContextBudgetManager())
runtime_service = RuntimeProfileService(profile_repo)
feedback_service = FeedbackService(feedback_repo)


@app.get("/", response_class=HTMLResponse)
def ui() -> str:
    return INDEX_HTML


@app.get("/api/providers")
def providers() -> list[str]:
    return [p.value for p in Provider]


@app.get("/api/models")
def models(provider: Provider | None = None):
    return runtime_service.list_models(provider)


@app.get("/api/runtime-profiles")
def list_runtime_profiles() -> list[RuntimeProfile]:
    return runtime_service.list_profiles()


@app.post("/api/runtime-profiles")
def create_runtime_profile(profile: RuntimeProfile) -> RuntimeProfile:
    try:
        return runtime_service.create_profile(profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/reviews")
def submit_review(job: ReviewJob) -> ReviewJob:
    return review_service.submit(job)


@app.get("/api/reviews")
def list_reviews() -> list[ReviewJob]:
    return review_service.list()


@app.get("/api/reviews/{job_id}")
def get_review(job_id: str) -> ReviewJob:
    job = review_service.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/memory/{repository_name}")
def list_memory(repository_name: str, memory_type: str | None = None) -> list[MemoryRecord]:
    return memory_repo.list(repository_name=repository_name, memory_type=memory_type)


@app.post("/api/feedback")
def create_feedback(event: ReviewFeedbackEvent) -> ReviewFeedbackEvent:
    return feedback_service.record(event)


@app.get("/api/feedback")
def list_feedback(review_job_id: str | None = None) -> list[ReviewFeedbackEvent]:
    return feedback_service.list(review_job_id=review_job_id)
