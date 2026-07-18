"""Escalation model for MongoDB."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EscalationLevel(BaseModel):
    """A level in the escalation hierarchy."""

    level_number: int = Field(..., description="Escalation level (1, 2, 3)")
    level_name: str = Field(..., description="Level name: ward_supervisor, department_head, commissioner")
    target_official_id: str = Field(..., description="Official ID at this level")
    escalated_at: datetime = Field(..., description="When escalated to this level")
    acknowledged_at: Optional[datetime] = Field(None, description="When acknowledged")
    resolution_note: Optional[str] = Field(None, description="Resolution or action at this level")


class EscalationRecord(BaseModel):
    """Complete escalation record for a complaint."""

    id: Optional[str] = Field(default=None, alias="_id")
    complaint_id: str = Field(..., description="Complaint ID being escalated")
    citizen_id: str = Field(..., description="Submitting citizen")
    original_assignment_official_id: str = Field(..., description="Original assigned official")
    initial_escalation_at: datetime = Field(..., description="When escalation process started")
    current_level: int = Field(default=1, ge=1, le=3, description="Current escalation level")
    escalation_reason: str = Field(..., description="Why it was escalated")
    escalation_history: List[EscalationLevel] = Field(
        default_factory=list, description="History of escalation levels"
    )
    is_resolved: bool = Field(default=False, description="Has escalation been resolved")
    resolution_date: Optional[datetime] = Field(None, description="When resolved")
    resolution_summary: Optional[str] = Field(None, description="Resolution summary")
    citizen_satisfaction_rating: Optional[int] = Field(
        None, ge=1, le=5, description="Citizen rating after resolution"
    )
    escalation_summary: Optional[str] = Field(None, description="AI-generated escalation summary")
    documents: List[str] = Field(default_factory=list, description="Document URLs/IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True
