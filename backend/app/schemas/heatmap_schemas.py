"""Request and response schemas for heatmap endpoints."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class IssueTypeEnum(str, Enum):
    """Types of civic issues for heatmap."""

    POTHOLE = "pothole"
    WATER_LEAK = "water_leak"
    GARBAGE = "garbage"
    STREETLIGHT = "streetlight"
    TRAFFIC_SIGNAL = "traffic_signal"
    TREE_HAZARD = "tree_hazard"
    DRAINAGE = "drainage"
    PUBLIC_SAFETY = "public_safety"
    OTHER = "other"


class HotspotSchema(BaseModel):
    """Individual hotspot in heatmap."""

    latitude: float = Field(..., description="Latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude", ge=-180, le=180)
    intensity: float = Field(
        ..., description="Intensity score (0-1)", ge=0, le=1
    )
    issue_count: int = Field(..., description="Number of issues at this location", ge=1)
    recent_issues: List[str] = Field(
        default_factory=list, description="IDs of recent issues"
    )
    primary_issue_type: Optional[str] = Field(
        None, description="Most common issue type"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "intensity": 0.85,
                "issue_count": 12,
                "recent_issues": ["COMP_001", "COMP_002"],
                "primary_issue_type": "pothole",
            }
        }


class ClusterSchema(BaseModel):
    """Cluster of geographically close issues."""

    cluster_id: str = Field(..., description="Unique cluster identifier")
    center_latitude: float = Field(..., description="Cluster center latitude", ge=-90, le=90)
    center_longitude: float = Field(..., description="Cluster center longitude", ge=-180, le=180)
    radius_meters: int = Field(..., description="Cluster radius in meters", ge=100)
    issue_count: int = Field(..., description="Number of issues in cluster", ge=1)
    severity_distribution: Dict[str, int] = Field(
        ..., description="Count of issues by severity"
    )
    issue_type_distribution: Dict[str, int] = Field(
        ..., description="Count of issues by type"
    )
    hotspots: List[HotspotSchema] = Field(
        default_factory=list, description="Hotspots within cluster"
    )
    recent_activity_timestamp: datetime = Field(
        ..., description="Most recent issue timestamp"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "cluster_id": "CLU_001",
                "center_latitude": 40.7128,
                "center_longitude": -74.0060,
                "radius_meters": 500,
                "issue_count": 45,
                "severity_distribution": {
                    "low": 10,
                    "medium": 20,
                    "high": 12,
                    "critical": 3,
                },
                "issue_type_distribution": {
                    "pothole": 25,
                    "garbage": 15,
                    "water_leak": 5,
                },
            }
        }


class HeatmapDataResponse(BaseModel):
    """Complete heatmap data response."""

    generated_at: datetime = Field(..., description="Timestamp when heatmap was generated")
    time_period_days: int = Field(..., description="Number of days in analysis period", ge=1)
    total_issues: int = Field(..., description="Total issues in analysis period", ge=0)
    clusters: List[ClusterSchema] = Field(
        default_factory=list, description="All detected clusters"
    )
    hotspots: List[HotspotSchema] = Field(
        default_factory=list, description="Top hotspots"
    )
    statistics: Dict[str, Any] = Field(
        default_factory=dict, description="Heatmap statistics"
    )
    filters_applied: Dict[str, Any] = Field(
        default_factory=dict, description="Filters that were applied"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "generated_at": "2024-01-15T10:30:00Z",
                "time_period_days": 30,
                "total_issues": 250,
                "clusters": [],
                "hotspots": [],
                "statistics": {
                    "average_issue_density_per_km2": 45.3,
                    "most_common_issue_type": "pothole",
                    "critical_severity_count": 12,
                },
                "filters_applied": {
                    "issue_types": ["pothole", "water_leak"],
                    "min_severity": "medium",
                    "ward_ids": ["W001", "W002"],
                },
            }
        }


class HeatmapQueryRequest(BaseModel):
    """Request parameters for heatmap data."""

    time_period_days: Optional[int] = Field(
        default=30, description="Analysis period in days", ge=1, le=365
    )
    issue_types: Optional[List[str]] = Field(
        default=None, description="Filter by issue types"
    )
    min_severity: Optional[str] = Field(
        default=None, description="Minimum severity level"
    )
    ward_ids: Optional[List[str]] = Field(
        default=None, description="Filter by ward IDs"
    )
    latitude_min: Optional[float] = Field(
        default=None, description="Bounding box min latitude"
    )
    latitude_max: Optional[float] = Field(
        default=None, description="Bounding box max latitude"
    )
    longitude_min: Optional[float] = Field(
        default=None, description="Bounding box min longitude"
    )
    longitude_max: Optional[float] = Field(
        default=None, description="Bounding box max longitude"
    )
    clustering_radius_meters: Optional[int] = Field(
        default=500, description="Radius for clustering", ge=100, le=10000
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "time_period_days": 30,
                "issue_types": ["pothole", "water_leak"],
                "min_severity": "medium",
                "ward_ids": ["W001"],
                "clustering_radius_meters": 500,
            }
        }


class SeverityTrendSchema(BaseModel):
    """Severity trend over time."""

    date: str = Field(..., description="Date (YYYY-MM-DD)")
    low_count: int = Field(..., description="Count of low severity", ge=0)
    medium_count: int = Field(..., description="Count of medium severity", ge=0)
    high_count: int = Field(..., description="Count of high severity", ge=0)
    critical_count: int = Field(..., description="Count of critical severity", ge=0)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "low_count": 5,
                "medium_count": 12,
                "high_count": 8,
                "critical_count": 1,
            }
        }


class AnalyticsResponse(BaseModel):
    """Analytics response with trends and insights."""

    period_analyzed_days: int = Field(..., description="Analysis period", ge=1)
    total_complaints: int = Field(..., description="Total complaints", ge=0)
    resolved_complaints: int = Field(..., description="Resolved complaints", ge=0)
    resolution_rate: float = Field(..., description="Resolution rate percentage", ge=0, le=100)
    average_resolution_days: float = Field(
        ..., description="Average days to resolution", ge=0
    )
    severity_trends: List[SeverityTrendSchema] = Field(
        default_factory=list, description="Severity trends over time"
    )
    top_issue_types: Dict[str, int] = Field(
        ..., description="Top 5 issue types by count"
    )
    department_performance: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Performance by department"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "period_analyzed_days": 30,
                "total_complaints": 250,
                "resolved_complaints": 180,
                "resolution_rate": 72.0,
                "average_resolution_days": 4.5,
                "severity_trends": [],
                "top_issue_types": {
                    "pothole": 85,
                    "garbage": 65,
                    "water_leak": 45,
                },
                "department_performance": {
                    "Public Works": {
                        "assigned": 100,
                        "resolved": 75,
                        "avg_days": 4.2,
                    }
                },
            }
        }
