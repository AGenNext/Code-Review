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


class FindingCategory(str, Enum):
    security = "security"
    quality = "quality"
    maintainability = "maintainability"


class ReviewFeedbackType(str, Enum):
    false_positive = "false_positive"
    false_negative = "false_negative"
    accepted = "accepted"
    rejected = "rejected"
    overridden = "overridden"


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
    tenant_id: str = "default"
    name: str
    provider: Provider
    model_id: str
    auth_reference: str
    temperature: float = 0.1
    max_tokens: int = 4096
    is_default: bool = False
    metadata: dict[str, str] = Field(default_factory=dict)


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
    category: FindingCategory = FindingCategory.quality
    subtype: str = "general"
    confidence: float = 0.5
    evidence: str | None = None
    remediation: str | None = None
    provenance: str = "rule:heuristic"
    fingerprint: str | None = None
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
    tenant_id: str = "default"
    agent_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    queued_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: ReviewJobStatus = ReviewJobStatus.queued
    repository: RepositoryContext
    changes: list[FileChangeContext]
    runtime_profile_id: str
    findings: list[Finding] = Field(default_factory=list)
    summary: ReviewSummary | None = None
    error: str | None = None
    retry_count: int = 0


class ReviewFeedbackEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str = "default"
    agent_id: str | None = None
    review_job_id: str
    finding_id: str | None = None
    feedback_type: ReviewFeedbackType
    reason: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str = "default"
    agent_id: str | None = None
    repository_name: str
    memory_type: Literal["review_history", "workspace"]
    key: str
    value: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
