from __future__ import annotations

import os

from pydantic import BaseModel


def _is_enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


class SSOConfig(BaseModel):
    enabled: bool
    provider: str
    issuer_url: str | None = None
    client_id: str | None = None
    client_secret_configured: bool = False
    audience: str | None = None
    redirect_uri: str | None = None
    scopes: list[str]


def load_sso_config() -> SSOConfig:
    scopes = [scope.strip() for scope in os.getenv("SSO_SCOPES", "openid,profile,email").split(",") if scope.strip()]
    return SSOConfig(
        enabled=_is_enabled(os.getenv("SSO_ENABLED")),
        provider=os.getenv("SSO_PROVIDER", "oidc"),
        issuer_url=os.getenv("SSO_ISSUER_URL"),
        client_id=os.getenv("SSO_CLIENT_ID"),
        client_secret_configured=bool(os.getenv("SSO_CLIENT_SECRET")),
        audience=os.getenv("SSO_AUDIENCE"),
        redirect_uri=os.getenv("SSO_REDIRECT_URI"),
        scopes=scopes,
    )
