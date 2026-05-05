"""
Audit Logging Service
Provides immutable audit trail for compliance and forensics
"""

from datetime import datetime
from typing import Any, Dict, Optional, List
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum
import json


class AuditAction(str, Enum):
    """Standard audit actions."""
    REVIEW_SUBMITTED = "review_submitted"
    REVIEW_COMPLETED = "review_completed"
    REVIEW_FAILED = "review_failed"
    AGENT_SPAWNED = "agent_spawned"
    PROFILE_CREATED = "profile_created"
    PROFILE_UPDATED = "profile_updated"
    FEEDBACK_SUBMITTED = "feedback_submitted"
    API_AUTH_FAILED = "api_auth_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


class AuditStatus(str, Enum):
    """Audit entry status."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"


@dataclass
class AuditLogEntry:
    """Immutable audit log entry."""
    id: str  # UUID
    timestamp: datetime
    tenant_id: str
    agent_id: Optional[str]
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    created_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class AuditService:
    """
    Service for immutable audit logging.
    
    Features:
    - Insert-only (no updates/deletes)
    - Immutable once created
    - Trace every action with full context
    - Full tenant/agent/user attribution
    """
    
    def __init__(self, db_session=None):
        """Initialize audit service."""
        self.db = db_session
        self.audit_logs: List[AuditLogEntry] = []  # In-memory buffer (would use DB in production)
    
    async def log_action(
        self,
        tenant_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        status: str = "success",
        agent_id: Optional[str] = None,
        user_id: str = "system",
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> AuditLogEntry:
        """
        Log an action immutably.
        
        Args:
            tenant_id: Tenant identifier
            action: Action name (from AuditAction)
            resource_type: Type of resource (Review, Profile, etc.)
            resource_id: ID of the resource
            status: Success/failure/error
            agent_id: Optional agent identifier
            user_id: User who performed action (from SSO)
            details: Additional context (before/after values)
            error_message: Error message if failed
        
        Returns:
            AuditLogEntry: The created audit log entry
        """
        entry = AuditLogEntry(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
            error_message=error_message,
            created_at=datetime.utcnow(),
        )
        
        # In production, would save to database (insert-only)
        self.audit_logs.append(entry)
        
        # Log to stdout for traceability
        print(f"[AUDIT] {entry.to_json()}")
        
        return entry
    
    async def get_audit_trail(
        self,
        tenant_id: str,
        resource_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """
        Retrieve immutable audit trail.
        
        Args:
            tenant_id: Tenant to filter by (required - tenant isolation)
            resource_id: Optional resource ID filter
            agent_id: Optional agent ID filter
            limit: Max results to return
        
        Returns:
            List of audit log entries
        """
        results = self.audit_logs
        
        # Filter by tenant (REQUIRED - tenant isolation)
        results = [log for log in results if log.tenant_id == tenant_id]
        
        # Optional filters
        if resource_id:
            results = [log for log in results if log.resource_id == resource_id]
        if agent_id:
            results = [log for log in results if log.agent_id == agent_id]
        
        # Sort by timestamp descending (newest first)
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        return results[:limit]
    
    async def get_action_history(
        self,
        tenant_id: str,
        action: str,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """Get history of specific action type."""
        results = [
            log for log in self.audit_logs
            if log.tenant_id == tenant_id and log.action == action
        ]
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    async def get_user_actions(
        self,
        tenant_id: str,
        user_id: str,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """Get all actions by a specific user."""
        results = [
            log for log in self.audit_logs
            if log.tenant_id == tenant_id and log.user_id == user_id
        ]
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    async def get_failed_actions(
        self,
        tenant_id: str,
        limit: int = 100,
    ) -> List[AuditLogEntry]:
        """Get all failed/error actions for troubleshooting."""
        results = [
            log for log in self.audit_logs
            if log.tenant_id == tenant_id and log.status in ("failure", "error")
        ]
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    def get_stats(self, tenant_id: str) -> dict:
        """Get audit statistics for a tenant."""
        tenant_logs = [log for log in self.audit_logs if log.tenant_id == tenant_id]
        
        return {
            "total_events": len(tenant_logs),
            "by_action": self._count_by(tenant_logs, "action"),
            "by_status": self._count_by(tenant_logs, "status"),
            "by_user": self._count_by(tenant_logs, "user_id"),
            "by_agent": self._count_by(tenant_logs, "agent_id"),
        }
    
    @staticmethod
    def _count_by(logs: List[AuditLogEntry], field: str) -> dict:
        """Count occurrences by field value."""
        counts = {}
        for log in logs:
            value = getattr(log, field)
            counts[value] = counts.get(value, 0) + 1
        return counts


# Example: Using the audit service
async def example_audit_usage():
    """Example of how to use the audit service."""
    audit = AuditService()
    
    # Log a successful action
    await audit.log_action(
        tenant_id="acme",
        agent_id="agent-001",
        user_id="user-123",
        action=AuditAction.REVIEW_SUBMITTED,
        resource_type="Review",
        resource_id="rev-456",
        details={
            "language": "python",
            "diff_size": 2048,
            "provider": "anthropic",
        },
        status=AuditStatus.SUCCESS,
    )
    
    # Log a failed action
    await audit.log_action(
        tenant_id="acme",
        agent_id="agent-001",
        user_id="user-123",
        action=AuditAction.REVIEW_COMPLETED,
        resource_type="Review",
        resource_id="rev-456",
        status=AuditStatus.ERROR,
        error_message="Claude API rate limit exceeded",
    )
    
    # Get audit trail for a resource
    trail = await audit.get_audit_trail(
        tenant_id="acme",
        resource_id="rev-456",
    )
    
    # Get failed actions
    failed = await audit.get_failed_actions(tenant_id="acme")
    
    # Get stats
    stats = audit.get_stats(tenant_id="acme")
    print(f"Audit stats: {stats}")
