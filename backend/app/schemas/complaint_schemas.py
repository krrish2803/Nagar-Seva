"""Request and response schemas for complaint endpoints."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


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


class LocationSchema(BaseModel):
    """Geographic location with coordinates."""

    latitude: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude coordinate", ge=-180, le=180)
    address: str = Field(..., description="Human-readable address", min_length=5)
    ward_id: Optional[str] = Field(None, description="Ward identifier")
    pin_code: Optional[str] = Field(None, description="PIN code")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ClassificationSchema(BaseModel):
    """Issue classification details."""

    issue_type: IssueType = Field(..., description="Classified issue type")
    severity: SeverityLevel = Field(..., description="Severity level")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")
    description: str = Field(..., description="Detailed description from analysis")
    extracted_keywords: List[str] = Field(
        default_factory=list, description="Key terms extracted"
    )

    class Config:
        """Pydantic config."""

        use_enum_values = True


class MediaAttachmentSchema(BaseModel):
    """Media file attached to complaint."""

    type: str = Field(..., description="Type: image, video, audio")
    url: str = Field(..., description="File URL or storage path")
    file_name: str = Field(..., description="Original file name")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    size_bytes: Optional[int] = Field(None, description="File size in bytes", ge=0)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "type": "image",
                "url": "uploads/complaint_123_image.jpg",
                "file_name": "pothole.jpg",
                "size_bytes": 2048000,
            }
        }


class AssignmentSchema(BaseModel):
    """Assignment details for complaint."""

    official_id: str = Field(..., description="Assigned official ID")
    department: str = Field(..., description="Department responsible")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    sla_days: int = Field(..., ge=1, description="Service level agreement days")
    expected_resolution: datetime = Field(..., description="Expected resolution date")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "official_id": "OFF_12345",
                "department": "Public Works",
                "sla_days": 7,
            }
        }


class ComplaintReportRequest(BaseModel):
    """Request to submit a complaint."""

    citizen_id: str = Field(..., description="Submitting citizen ID", min_length=1)
    issue_title: str = Field(
        ..., description="Brief issue title", min_length=5, max_length=200
    )
    issue_description: str = Field(
        ..., description="Detailed description", min_length=10, max_length=2000
    )
    location: LocationSchema = Field(..., description="Complaint location")
    tags: List[str] = Field(default_factory=list, description="Optional tags")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "citizen_id": "CITI_12345",
                "issue_title": "Large pothole on Main Street",
                "issue_description": "There is a large pothole causing traffic hazards",
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "address": "123 Main St, New York, NY 10001",
                    "ward_id": "W001",
                    "pin_code": "10001",
                },
                "tags": ["road-safety", "urgent"],
            }
        }


class ComplaintResponse(BaseModel):
    """Response after complaint submission."""

    complaint_id: str = Field(..., description="Unique complaint ID")
    status: str = Field(..., description="Current complaint status")
    issue_type: str = Field(..., description="Classified issue type")
    severity: str = Field(..., description="Severity level")
    assigned_to_official_id: str = Field(..., description="Assigned official ID")
    sla_days: int = Field(..., description="Service level agreement days")
    confidence: Optional[float] = Field(
        None, description="Classification confidence score"
    )
    message: str = Field(..., description="Response message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "complaint_id": "COMP_uuid_here",
                "status": "assigned",
                "issue_type": "pothole",
                "severity": "high",
                "assigned_to_official_id": "OFF_12345",
                "sla_days": 7,
                "confidence": 0.95,
                "message": "Complaint successfully submitted and assigned",
            }
        }


class ComplaintDetailResponse(BaseModel):
    """Detailed complaint response."""

    id: str = Field(..., alias="_id", description="Complaint ID")
    citizen_id: str = Field(..., description="Submitting citizen ID")
    issue_title: str = Field(..., description="Issue title")
    issue_description: str = Field(..., description="Detailed description")
    location: LocationSchema = Field(..., description="Complaint location")
    classification: Optional[ClassificationSchema] = Field(
        None, description="AI classification"
    )
    status: ComplaintStatus = Field(..., description="Current status")
    assignment: Optional[AssignmentSchema] = Field(None, description="Assignment info")
    media_attachments: List[MediaAttachmentSchema] = Field(
        default_factory=list, description="Media files"
    )
    rating: Optional[int] = Field(None, ge=1, le=5, description="Resolution rating")
    resolution_note: Optional[str] = Field(None, description="Resolution details")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        populate_by_name = True
        use_enum_values = True


class ComplaintListResponse(BaseModel):
    """List of complaints response."""

    total: int = Field(..., description="Total complaints count")
    skip: int = Field(..., description="Records skipped")
    limit: int = Field(..., description="Records limit")
    complaints: List[ComplaintDetailResponse] = Field(
        default_factory=list, description="List of complaints"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total": 150,
                "skip": 0,
                "limit": 10,
                "complaints": [],
            }
        }


class ComplaintUpdateRequest(BaseModel):
    """Request to update complaint status."""

    new_status: ComplaintStatus = Field(..., description="New status value")
    update_note: str = Field(
        default="", description="Note about the update", max_length=500
    )
    updated_by: str = Field(
        ..., description="User ID making update", min_length=1
    )

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ComplaintUpdateResponse(BaseModel):
    """Response after updating complaint."""

    complaint_id: str = Field(..., description="Complaint ID")
    status: str = Field(..., description="New status")
    updated_at: datetime = Field(..., description="Update timestamp")
    message: str = Field(..., description="Update message")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "complaint_id": "COMP_uuid",
                "status": "in_progress",
                "message": "Status updated successfully",
            }
        }
