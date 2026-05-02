from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class AGenEnvelope(BaseModel):
    protocol: str = "agen.cp.v1"
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    correlation_id: str | None = None
    tenant_id: str
    agent_id: str | None = None
    sender: str
    receiver: str
    type: str
    intent: str
    subject: dict = Field(default_factory=dict)
    authz: dict = Field(default_factory=dict)
    payload: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
