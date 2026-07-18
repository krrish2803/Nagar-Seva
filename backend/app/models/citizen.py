"""Citizen user model for MongoDB."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class CitizenProfile(BaseModel):
    """Citizen user profile."""

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    profile_image_url: Optional[str] = Field(None, description="Profile photo URL")
    bio: Optional[str] = Field(None, description="User bio/description")
    latitude: Optional[float] = Field(None, description="Home latitude")
    longitude: Optional[float] = Field(None, description="Home longitude")
    ward_id: Optional[str] = Field(None, description="Preferred ward")
    verified: bool = Field(default=False, description="Email verified")
    account_status: str = Field(default="active", description="active/suspended/deleted")
    complaints_submitted: int = Field(default=0, description="Total complaints submitted")
    complaints_resolved: int = Field(default=0, description="Complaints marked resolved")
    average_rating: float = Field(default=0, ge=0, le=5, description="Average resolution rating")
    badges: List[str] = Field(
        default_factory=list, description="Earned badges (e.g., 'civic_hero', 'early_adopter')"
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User preferences: route_mode, notification_settings, privacy_level, etc.",
    )
    notification_settings: Dict[str, bool] = Field(
        default_factory=dict,
        description="Email/SMS/push notification preferences",
    )
    impact_score: int = Field(
        default=0, description="Score based on resolved complaints and community impact"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True
