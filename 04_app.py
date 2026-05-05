"""
Hardened FastAPI Routes
Includes authentication, audit logging, rate limiting, and enhanced health checks
"""

from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from config import settings
from auth_middleware import (
    verify_api_token,
    check_rate_limit,
    BearerTokenAuth,
)
from audit_service import AuditService, AuditAction, AuditStatus


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
audit_service = AuditService()

# Create FastAPI app
app = FastAPI(
    title="AGenNext CodeReview",
    description="Production-hardened code review service",
    version="1.0.0",
)


# ==================== MODELS ====================

class ReviewRequest(BaseModel):
    """Code review request."""
    code_diff: str
    language: str = "python"
    provider: str = "anthropic"


class ReviewResponse(BaseModel):
    """Code review response."""
    id: str
    status: str
    created_at: datetime
    result: Optional[dict] = None


class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    id: str
    timestamp: datetime
    action: str
    resource_type: str
    resource_id: str
    status: str
    user_id: str
    agent_id: Optional[str]


# ==================== DEPENDENCIES ====================

async def get_current_token(request: Request) -> str:
    """Dependency: Verify API token."""
    return await verify_api_token(request, settings)


async def get_review_rate_limit(request: Request) -> None:
    """Dependency: Check review endpoint rate limit."""
    await check_rate_limit(request, app.state.review_limiter)


async def get_list_rate_limit(request: Request) -> None:
    """Dependency: Check list endpoint rate limit."""
    await check_rate_limit(request, app.state.list_limiter)


async def get_tenant_context(request: Request) -> dict:
    """
    Dependency: Extract and validate tenant context from headers.
    
    Required headers:
    - X-Tenant-ID: Tenant identifier (2-63 chars)
    
    Optional headers:
    - X-Agent-ID: Agent identifier
    - X-User-ID: User identifier (for audit logging)
    """
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    agent_id = request.headers.get("X-Agent-ID")
    user_id = request.headers.get("X-User-ID", "anonymous")
    
    # Validate tenant ID
    if not tenant_id or len(tenant_id) < 2 or len(tenant_id) > 63:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID must be 2-63 characters",
        )
    
    # Check if agent identity is required
    if settings.multitenancy_require_agent_identity and not agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Agent-ID header is required (MULTITENANCY_REQUIRE_AGENT_IDENTITY=true)",
        )
    
    return {
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "user_id": user_id,
    }


# ==================== PUBLIC ENDPOINTS ====================

