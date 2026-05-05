"""
AGenNext CodeReview - Production Configuration
Fixed: Authentication mandatory, validation enforced
"""

from pydantic import BaseSettings, Field, validator
from typing import Optional


class Settings(BaseSettings):
    """Production-hardened settings with security by default."""
    
    # ==================== CORE SETTINGS ====================
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    pythonpath: str = Field(default="/app/src", description="Python path")
    
    # ==================== DATABASE ====================
    codereviewer_db_path: str = Field(
        default="sqlite:///codereviewer.db",
        description="Database URL (use PostgreSQL for production: postgresql://user:pass@host/db)"
    )
    
    @validator('codereviewer_db_path')
    def validate_database_url(cls, v):
        """Warn if using SQLite in production."""
        if v.startswith("sqlite"):
            print("⚠️  WARNING: SQLite detected. Use PostgreSQL for production.")
        if not v:
            raise ValueError("CODEREVIEWER_DB_PATH is required")
        return v
    
    # ==================== AUTHENTICATION (MANDATORY) ====================
    api_bearer_auth_enabled: bool = Field(
        default=True,  # ✅ FIXED: Changed from False to True
        description="Enable bearer token authentication (MANDATORY for production)"
    )
    
    api_bearer_token: Optional[str] = Field(
        default=None,
        description="Bearer token for API authentication (required when enabled)"
    )
    
    @validator('api_bearer_token')
    def validate_bearer_token(cls, v, values):
        """Validate bearer token when auth is enabled."""
        auth_enabled = values.get('api_bearer_auth_enabled', True)
        
        if auth_enabled:
            if not v:
                raise ValueError(
                    "API_BEARER_TOKEN is required when API_BEARER_AUTH_ENABLED=true\n"
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            if len(v) < 32:
                raise ValueError("API_BEARER_TOKEN must be at least 32 characters")
        
        return v
    
    # ==================== SECURITY HARDENING ====================
    security_hardening_enabled: bool = Field(
        default=True,
        description="Enable hardened security response headers"
    )
    
    security_headers: str = Field(
        default="all",
        description="Security headers to enable: all, minimal, none"
    )
    
    # ==================== RATE LIMITING ====================
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable API rate limiting"
    )
    
    rate_limit_global: str = Field(
        default="100/minute",
        description="Global rate limit (e.g., '100/minute')"
    )
    
    rate_limit_review_submit: str = Field(
        default="10/minute",
        description="Rate limit for expensive review submission endpoint"
    )
    
    rate_limit_list: str = Field(
        default="30/minute",
        description="Rate limit for list endpoints"
    )
    
    # ==================== AUDIT LOGGING ====================
    audit_logging_enabled: bool = Field(
        default=True,
        description="Enable immutable audit logging"
    )
    
    audit_log_table: str = Field(
        default="audit_logs",
        description="Table name for audit logs"
    )
    
    # ==================== SSO / AUTHENTICATION ====================
    sso_enabled: bool = Field(
        default=False,  # Optional, but recommended
        description="Enable SSO integration"
    )
    
    sso_provider: Optional[str] = Field(
        default=None,
        description="SSO provider (okta, auth0, keycloak, etc.)"
    )
    
    sso_issuer_url: Optional[str] = Field(
        default=None,
        description="SSO issuer URL"
    )
    
    sso_client_id: Optional[str] = Field(
        default=None,
        description="SSO client ID"
    )
    
    sso_client_secret: Optional[str] = Field(
        default=None,
        description="SSO client secret (from secret manager)"
    )
    
    sso_audience: Optional[str] = Field(
        default=None,
        description="SSO audience"
    )
    
    sso_redirect_uri: Optional[str] = Field(
        default=None,
        description="SSO redirect URI"
    )
    
    sso_scopes: Optional[str] = Field(
        default="openid profile email",
        description="SSO scopes"
    )
    
    # ==================== MULTITENANCY ====================
    multitenancy_require_agent_identity: bool = Field(
        default=True,
        description="Require X-Agent-ID header on all requests"
    )
    
    # ==================== LLM PROVIDERS ====================
    claude_agent_sdk_enabled: bool = Field(
        default=True,
        description="Enable Claude Agent SDK"
    )
    
    claude_agent_sdk_strict: bool = Field(
        default=True,
        description="Fail on SDK errors instead of fallback"
    )
    
    claude_agent_sdk_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Default Claude model"
    )
    
    claude_agent_sdk_max_tokens: int = Field(
        default=4096,
        description="Max tokens for Claude SDK"
    )
    
    claude_agent_sdk_temperature: float = Field(
        default=0.1,
        description="Temperature for Claude SDK"
    )
    
    claude_api_key: Optional[str] = Field(
        default=None,
        description="Claude API key (from secret manager)"
    )
    
    # LiteLLM
    litellm_enabled: bool = Field(
        default=False,
        description="Enable LiteLLM provider routing"
    )
    
    litellm_base_url: Optional[str] = Field(
        default=None,
        description="LiteLLM gateway URL"
    )
    
    litellm_api_key: Optional[str] = Field(
        default=None,
        description="LiteLLM API key"
    )
    
    litellm_model: Optional[str] = Field(
        default=None,
        description="Default LiteLLM model"
    )
    
    litellm_provider_prefix_map: Optional[str] = Field(
        default='{"bedrock":"bedrock/","anthropic":"anthropic/","vertex":"vertex_ai/","foundry":"azure/"}',
        description="Provider prefix mapping (JSON)"
    )
    
    # ==================== OBSERVABILITY ====================
    signoz_enabled: bool = Field(
        default=False,
        description="Enable SignalOz observability"
    )
    
    signoz_service_name: str = Field(
        default="agentnxt-code-reviewer",
        description="Service name for SignalOz"
    )
    
    signoz_otlp_traces_endpoint: Optional[str] = Field(
        default=None,
        description="SignalOz OTLP traces endpoint"
    )
    
    # ==================== NOTIFICATIONS ====================
    notifications_enabled: bool = Field(
        default=False,
        description="Enable notifications"
    )
    
    notification_channels: str = Field(
        default="email,slack",
        description="Notification channels"
    )
    
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_from: Optional[str] = Field(default=None, description="SMTP from address")
    smtp_to: Optional[str] = Field(default=None, description="SMTP to address")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    smtp_use_ssl: bool = Field(default=False, description="Use SSL for SMTP")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Log security configuration
        print("=" * 60)
        print("AGenNext CodeReview - Security Configuration")
        print("=" * 60)
        print(f"✅ Authentication Enabled: {self.api_bearer_auth_enabled}")
        print(f"✅ Security Hardening: {self.security_hardening_enabled}")
        print(f"✅ Rate Limiting: {self.rate_limit_enabled}")
        print(f"✅ Audit Logging: {self.audit_logging_enabled}")
        print(f"✅ SSO Enabled: {self.sso_enabled}")
        print(f"✅ Agent Identity Required: {self.multitenancy_require_agent_identity}")
        print("=" * 60)
    
    def get_security_headers(self) -> dict:
        """Get security headers based on configuration."""
        headers = {}
        
        if not self.security_hardening_enabled:
            return headers
        
        if self.security_headers in ("all", "minimal"):
            headers.update({
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            })
        
        if self.security_headers == "all":
            headers.update({
                "Content-Security-Policy": "default-src 'self'",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            })
        
        return headers


# Global settings instance
settings = Settings()
