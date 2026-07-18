"""Request and response schemas for route endpoints."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class RouteTypeEnum(str, Enum):
    """Types of routes."""

    SHORTEST = "shortest"
    SAFEST = "safest"
    BALANCED = "balanced"


class RiskLevelEnum(str, Enum):
    """Risk levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RoadSegmentSchema(BaseModel):
    """Individual road segment in route."""

    latitude: float = Field(..., description="Segment latitude", ge=-90, le=90)
    longitude: float = Field(..., description="Segment longitude", ge=-180, le=180)
    next_latitude: float = Field(..., description="Next point latitude", ge=-90, le=90)
    next_longitude: float = Field(..., description="Next point longitude", ge=-180, le=180)
    distance_meters: float = Field(..., description="Segment distance", ge=0)
    risk_level: RiskLevelEnum = Field(..., description="Risk level of this segment")
    issues_count: int = Field(..., description="Number of issues on this segment", ge=0)
    speed_limit_kmh: Optional[int] = Field(None, description="Speed limit in km/h")
    road_condition: Optional[str] = Field(
        None, description="Road condition description"
    )

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "next_latitude": 40.7135,
                "next_longitude": -74.0065,
                "distance_meters": 250.5,
                "risk_level": "low",
                "issues_count": 0,
                "speed_limit_kmh": 50,
            }
        }


class SaferRouteRequest(BaseModel):
    """Request for safer route calculation."""

    origin_latitude: float = Field(
        ..., description="Origin latitude", ge=-90, le=90
    )
    origin_longitude: float = Field(
        ..., description="Origin longitude", ge=-180, le=180
    )
    destination_latitude: float = Field(
        ..., description="Destination latitude", ge=-90, le=90
    )
    destination_longitude: float = Field(
        ..., description="Destination longitude", ge=-180, le=180
    )
    route_type: Optional[RouteTypeEnum] = Field(
        default=RouteTypeEnum.SAFEST, description="Type of route optimization"
    )
    avoid_critical_areas: Optional[bool] = Field(
        default=True, description="Avoid critical safety zones"
    )
    user_vulnerability_level: Optional[str] = Field(
        default="medium",
        description="User vulnerability: low, medium, high (e.g., elderly, children)",
    )

    class Config:
        """Pydantic config."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "origin_latitude": 40.7128,
                "origin_longitude": -74.0060,
                "destination_latitude": 40.7200,
                "destination_longitude": -74.0100,
                "route_type": "safest",
                "avoid_critical_areas": True,
                "user_vulnerability_level": "medium",
            }
        }


class RouteMetricsSchema(BaseModel):
    """Metrics for a route."""

    total_distance_km: float = Field(..., description="Total distance in km", ge=0)
    estimated_duration_minutes: float = Field(
        ..., description="Estimated travel time", ge=0
    )
    safety_score: float = Field(
        ..., description="Safety score (0-100)", ge=0, le=100
    )
    risk_zones_count: int = Field(
        ..., description="Number of risk zones on route", ge=0
    )
    well_lit_percentage: float = Field(
        ..., description="Percentage of well-lit segments", ge=0, le=100
    )
    crowd_level_percentage: Optional[float] = Field(
        None, description="Estimated crowd presence", ge=0, le=100
    )
    traffic_congestion_level: Optional[str] = Field(
        None, description="Congestion: low, medium, high"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_distance_km": 2.5,
                "estimated_duration_minutes": 8.5,
                "safety_score": 78.5,
                "risk_zones_count": 1,
                "well_lit_percentage": 85.0,
                "crowd_level_percentage": 60.0,
                "traffic_congestion_level": "low",
            }
        }


class RouteResponse(BaseModel):
    """Response with calculated route."""

    route_id: str = Field(..., description="Unique route identifier")
    created_at: datetime = Field(..., description="Route creation timestamp")
    route_type: str = Field(..., description="Type of route")
    origin: Dict[str, float] = Field(..., description="Origin coordinates")
    destination: Dict[str, float] = Field(..., description="Destination coordinates")
    segments: List[RoadSegmentSchema] = Field(
        default_factory=list, description="Route segments"
    )
    metrics: RouteMetricsSchema = Field(..., description="Route metrics")
    alerts: List[Dict[str, Any]] = Field(
        default_factory=list, description="Safety alerts along route"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Safety recommendations"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "route_id": "ROUTE_uuid",
                "route_type": "safest",
                "created_at": "2024-01-15T10:30:00Z",
                "origin": {"latitude": 40.7128, "longitude": -74.0060},
                "destination": {"latitude": 40.7200, "longitude": -74.0100},
                "segments": [],
                "metrics": {
                    "total_distance_km": 2.5,
                    "safety_score": 78.5,
                },
                "alerts": [],
                "recommendations": ["Avoid peak hours", "Stay alert in Zone A"],
            }
        }


class RoutesListResponse(BaseModel):
    """List of calculated routes."""

    total_routes: int = Field(..., description="Total routes calculated", ge=0)
    routes: List[RouteResponse] = Field(
        default_factory=list, description="List of routes"
    )
    comparison_summary: Optional[Dict[str, Any]] = Field(
        None, description="Comparison metrics between routes"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_routes": 3,
                "routes": [],
                "comparison_summary": {
                    "safest_route_id": "ROUTE_001",
                    "shortest_route_id": "ROUTE_002",
                    "safety_difference_percent": 12.5,
                    "distance_difference_km": 1.2,
                },
            }
        }


class RouteRecommendationSchema(BaseModel):
    """Route recommendation for a user profile."""

    user_id: str = Field(..., description="User identifier")
    origin: Dict[str, float] = Field(..., description="Origin coordinates")
    destination: Dict[str, float] = Field(..., description="Destination coordinates")
    recommended_route_id: str = Field(
        ..., description="ID of recommended route"
    )
    reason: str = Field(..., description="Why this route is recommended")
    time_of_day: Optional[str] = Field(
        None, description="Optimal time to travel (e.g., avoid 5-7pm)"
    )
    safe_travel_window_start: Optional[str] = Field(
        None, description="Start of safest travel window (HH:MM)"
    )
    safe_travel_window_end: Optional[str] = Field(
        None, description="End of safest travel window (HH:MM)"
    )
    emergency_contacts: Optional[List[Dict[str, str]]] = Field(
        None, description="Emergency contacts for the area"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "USER_123",
                "origin": {"latitude": 40.7128, "longitude": -74.0060},
                "destination": {"latitude": 40.7200, "longitude": -74.0100},
                "recommended_route_id": "ROUTE_001",
                "reason": "Safest option with good lighting coverage",
                "time_of_day": "Recommend 8-10am or 3-5pm",
                "safe_travel_window_start": "08:00",
                "safe_travel_window_end": "20:00",
                "emergency_contacts": [
                    {
                        "type": "police",
                        "number": "+1-555-0100",
                        "distance_km": 0.5,
                    }
                ],
            }
        }
