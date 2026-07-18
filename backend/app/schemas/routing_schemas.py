"""Request and response schemas for routing endpoints."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class DepartmentEnum(str, Enum):
    """Civic departments."""

    PUBLIC_WORKS = "public_works"
    WATER_SUPPLY = "water_supply"
    SANITATION = "sanitation"
    TRAFFIC = "traffic"
    SAFETY = "safety"
    PARKS = "parks"
    DRAINAGE = "drainage"
    UTILITIES = "utilities"


class RoutingRequest(BaseModel):
    """Request to route a complaint to appropriate authority."""

    complaint_id: str = Field(..., description="Complaint ID", min_length=1)
    issue_type: str = Field(..., description="Classified issue type")
    severity: str = Field(..., description="Severity level")
    location_latitude: float = Field(
        ..., description="Latitude of issue", ge=-90, le=90
    )
    location_longitude: float = Field(
        ..., description="Longitude of issue", ge=-180, le=180
    )
    ward_id: Optional[str] = Field(None, description="Ward ID")
    department_priority: Optional[str] = Field(
        None, description="Preferred department"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "complaint_id": "COMP_uuid",
                "issue_type": "pothole",
                "severity": "high",
                "location_latitude": 40.7128,
                "location_longitude": -74.0060,
                "ward_id": "W001",
            }
        }


class OfficialSchema(BaseModel):
    """Official assigned to handle complaint."""

    official_id: str = Field(..., description="Official ID")
    name: str = Field(..., description="Official name")
    email: str = Field(..., description="Official email")
    phone: str = Field(..., description="Official phone")
    department: str = Field(..., description="Department")
    workload: int = Field(..., description="Current workload count", ge=0)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "official_id": "OFF_12345",
                "name": "John Smith",
                "email": "john@publicworks.gov",
                "phone": "+1-555-0123",
                "department": "Public Works",
                "workload": 5,
            }
        }


class RoutingRulesSchema(BaseModel):
    """Routing rules applied."""

    rule_id: str = Field(..., description="Applied rule ID")
    sla_days: int = Field(..., description="Service level agreement days", ge=1)
    priority_level: str = Field(
        ..., description="Priority level: low, medium, high, critical"
    )
    escalation_threshold_days: int = Field(
        ..., description="Days before escalation", ge=1
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "rule_id": "RULE_POT001",
                "sla_days": 7,
                "priority_level": "high",
                "escalation_threshold_days": 5,
            }
        }


class RoutingResponse(BaseModel):
    """Response after routing complaint."""

    complaint_id: str = Field(..., description="Complaint ID")
    routing_status: str = Field(..., description="Routing status")
    assigned_official: OfficialSchema = Field(..., description="Assigned official")
    routing_rules: RoutingRulesSchema = Field(..., description="Applied rules")
    assignment_timestamp: datetime = Field(
        ..., description="When assignment was made"
    )
    message: str = Field(..., description="Routing message")
    confidence_score: Optional[float] = Field(
        None, description="Routing decision confidence", ge=0, le=1
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "complaint_id": "COMP_uuid",
                "routing_status": "assigned",
                "assigned_official": {
                    "official_id": "OFF_12345",
                    "name": "John Smith",
                    "email": "john@publicworks.gov",
                },
                "routing_rules": {
                    "rule_id": "RULE_POT001",
                    "sla_days": 7,
                    "priority_level": "high",
                },
                "message": "Complaint routed to Public Works",
                "confidence_score": 0.92,
            }
        }


class RoutingMetricsSchema(BaseModel):
    """Routing metrics and statistics."""

    total_routed_complaints: int = Field(..., description="Total routed complaints", ge=0)
    average_routing_time_seconds: float = Field(
        ..., description="Average routing time", ge=0
    )
    officials_load_distribution: Dict[str, int] = Field(
        ..., description="Load per official"
    )
    department_distribution: Dict[str, int] = Field(
        ..., description="Distribution by department"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_routed_complaints": 450,
                "average_routing_time_seconds": 1.23,
                "officials_load_distribution": {
                    "OFF_12345": 5,
                    "OFF_12346": 8,
                },
                "department_distribution": {
                    "Public Works": 200,
                    "Water Supply": 150,
                },
            }
        }
