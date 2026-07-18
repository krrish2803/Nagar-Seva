"""Official user model for MongoDB."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class OfficialProfile(BaseModel):
    """Government official profile."""

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: str = Field(..., description="Office phone number")
    profile_image_url: Optional[str] = Field(None, description="Profile photo URL")
    designation: str = Field(..., description="Job title/designation")
    department: str = Field(..., description="Department name")
    ward_id: str = Field(..., description="Assigned ward ID")
    authority_level: str = Field(
        ...,
        description="Authorization level: field_staff/supervisor/department_head/commissioner",
    )
    office_address: str = Field(..., description="Office address")
    office_latitude: float = Field(..., description="Office latitude")
    office_longitude: float = Field(..., description="Office longitude")
    verified: bool = Field(default=True, description="Official verified by system")
    account_status: str = Field(default="active", description="active/on_leave/suspended")
    complaints_assigned: int = Field(default=0, description="Complaints assigned to official")
    complaints_resolved: int = Field(default=0, description="Complaints resolved by official")
    average_resolution_days: float = Field(default=0, description="Average resolution time")
    performance_rating: float = Field(default=0, ge=0, le=5, description="Performance rating")
    escalations_received: int = Field(default=0, description="Times escalated")
    escalations_handled: int = Field(default=0, description="Escalations they handled")
    availability_status: str = Field(default="available", description="available/busy/away")
    shift_start_hour: int = Field(default=9, description="Work shift start hour (0-23)")
    shift_end_hour: int = Field(default=17, description="Work shift end hour (0-23)")
    response_time_minutes: int = Field(default=60, description="Average response time in minutes")
    specializations: List[str] = Field(
        default_factory=list,
        description="Areas of expertise: pothole_repair, drainage, etc.",
    )
    team_members: List[str] = Field(
        default_factory=list, description="IDs of field staff under this official"
    )
    notification_preferences: Dict[str, Any] = Field(
        default_factory=dict, description="How to notify: email, sms, push, etc."
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True
