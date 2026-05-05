"""
Authentication and Rate Limiting Middleware
Enforces bearer token auth and prevents API abuse
"""

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import asyncio
from functools import wraps


# ==================== AUTHENTICATION ====================

security = HTTPBearer()


class BearerTokenAuth:
    """Bearer token authentication."""
    
    def __init__(self, token: str, enabled: bool = True):
        """
        Initialize bearer token auth.
        
        Args:
            token: The valid bearer token
            enabled: Whether auth is enabled
        """
        self.token = token
        self.enabled = enabled
    
    async def __call__(self, request: Request) -> str:
        """
        Authenticate request using bearer token.
        
        Args:
            request: FastAPI request
        
        Returns:
            The authenticated token
        
        Raises:
            HTTPException: If authentication fails
        """
        if not self.enabled:
            return "none"
        
        # Get authorization header
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header. Use: Authorization: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = auth_header.replace("Bearer ", "")
        
        if token != self.token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token


# ==================== RATE LIMITING ====================

class RateLimiter:
    """
    Simple token bucket rate limiter.
    
    Tracks requests per IP address and enforces limits.
    """
    
    def __init__(self, requests: int, period_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            requests: Number of requests allowed
            period_seconds: Time period in seconds
        """
        self.requests = requests
        self.period_seconds = period_seconds
        self.requests_per_ip: Dict[str, list] = defaultdict(list)
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for X-Forwarded-For header (behind proxy)
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Fallback to client IP
        return request.client.host if request.client else "unknown"
    
    async def is_rate_limited(self, request: Request) -> Tuple[bool, Dict[str, str]]:
        """
        Check if request is rate limited.
        
        Args:
            request: FastAPI request
        
        Returns:
            Tuple of (is_limited, headers) where headers contain retry info
        """
        client_ip = self.get_client_ip(request)
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period_seconds)
        
        # Remove old requests outside the period
        self.requests_per_ip[client_ip] = [
            req_time for req_time in self.requests_per_ip[client_ip]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.requests_per_ip[client_ip]) >= self.requests:
            # Calculate retry-after
            oldest = min(self.requests_per_ip[client_ip])
            retry_after = int((oldest + timedelta(seconds=self.period_seconds) - now).total_seconds())
            retry_after = max(retry_after, 1)
            
            return True, {"Retry-After": str(retry_after)}
        
        # Add current request
        self.requests_per_ip[client_ip].append(now)
        return False, {}
    
    async def __call__(self, request: Request) -> None:
        """Rate limit middleware."""
        is_limited, headers = await self.is_rate_limited(request)
        
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.requests} requests per {self.period_seconds} seconds.",
                headers=headers,
            )


# ==================== HELPER FUNCTIONS ====================

def parse_rate_limit(limit_str: str) -> Tuple[int, int]:
    """
    Parse rate limit string.
    
    Examples:
        "100/minute" -> (100, 60)
        "10/second" -> (10, 1)
        "1000/hour" -> (1000, 3600)
    
    Args:
        limit_str: Rate limit string
    
    Returns:
        Tuple of (requests, seconds)
    """
    if not limit_str or "/" not in limit_str:
        raise ValueError(f"Invalid rate limit format: {limit_str}")
    
    requests_str, period_str = limit_str.split("/")
    requests = int(requests_str)
    
    period_map = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }
    
    if period_str not in period_map:
        raise ValueError(f"Invalid period: {period_str}. Use: second, minute, hour, day")
    
    seconds = period_map[period_str]
    
    return requests, seconds


# ==================== MIDDLEWARE SETUP ====================

async def add_security_middleware(app):
    """
    Add security middleware to FastAPI app.
    
    Args:
        app: FastAPI application
    """
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],  # In production, list specific hosts
    )


async def add_rate_limiting_middleware(app, settings):
    """
    Add rate limiting middleware to FastAPI app.
    
    Args:
        app: FastAPI application
        settings: Settings object with rate_limit_* config
    """
    
    # Parse rate limits
    global_requests, global_seconds = parse_rate_limit(settings.rate_limit_global)
    review_requests, review_seconds = parse_rate_limit(settings.rate_limit_review_submit)
    list_requests, list_seconds = parse_rate_limit(settings.rate_limit_list)
    
    # Create limiters
    global_limiter = RateLimiter(global_requests, global_seconds)
    review_limiter = RateLimiter(review_requests, review_seconds)
    list_limiter = RateLimiter(list_requests, list_seconds)
    
    # Store on app for use in routes
    app.state.global_limiter = global_limiter
    app.state.review_limiter = review_limiter
    app.state.list_limiter = list_limiter


# ==================== DEPENDENCY FUNCTIONS ====================

async def verify_api_token(request: Request, settings) -> str:
    """
    Verify API bearer token.
    
    Args:
        request: FastAPI request
        settings: Settings object
    
    Returns:
        The validated token
    
    Raises:
        HTTPException: If token is invalid
    """
    if not settings.api_bearer_auth_enabled:
        return "none"
    
    auth = BearerTokenAuth(settings.api_bearer_token, enabled=True)
    return await auth(request)


async def check_rate_limit(request: Request, limiter: RateLimiter) -> None:
    """
    Check rate limit for request.
    
    Args:
        request: FastAPI request
        limiter: RateLimiter instance
    
    Raises:
        HTTPException: If rate limit exceeded
    """
    await limiter(request)


# ==================== EXAMPLE USAGE ====================

"""
# In your FastAPI app:

from fastapi import FastAPI, Depends, Request
from 01_config import settings
from 03_auth_middleware import (
    verify_api_token,
    check_rate_limit,
    add_security_middleware,
    add_rate_limiting_middleware,
    BearerTokenAuth,
)

app = FastAPI()

# Setup middleware
@app.on_event("startup")
async def startup():
    await add_security_middleware(app)
    await add_rate_limiting_middleware(app, settings)

# Apply to routes
@app.post("/api/reviews")
async def submit_review(
    review: ReviewRequest,
    token: str = Depends(lambda r: verify_api_token(r, settings)),
    _: None = Depends(lambda r: check_rate_limit(r, app.state.review_limiter)),
):
    # Handler code
    pass

@app.get("/api/reviews")
async def list_reviews(
    token: str = Depends(lambda r: verify_api_token(r, settings)),
    _: None = Depends(lambda r: check_rate_limit(r, app.state.list_limiter)),
):
    # Handler code
    pass
"""
