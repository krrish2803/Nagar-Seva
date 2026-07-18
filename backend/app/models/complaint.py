"""Complaint model for MongoDB."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    """Severity levels for complaints."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, Enum):
    """Types of civic issues."""

    POTHOLE = "pothole"
    WATER_LEAK = "water_leak"
    GARBAGE = "garbage"
    STREETLIGHT = "streetlight"
    TRAFFIC_SIGNAL = "traffic_signal"
    TREE_HAZARD = "tree_hazard"
    DRAINAGE = "drainage"
    PUBLIC_SAFETY = "public_safety"
    OTHER = "other"


class ComplaintStatus(str, Enum):
    """Status of complaint processing."""

    SUBMITTED = "submitted"
    CLASSIFIED = "classified"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class Location(BaseModel):
    """Geographic location with coordinates."""

    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    address: str = Field(..., description="Human-readable address")
    ward_id: Optional[str] = Field(None, description="Ward identifier")
    pin_code: Optional[str] = Field(None, description="PIN code")


class Classification(BaseModel):
    """Issue classification details."""

    issue_type: IssueType = Field(..., description="Classified issue type")
    severity: SeverityLevel = Field(..., description="Severity level")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")
    description: str = Field(..., description="Detailed description from analysis")
    extracted_keywords: List[str] = Field(default_factory=list, description="Key terms extracted")


class VoiceDraft(BaseModel):
    """AI-generated complaint draft from a voice-first report."""

    original_transcript: str = Field(..., description="Raw transcription in the spoken language")
    detected_language: str = Field(default="unknown", description="Detected spoken language")
    translated_text: str = Field(..., description="Translated/normalized English text")
    drafted_title: str = Field(..., description="AI-generated complaint title")
    drafted_description: str = Field(..., description="AI-generated detailed complaint")
    confidence: float = Field(default=0.7, ge=0, le=1, description="Draft confidence")
    needs_human_review: bool = Field(default=False, description="Whether the draft needs review")


class TrustScore(BaseModel):
    """Trust and verification signal for a complaint."""

    overall_score: float = Field(..., ge=0, le=1, description="Final trust score from 0 to 1")
    photo_quality_score: float = Field(default=0, ge=0, le=1, description="Photo clarity/evidence score")
    voice_clarity_score: float = Field(default=0, ge=0, le=1, description="Voice clarity/transcript score")
    location_accuracy_score: float = Field(default=0, ge=0, le=1, description="GPS/address consistency score")
    citizen_reputation_score: float = Field(default=0.5, ge=0, le=1, description="Reporter history score")
    otp_verified: bool = Field(default=False, description="Whether mobile OTP verification was completed")
    evidence_flags: List[str] = Field(default_factory=list, description="Issues with evidence quality")
    recommended_action: str = Field(
        default="accept",
        description="accept/request_more_evidence/manual_review/reject",
    )
    explanation: str = Field(..., description="Human-readable trust score explanation")
    scored_at: datetime = Field(default_factory=datetime.utcnow)


class MediaAttachment(BaseModel):
    """Media file attached to complaint."""

    type: str = Field(..., description="Type: image, video, audio")
    url: str = Field(..., description="File URL or storage path")
    file_name: str = Field(..., description="Original file name")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    size_bytes: Optional[int] = Field(None, description="File size in bytes")


class Assignment(BaseModel):
    """Assignment details for complaint."""

    official_id: str = Field(..., description="Assigned official ID")
    department: str = Field(..., description="Department responsible")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    sla_days: int = Field(..., ge=1, description="Service level agreement days")
    expected_resolution: datetime = Field(..., description="Expected resolution date")


class Escalation(BaseModel):
    """Escalation record."""

    level: int = Field(..., ge=1, description="Escalation level (1-3)")
    escalated_at: datetime = Field(default_factory=datetime.utcnow)
    escalated_to_official_id: str = Field(..., description="Official receiving escalation")
    reason: str = Field(..., description="Reason for escalation")
    summary: Optional[str] = Field(None, description="Escalation summary")


class ComplaintUpdate(BaseModel):
    """Update to complaint status."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: ComplaintStatus = Field(..., description="New status")
    message: str = Field(..., description="Update message")
    updated_by: str = Field(..., description="User or official ID making update")


class Complaint(BaseModel):
    """Main Complaint model for MongoDB."""

    id: Optional[str] = Field(default=None, alias="_id")
    citizen_id: str = Field(..., description="Submitting citizen ID")
    location: Location = Field(..., description="Complaint location")
    issue_title: str = Field(..., description="Brief issue title")
    issue_description: str = Field(..., description="Detailed description")
    classification: Optional[Classification] = Field(None, description="AI classification")
    voice_draft: Optional[VoiceDraft] = Field(None, description="Voice-first AI draft metadata")
    trust_score: Optional[TrustScore] = Field(None, description="AI trust and verification score")
    media_attachments: List[MediaAttachment] = Field(
        default_factory=list, description="Photos/videos/audio"
    )
    status: ComplaintStatus = Field(default=ComplaintStatus.SUBMITTED, description="Current status")
    assignment: Optional[Assignment] = Field(None, description="Current assignment")
    escalations: List[Escalation] = Field(default_factory=list, description="Escalation history")
    updates: List[ComplaintUpdate] = Field(default_factory=list, description="Status updates")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Resolution rating (1-5)")
    resolution_note: Optional[str] = Field(None, description="Resolution details")
    tags: List[str] = Field(default_factory=list, description="Search/filter tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True
