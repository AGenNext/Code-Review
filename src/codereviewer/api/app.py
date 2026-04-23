import os
from pathlib import Path
from dataclasses import dataclass

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

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
from codereviewer.services.notification_service import NotificationService
from codereviewer.services.observability_service import configure_signoz
from codereviewer.services.review_service import ReviewService
from codereviewer.services.runtime_service import RuntimeProfileService
from codereviewer.services.sso_service import SSOConfig, load_sso_config
from codereviewer.web.landing import LANDING_HTML
from codereviewer.web.ui import INDEX_HTML

app = FastAPI(title="CodeReviewer")
configure_signoz(app)

static_dir = Path(__file__).resolve().parent.parent / "web" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

storage = SQLiteRepository(db_path=os.getenv("CODEREVIEWER_DB_PATH", "./.codereviewer/codereviewer.db"))
job_repo = ReviewJobRepository(storage)
profile_repo = RuntimeProfileRepository(storage)
memory_repo = MemoryRepository(storage)
feedback_repo = ReviewFeedbackRepository(storage)
notification_service = NotificationService()
review_service = ReviewService(
    job_repo,
    profile_repo,
    memory_repo,
    ClaudeAgentSDKReviewer(),
    ContextBudgetManager(),
    notification_service=notification_service,
)
runtime_service = RuntimeProfileService(profile_repo)
feedback_service = FeedbackService(feedback_repo)

@dataclass(frozen=True)
class IdentityContext:
    tenant_id: str
    agent_id: str | None = None


def _clean_identity(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _is_enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def get_identity_context(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    x_agent_id: str | None = Header(default=None, alias="X-Agent-ID"),
) -> IdentityContext:
    tenant_id = _clean_identity(x_tenant_id)
    agent_id = _clean_identity(x_agent_id)

    if _is_enabled(os.getenv("MULTITENANCY_REQUIRE_AGENT_IDENTITY")) and not agent_id:
        raise HTTPException(status_code=401, detail="X-Agent-ID is required")

    if tenant_id:
        return IdentityContext(tenant_id=tenant_id, agent_id=agent_id)
    if agent_id:
        return IdentityContext(tenant_id=f"agent:{agent_id}", agent_id=agent_id)
    return IdentityContext(tenant_id="default", agent_id=None)


@app.get("/", response_class=HTMLResponse)
def landing() -> str:
    return LANDING_HTML


@app.get("/app", response_class=HTMLResponse)
def ui() -> str:
    return INDEX_HTML


@app.get("/api/providers")
def providers() -> list[str]:
    return [p.value for p in Provider]


@app.get("/api/models")
def models(provider: Provider | None = None):
    return runtime_service.list_models(provider)


@app.get("/api/config")
def frontend_config(identity: IdentityContext = Depends(get_identity_context)) -> dict:
    sso = load_sso_config()
    profiles = runtime_service.list_profiles(tenant_id=identity.tenant_id)
    model_catalog = runtime_service.list_models()

    return {
        "identity": {
            "tenant_id": identity.tenant_id,
            "agent_id": identity.agent_id,
        },
        "runtime": {
            "providers": [p.value for p in Provider],
            "models": [model.model_dump(mode="json") for model in model_catalog],
            "profiles": [
                {
                    "id": profile.id,
                    "name": profile.name,
                    "provider": profile.provider.value,
                    "model_id": profile.model_id,
                    "is_default": profile.is_default,
                    "temperature": profile.temperature,
                    "max_tokens": profile.max_tokens,
                }
                for profile in profiles
            ],
        },
        "integrations": {
            "claude_agent_sdk": {
                "enabled": _is_enabled(os.getenv("CLAUDE_AGENT_SDK_ENABLED")),
                "strict": _is_enabled(os.getenv("CLAUDE_AGENT_SDK_STRICT")),
                "default_model": os.getenv("CLAUDE_AGENT_SDK_MODEL", "claude-sonnet-4"),
                "api_key_configured": bool(os.getenv("CLAUDE_API_KEY")),
            },
            "litellm": {
                "enabled": _is_enabled(os.getenv("LITELLM_ENABLED")),
                "base_url": os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
                "model": os.getenv("LITELLM_MODEL", "anthropic/claude-sonnet-4"),
                "api_key_configured": bool(os.getenv("LITELLM_API_KEY")),
            },
            "notifications": {
                "enabled": notification_service.enabled,
                "channels": sorted(notification_service.channels),
                "smtp_configured": bool(notification_service.smtp_host and notification_service.smtp_from and notification_service.smtp_to),
                "smtp_host": notification_service.smtp_host or None,
                "smtp_from_configured": bool(notification_service.smtp_from),
                "smtp_to_count": len(notification_service.smtp_to),
            },
            "observability": {
                "signoz_enabled": _is_enabled(os.getenv("SIGNOZ_ENABLED")),
                "service_name": os.getenv("SIGNOZ_SERVICE_NAME", "code-reviewer"),
                "traces_endpoint": os.getenv("SIGNOZ_OTLP_TRACES_ENDPOINT", "http://localhost:4318/v1/traces"),
            },
            "sso": sso.model_dump(mode="json"),
        },
    }


@app.get("/api/runtime-profiles")
def list_runtime_profiles(identity: IdentityContext = Depends(get_identity_context)) -> list[RuntimeProfile]:
    return runtime_service.list_profiles(tenant_id=identity.tenant_id)


@app.post("/api/runtime-profiles")
def create_runtime_profile(profile: RuntimeProfile, identity: IdentityContext = Depends(get_identity_context)) -> RuntimeProfile:
    try:
        return runtime_service.create_profile(profile, tenant_id=identity.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/reviews")
def submit_review(job: ReviewJob, identity: IdentityContext = Depends(get_identity_context)) -> ReviewJob:
    job.tenant_id = identity.tenant_id
    job.agent_id = identity.agent_id
    return review_service.submit(job)


@app.get("/api/reviews")
def list_reviews(identity: IdentityContext = Depends(get_identity_context)) -> list[ReviewJob]:
    return review_service.list(tenant_id=identity.tenant_id)


@app.get("/api/reviews/{job_id}")
def get_review(job_id: str, identity: IdentityContext = Depends(get_identity_context)) -> ReviewJob:
    job = review_service.get(job_id, tenant_id=identity.tenant_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/memory/{repository_name}")
def list_memory(repository_name: str, memory_type: str | None = None, identity: IdentityContext = Depends(get_identity_context)) -> list[MemoryRecord]:
    return memory_repo.list(repository_name=repository_name, memory_type=memory_type, tenant_id=identity.tenant_id)


@app.post("/api/feedback")
def create_feedback(event: ReviewFeedbackEvent, identity: IdentityContext = Depends(get_identity_context)) -> ReviewFeedbackEvent:
    event.tenant_id = identity.tenant_id
    event.agent_id = identity.agent_id
    return feedback_service.record(event)


@app.get("/api/feedback")
def list_feedback(review_job_id: str | None = None, identity: IdentityContext = Depends(get_identity_context)) -> list[ReviewFeedbackEvent]:
    return feedback_service.list(review_job_id=review_job_id, tenant_id=identity.tenant_id)


@app.post("/api/notifications/test")
def test_notification() -> dict[str, bool]:
    sent = notification_service.send_test_notification()
    return {"sent": sent}


@app.get("/api/sso/config")
def sso_config() -> SSOConfig:
    return load_sso_config()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
