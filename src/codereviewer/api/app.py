import os
import re
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from codereviewer.core.models import MemoryRecord, Provider, ReviewFeedbackEvent, ReviewJob, RuntimeProfile
from codereviewer.infra.repositories import (
    MemoryRepository,
    ReviewFeedbackRepository,
    ReviewJobRepository,
    RuntimeProfileRepository,
    SQLiteRepository,
)
from codereviewer.adapters.runtime.claude_agent_sdk import ClaudeAgentSDKReviewRuntime
from codereviewer.adapters.runner.client import RunnerReviewRuntime
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
TENANT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.:-]{1,62}$")

static_dir = Path(__file__).resolve().parent.parent / "web" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

storage = SQLiteRepository(db_path=os.getenv("CODEREVIEWER_DB_PATH", "./.codereviewer/codereviewer.db"))
job_repo = ReviewJobRepository(storage)
profile_repo = RuntimeProfileRepository(storage)
memory_repo = MemoryRepository(storage)
feedback_repo = ReviewFeedbackRepository(storage)
notification_service = NotificationService()
runtime_adapter = RunnerReviewRuntime() if os.getenv("AGENNEXT_RUNNER_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"} else ClaudeAgentSDKReviewRuntime()
review_service = ReviewService(
    job_repo,
    profile_repo,
    memory_repo,
    runtime_adapter,
    ContextBudgetManager(),
    notification_service=notification_service,
)
runtime_service = RuntimeProfileService(profile_repo)
feedback_service = FeedbackService(feedback_repo)


AGENT_ROSTER = [
    "code-reviewer",
    "code-assist",
    "code-tester",
    "code-deploy",
    "technical-writer",
    "product-designer",
    "design-agent",
]


class AgentChatRequest(BaseModel):
    agent_name: str
    message: str


class AgentChatResponse(BaseModel):
    agent_name: str
    response: str


class AgentState(BaseModel):
    agent_name: str
    active: bool
    last_seen: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _agent_idle_timeout_seconds() -> int:
    return int(os.getenv("AGENT_MAX_IDLE_SECONDS", "1800"))


AGENT_RUNTIME_STATE: dict[str, AgentState] = {
    name: AgentState(agent_name=name, active=True, last_seen=_now_iso())
    for name in AGENT_ROSTER
}


def _refresh_agent_states() -> None:
    now = datetime.now(timezone.utc)
    timeout = _agent_idle_timeout_seconds()
    for state in AGENT_RUNTIME_STATE.values():
        if not state.active:
            continue
        try:
            last = datetime.fromisoformat(state.last_seen)
        except ValueError:
            state.active = False
            continue
        idle = (now - last).total_seconds()
        if idle > timeout:
            state.active = False


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


def _security_enabled() -> bool:
    return _is_enabled(os.getenv("SECURITY_HARDENING_ENABLED", "true"))


def _bearer_auth_enabled() -> bool:
    return _is_enabled(os.getenv("API_BEARER_AUTH_ENABLED", "false"))


def _is_valid_tenant_id(value: str) -> bool:
    return bool(TENANT_ID_PATTERN.match(value))


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if _bearer_auth_enabled() and request.url.path.startswith("/api/"):
        auth = request.headers.get("authorization", "")
        token = auth.removeprefix("Bearer ").strip() if auth.startswith("Bearer ") else ""
        expected = os.getenv("API_BEARER_TOKEN", "").strip()
        if not token or not expected or token != expected:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    response = await call_next(request)
    if _security_enabled():
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store"
    return response


def get_identity_context(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    x_agent_id: str | None = Header(default=None, alias="X-Agent-ID"),
) -> IdentityContext:
    tenant_id = _clean_identity(x_tenant_id)
    agent_id = _clean_identity(x_agent_id)

    if _is_enabled(os.getenv("MULTITENANCY_REQUIRE_AGENT_IDENTITY")) and not agent_id:
        raise HTTPException(status_code=401, detail="X-Agent-ID is required")

    if tenant_id:
        if not _is_valid_tenant_id(tenant_id):
            raise HTTPException(status_code=400, detail="X-Tenant-ID must be 2-63 chars and use [a-zA-Z0-9_.:-]")
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
            "agent_runtime": {
                "max_idle_seconds": _agent_idle_timeout_seconds(),
            },
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

@app.post("/api/agents/spawn-all")
def spawn_all_agents() -> dict[str, list[str]]:
    _refresh_agent_states()
    return {"agents": [name for name, st in AGENT_RUNTIME_STATE.items() if st.active]}


@app.get("/api/agents")
def list_agents() -> list[str]:
    _refresh_agent_states()
    return [name for name, st in AGENT_RUNTIME_STATE.items() if st.active]


@app.get("/api/agents/state")
def list_agent_states() -> dict[str, object]:
    _refresh_agent_states()
    return {
        "max_idle_seconds": _agent_idle_timeout_seconds(),
        "agents": [st.model_dump(mode="json") for st in AGENT_RUNTIME_STATE.values()],
    }


@app.post("/api/agents/enable/{agent_name}")
def enable_agent(agent_name: str) -> AgentState:
    if agent_name not in AGENT_RUNTIME_STATE:
        raise HTTPException(status_code=404, detail="Unknown agent")
    st = AGENT_RUNTIME_STATE[agent_name]
    st.active = True
    st.last_seen = _now_iso()
    return st


@app.post("/api/agents/chat", response_model=AgentChatResponse)
def agent_chat(payload: AgentChatRequest) -> AgentChatResponse:
    _refresh_agent_states()
    agent_name = payload.agent_name.strip()
    if agent_name not in AGENT_RUNTIME_STATE:
        raise HTTPException(status_code=400, detail="Unknown agent")
    st = AGENT_RUNTIME_STATE[agent_name]
    if not st.active:
        raise HTTPException(status_code=409, detail="Agent disabled due to idle timeout")
    st.last_seen = _now_iso()
    message = payload.message.strip()
    return AgentChatResponse(
        agent_name=agent_name,
        response=f"{agent_name}: received '{message}'. Task accepted.",
    )

@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
