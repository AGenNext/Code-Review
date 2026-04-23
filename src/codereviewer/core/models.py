from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class RecommendationType(str, Enum):
    must_fix = "must_fix"
    should_fix = "should_fix"
    consider = "consider"


class Provider(str, Enum):
    anthropic = "anthropic"
    bedrock = "bedrock"
    vertex = "vertex"
    foundry = "foundry"


class ModelConfiguration(BaseModel):
    model_id: str
    display_name: str
    provider: Provider
    context_window: int | None = None
    enabled: bool = True


class ProviderConfiguration(BaseModel):
    provider: Provider
    auth_strategy: Literal["api_key", "aws_iam", "gcp_service_account", "azure_entra"]
    endpoint: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class RuntimeProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    provider: Provider
    model_id: str
    auth_reference: str
    temperature: float = 0.1
    max_tokens: int = 4096
    is_default: bool = False


class RepositoryContext(BaseModel):
    name: str
    url: str | None = None
    branch: str = "main"
    commit_sha: str | None = None


class FileChangeContext(BaseModel):
    path: str
    change_type: Literal["added", "modified", "deleted", "renamed"]
    patch: str


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    severity: Severity
    recommendation: RecommendationType
    file_path: str
    line_start: int | None = None
    line_end: int | None = None


class ReviewSummary(BaseModel):
    total_findings: int
    by_severity: dict[Severity, int]
    risk_score: int


class ReviewJobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class ReviewJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ReviewJobStatus = ReviewJobStatus.queued
    repository: RepositoryContext
    changes: list[FileChangeContext]
    runtime_profile_id: str
    findings: list[Finding] = Field(default_factory=list)
    summary: ReviewSummary | None = None
    error: str | None = None
