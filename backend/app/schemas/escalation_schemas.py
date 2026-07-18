"""Request and response schemas for escalation endpoints."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class EscalationStatusEnum(str, Enum):
    """Escalation status."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class EscalationLevelEnum(str, Enum):
    """Escalation levels."""

    LEVEL_1 = "level_1"  # Ward supervisor
    LEVEL_2 = "level_2"  # Department head
    LEVEL_3 = "level_3"  # Commissioner


class EscalationItemSchema(BaseModel):
    """Individual escalation item."""

    escalation_id: str = Field(..., description="Escalation record ID")
    complaint_id: str = Field(..., description="Associated complaint ID")
    escalation_level: EscalationLevelEnum = Field(
        ..., description="Current escalation level"
    )
    escalated_from_official_id: str = Field(
        ..., description="Official who escalated"
    )
    escalated_to_official_id: str = Field(
        ..., description="Official receiving escalation"
    )
    escalation_reason: str = Field(
        ..., description="Reason for escalation", min_length=10, max_length=500
    )
    status: EscalationStatusEnum = Field(..., description="Escalation status")
    escalated_at: datetime = Field(..., description="When escalation occurred")
    target_resolution_date: datetime = Field(
        ..., description="Target resolution date"
    )
    summary: Optional[str] = Field(None, description="Escalation summary")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "escalation_id": "ESC_001",
                "complaint_id": "COMP_123",
                "escalation_level": "level_1",
                "escalated_from_official_id": "OFF_001",
                "escalated_to_official_id": "OFF_002",
                "escalation_reason": "Complaint not resolved within SLA",
                "status": "assigned",
                "escalated_at": "2024-01-15T10:30:00Z",
                "target_resolution_date": "2024-01-20T10:30:00Z",
            }
        }


class EscalationQueueItemSchema(BaseModel):
    """Item in escalation queue."""

    queue_position: int = Field(..., description="Position in queue", ge=1)
    escalation_record: EscalationItemSchema = Field(
        ..., description="Escalation details"
    )
    days_overdue: int = Field(..., description="Days overdue", ge=0)
    risk_score: float = Field(
        ..., description="Risk/urgency score (0-100)", ge=0, le=100
    )
    auto_escalate_in_hours: Optional[int] = Field(
        None, description="Hours until auto-escalation"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "queue_position": 1,
                "escalation_record": {},
                "days_overdue": 3,
                "risk_score": 85.5,
                "auto_escalate_in_hours": 12,
            }
        }


class EscalationQueueResponse(BaseModel):
    """Response with escalation queue data."""

    total_pending: int = Field(
        ..., description="Total pending escalations", ge=0
    )
    total_in_review: int = Field(
        ..., description="Total in review", ge=0
    )
    high_priority_count: int = Field(
        ..., description="Count of high priority escalations", ge=0
    )
    queue_items: List[EscalationQueueItemSchema] = Field(
        default_factory=list, description="Escalation queue items"
    )
    oldest_escalation_days: Optional[int] = Field(
        None, description="Days since oldest escalation", ge=0
    )
    average_resolution_time_days: Optional[float] = Field(
        None, description="Average resolution time", ge=0
    )
    generated_at: datetime = Field(
        ..., description="When this queue snapshot was generated"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_pending": 15,
                "total_in_review": 8,
                "high_priority_count": 3,
                "queue_items": [],
                "oldest_escalation_days": 12,
                "average_resolution_time_days": 4.5,
                "generated_at": "2024-01-15T10:30:00Z",
            }
        }


class EscalationRequestSchema(BaseModel):
    """Request to escalate a complaint."""

    complaint_id: str = Field(..., description="Complaint ID to escalate")
    escalation_reason: str = Field(
        ..., description="Reason for escalation", min_length=10, max_length=500
    )
    escalated_by_official_id: str = Field(
        ..., description="Official escalating the complaint"
    )
    next_escalation_level: Optional[EscalationLevelEnum] = Field(
        None, description="Target escalation level"
    )
    target_resolution_date: Optional[datetime] = Field(
        None, description="New target resolution date"
    )
    notes: Optional[str] = Field(
        None, description="Additional context", max_length=1000
    )

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "complaint_id": "COMP_123",
                "escalation_reason": "Complaint not resolved within agreed SLA period",
                "escalated_by_official_id": "OFF_001",
                "next_escalation_level": "level_1",
                "target_resolution_date": "2024-01-20T10:30:00Z",
                "notes": "Customer dissatisfaction rising",
            }
        }


class EscalationResponseSchema(BaseModel):
    """Response after escalating a complaint."""

    escalation_id: str = Field(..., description="New escalation record ID")
    complaint_id: str = Field(..., description="Complaint ID")
    escalation_level: str = Field(..., description="Current escalation level")
    status: str = Field(..., description="Escalation status")
    assigned_to_official_id: str = Field(
        ..., description="Official assigned to handle"
    )
    target_resolution_date: datetime = Field(
        ..., description="New target resolution date"
    )
    message: str = Field(..., description="Response message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "escalation_id": "ESC_001",
                "complaint_id": "COMP_123",
                "escalation_level": "level_1",
                "status": "assigned",
                "assigned_to_official_id": "OFF_002",
                "target_resolution_date": "2024-01-20T10:30:00Z",
                "message": "Complaint escalated to Ward Supervisor",
            }
        }


class AutoEscalationEventSchema(BaseModel):
    """Automatic escalation event triggered by system."""

    event_id: str = Field(..., description="Event identifier")
    complaint_id: str = Field(..., description="Complaint ID")
    escalation_trigger: str = Field(
        ..., description="Trigger reason (e.g., sla_exceeded, no_progress)"
    )
    trigger_timestamp: datetime = Field(..., description="When trigger fired")
    escalation_result: Dict[str, Any] = Field(
        ..., description="Result of auto-escalation"
    )
    notification_sent_to: List[str] = Field(
        default_factory=list, description="Officials notified"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "event_id": "AEV_001",
                "complaint_id": "COMP_123",
                "escalation_trigger": "sla_exceeded",
                "trigger_timestamp": "2024-01-15T10:30:00Z",
                "escalation_result": {
                    "new_escalation_id": "ESC_001",
                    "new_level": "level_1",
                },
                "notification_sent_to": ["OFF_002", "OFF_003"],
            }
        }


class EscalationMetricsSchema(BaseModel):
    """Metrics for escalation system."""

    total_escalations: int = Field(..., description="Total escalations", ge=0)
    escalations_per_level: Dict[str, int] = Field(
        ..., description="Count by escalation level"
    )
    average_escalation_time_days: float = Field(
        ..., description="Average time to escalate", ge=0
    )
    resolution_rate_percentage: float = Field(
        ..., description="Percentage of escalations resolved", ge=0, le=100
    )
    average_resolution_time_days: float = Field(
        ..., description="Average resolution time after escalation", ge=0
    )
    auto_escalations_triggered: int = Field(
        ..., description="Number of auto-escalations", ge=0
    )
    pending_escalations: int = Field(..., description="Currently pending", ge=0)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_escalations": 45,
                "escalations_per_level": {
                    "level_1": 30,
                    "level_2": 12,
                    "level_3": 3,
                },
                "average_escalation_time_days": 2.5,
                "resolution_rate_percentage": 82.2,
                "average_resolution_time_days": 3.2,
                "auto_escalations_triggered": 18,
                "pending_escalations": 8,
            }
        }
