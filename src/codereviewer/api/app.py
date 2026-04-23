from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from codereviewer.core.models import Provider, ReviewJob, RuntimeProfile
from codereviewer.infra.repositories import InMemoryReviewJobRepository, InMemoryRuntimeProfileRepository
from codereviewer.services.claude_agent_sdk import ClaudeAgentSDKReviewer
from codereviewer.services.review_service import ReviewService
from codereviewer.services.runtime_service import RuntimeProfileService
from codereviewer.web.ui import INDEX_HTML

app = FastAPI(title="AgentNxt CodeReviewer")

job_repo = InMemoryReviewJobRepository()
profile_repo = InMemoryRuntimeProfileRepository()
review_service = ReviewService(job_repo, profile_repo, ClaudeAgentSDKReviewer())
runtime_service = RuntimeProfileService(profile_repo)


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
    return runtime_service.create_profile(profile)


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
