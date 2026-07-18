"""Safety models for MongoDB - incidents and clusters."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SafetyIncident(BaseModel):
    """Individual safety incident record."""

    id: Optional[str] = Field(default=None, alias="_id")
    complaint_id: str = Field(..., description="Associated complaint ID")
    incident_type: str = Field(..., description="Type of incident")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    severity: str = Field(..., description="Severity: low/medium/high/critical")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    description: str = Field(..., description="Incident description")
    reported_by: str = Field(..., description="Citizen ID who reported")
    resolved: bool = Field(default=False, description="Is incident resolved")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True


class ClusterPoint(BaseModel):
    """Point in a safety cluster."""

    complaint_id: str = Field(..., description="Complaint ID")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    severity: str = Field(..., description="Severity level")
    timestamp: datetime = Field(..., description="When reported")
    issue_type: str = Field(..., description="Type of issue")


class TimeWindow(BaseModel):
    """Time window analysis for cluster."""

    period: str = Field(..., description="Time period: morning/afternoon/evening/night")
    incident_count: int = Field(..., description="Number of incidents in this period")
    average_severity: float = Field(..., description="Average severity (0-1)")
    peak_hours: List[int] = Field(default_factory=list, description="Peak hours (0-23)")


class SafetyCluster(BaseModel):
    """Geographic cluster of safety incidents."""

    id: Optional[str] = Field(default=None, alias="_id")
    cluster_label: int = Field(..., description="DBSCAN cluster label")
    center_latitude: float = Field(..., description="Cluster center latitude")
    center_longitude: float = Field(..., description="Cluster center longitude")
    radius_meters: float = Field(..., description="Cluster radius")
    point_count: int = Field(..., description="Number of points in cluster")
    points: List[ClusterPoint] = Field(..., description="All points in cluster")
    risk_score: float = Field(..., ge=0, le=1, description="Overall risk score (0-1)")
    incident_types: Dict[str, int] = Field(default_factory=dict, description="Count by type")
    severity_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Count by severity"
    )
    time_analysis: List[TimeWindow] = Field(default_factory=list, description="Time window analysis")
    ward_id: Optional[str] = Field(None, description="Ward ID this cluster is in")
    is_active: bool = Field(default=True, description="Is this an active cluster")
    last_incident_at: datetime = Field(..., description="When was last incident")
    first_incident_at: datetime = Field(..., description="When was first incident")
    recommendations: List[str] = Field(default_factory=list, description="Action recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True