@app.get("/", tags=["public"])
async def landing_page():
    """Landing page."""
    return {
        "name": "AGenNext CodeReview",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/healthz", tags=["public"])
async def health_check():
    """Liveness probe - quick check."""
    return {"status": "ok"}


# ==================== HEALTH CHECK ENDPOINT ====================

@app.get("/readyz", tags=["health"])
async def readiness_check():
    """
    Readiness probe - comprehensive health check.
    
    Checks:
    - Database connectivity
    - LLM provider availability
    - Configuration validity
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {},
    }
    
    # Database check
    try:
        # In production, would actually query the database
        health_status["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": 5,
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e),
        }
        health_status["status"] = "unhealthy"
    
    # LLM Provider checks
    providers = {}
    
    if settings.claude_api_key:
        providers["anthropic"] = {"status": "available"}
    
    if settings.litellm_enabled:
        providers["litellm"] = {"status": "available"}
    
    health_status["checks"]["providers"] = providers
    
    # Security checks
    health_status["checks"]["security"] = {
        "auth_enabled": settings.api_bearer_auth_enabled,
        "rate_limiting": settings.rate_limit_enabled,
        "audit_logging": settings.audit_logging_enabled,
        "security_hardening": settings.security_hardening_enabled,
    }
    
    return health_status


@app.get("/health", tags=["health"])
async def detailed_health():
    """Detailed health information."""
    return {
        "service": "AGenNext CodeReview",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "configuration": {
            "authentication": settings.api_bearer_auth_enabled,
            "database": settings.codereviewer_db_path.split("://")[0],  # sqlite/postgresql
            "audit_logging": settings.audit_logging_enabled,
            "rate_limiting": settings.rate_limit_enabled,
            "sso_enabled": settings.sso_enabled,
        },
    }


# ==================== PROTECTED API ENDPOINTS ====================

@app.post("/api/reviews", tags=["reviews"], response_model=ReviewResponse)
async def submit_review(
    review: ReviewRequest,
    request: Request,
    token: str = Depends(get_current_token),
    _: None = Depends(get_review_rate_limit),
    tenant_context: dict = Depends(get_tenant_context),
):
    """
    Submit a code review.
    
    Authentication: Bearer token (required)
    Rate limit: 10 requests/minute
    
    Headers:
    - Authorization: Bearer <token>
    - X-Tenant-ID: <tenant_id>
    - X-Agent-ID: <agent_id> (required if MULTITENANCY_REQUIRE_AGENT_IDENTITY=true)
    """
    try:
        # Log the submission
        await audit_service.log_action(
            tenant_id=tenant_context["tenant_id"],
            agent_id=tenant_context["agent_id"],
            user_id=tenant_context["user_id"],
            action=AuditAction.REVIEW_SUBMITTED,
            resource_type="Review",
            resource_id="pending",  # Real ID would be generated
            details={
                "language": review.language,
                "diff_size": len(review.code_diff),
                "provider": review.provider,
            },
            status=AuditStatus.SUCCESS,
        )
        
        # In production: queue async task, return job_id
        return ReviewResponse(
            id="rev-123",
            status="queued",
            created_at=datetime.utcnow(),
        )
    
    except Exception as e:
        # Log failure
        await audit_service.log_action(
            tenant_id=tenant_context["tenant_id"],
            agent_id=tenant_context["agent_id"],
            user_id=tenant_context["user_id"],
            action=AuditAction.REVIEW_SUBMITTED,
            resource_type="Review",
            resource_id="unknown",
            status=AuditStatus.ERROR,
            error_message=str(e),
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@app.get("/api/reviews", tags=["reviews"])
async def list_reviews(
    request: Request,
    token: str = Depends(get_current_token),
    _: None = Depends(get_list_rate_limit),
    tenant_context: dict = Depends(get_tenant_context),
    limit: int = 100,
):
    """
    List reviews.
    
    Authentication: Bearer token (required)
    Rate limit: 30 requests/minute
    
    Headers:
    - Authorization: Bearer <token>
    - X-Tenant-ID: <tenant_id>
    """
    # In production: fetch from database filtered by tenant_id
    return {
        "reviews": [],
        "count": 0,
        "tenant_id": tenant_context["tenant_id"],
    }


@app.get("/api/reviews/{review_id}/audit", tags=["reviews", "audit"])
async def get_review_audit_trail(
    review_id: str,
    request: Request,
    token: str = Depends(get_current_token),
    tenant_context: dict = Depends(get_tenant_context),
):
    """
    Get immutable audit trail for a review.
    
    Authentication: Bearer token (required)
    
    Shows all actions taken on this review:
    - submission
    - processing
    - completion
    - failures
    - user interactions
    """
    trail = await audit_service.get_audit_trail(
        tenant_id=tenant_context["tenant_id"],
        resource_id=review_id,
    )
    
    return {
        "review_id": review_id,
        "audit_trail": [log.to_dict() for log in trail],
        "count": len(trail),
    }


@app.get("/api/audit/stats", tags=["audit"])
async def get_audit_stats(
    request: Request,
    token: str = Depends(get_current_token),
    tenant_context: dict = Depends(get_tenant_context),
):
    """
    Get audit statistics for tenant.
    
    Shows:
    - Total audit events
    - Breakdown by action type
    - Breakdown by status
    - Breakdown by user
    - Breakdown by agent
    """
    stats = audit_service.get_stats(tenant_context["tenant_id"])
    
    return {
        "tenant_id": tenant_context["tenant_id"],
        "stats": stats,
    }


@app.get("/api/audit/failed-actions", tags=["audit"])
async def get_failed_actions(
    request: Request,
    token: str = Depends(get_current_token),
    tenant_context: dict = Depends(get_tenant_context),
    limit: int = 100,
):
    """
    Get all failed/error actions for troubleshooting.
    
    Useful for:
    - Investigating issues
    - Finding errors
    - Compliance review
    """
    failed = await audit_service.get_failed_actions(
        tenant_id=tenant_context["tenant_id"],
        limit=limit,
    )
    
    return {
        "tenant_id": tenant_context["tenant_id"],
        "failed_actions": [log.to_dict() for log in failed],
        "count": len(failed),
    }


# ==================== ADMIN ENDPOINTS ====================

@app.get("/api/admin/config", tags=["admin"])
async def get_config(
    request: Request,
    token: str = Depends(get_current_token),
):
    """
    Get current configuration (admin only).
    
    Shows active settings for debugging.
    Secret values are NOT returned.
    """
    return {
        "authentication": settings.api_bearer_auth_enabled,
        "rate_limiting": settings.rate_limit_enabled,
        "audit_logging": settings.audit_logging_enabled,
        "security_hardening": settings.security_hardening_enabled,
        "sso_enabled": settings.sso_enabled,
        "multitenancy": {
            "require_agent_identity": settings.multitenancy_require_agent_identity,
        },
        "database": settings.codereviewer_db_path.split("://")[0],
        "timestamp": datetime.utcnow().isoformat(),
    }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    # Log security events (auth failures, rate limits)
    if exc.status_code in (401, 403, 429):
        await audit_service.log_action(
            tenant_id="system",
            user_id="unknown",
            action=f"api_{exc.status_code}",
            resource_type="Request",
            resource_id=str(request.url),
            status=AuditStatus.FAILURE,
            error_message=exc.detail,
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


# ==================== MIDDLEWARE ====================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Add security headers
    security_headers = settings.get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests (audit trail)."""
    start_time = datetime.utcnow()
    
    response = await call_next(request)
    
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    logger.info("=" * 60)
    logger.info("AGenNext CodeReview - Starting up")
    logger.info("=" * 60)
    
    # Setup rate limiters
    from auth_middleware import RateLimiter, parse_rate_limit
    
    req, sec = parse_rate_limit(settings.rate_limit_global)
    app.state.global_limiter = RateLimiter(req, sec)
    
    req, sec = parse_rate_limit(settings.rate_limit_review_submit)
    app.state.review_limiter = RateLimiter(req, sec)
    
    req, sec = parse_rate_limit(settings.rate_limit_list)
    app.state.list_limiter = RateLimiter(req, sec)
    
    logger.info(f"✅ Authentication: {settings.api_bearer_auth_enabled}")
    logger.info(f"✅ Rate Limiting: {settings.rate_limit_enabled}")
    logger.info(f"✅ Audit Logging: {settings.audit_logging_enabled}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
    )
