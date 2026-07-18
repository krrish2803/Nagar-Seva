"""Route model for safer path recommendations."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Waypoint(BaseModel):
    """A waypoint on a route."""

    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    order: int = Field(..., description="Order on route")
    distance_from_start_meters: float = Field(..., description="Distance from start")


class RouteSegment(BaseModel):
    """Segment of a route between waypoints."""

    start_waypoint: Waypoint = Field(..., description="Starting waypoint")
    end_waypoint: Waypoint = Field(..., description="Ending waypoint")
    distance_meters: float = Field(..., description="Segment distance")
    estimated_duration_minutes: float = Field(..., description="Travel time estimate")
    safety_score: float = Field(..., ge=0, le=1, description="Safety score for segment")
    safety_factors: Dict[str, Any] = Field(
        default_factory=dict, description="Factors affecting safety"
    )
    incidents_nearby: int = Field(default=0, description="Incidents near this segment")
    risk_level: str = Field(..., description="Risk level: low/medium/high/critical")
    time_of_day_safe: List[str] = Field(
        default_factory=list, description="Safest times: morning/afternoon/evening/night"
    )


class SaferRoute(BaseModel):
    """Complete safer route recommendation."""

    id: Optional[str] = Field(default=None, alias="_id")
    start_latitude: float = Field(..., description="Start latitude")
    start_longitude: float = Field(..., description="Start longitude")
    end_latitude: float = Field(..., description="End latitude")
    end_longitude: float = Field(..., description="End longitude")
    start_address: str = Field(..., description="Start address")
    end_address: str = Field(..., description="End address")
    route_index: int = Field(..., description="Route ranking (1 = safest)")
    mode: str = Field(..., description="Travel mode: walking/cycling/public_transport")
    waypoints: List[Waypoint] = Field(..., description="Route waypoints")
    segments: List[RouteSegment] = Field(..., description="Route segments")
    total_distance_meters: float = Field(..., description="Total route distance")
    total_estimated_duration_minutes: float = Field(..., description="Total travel time")
    overall_safety_score: float = Field(..., ge=0, le=1, description="Overall safety score")
    overall_risk_level: str = Field(..., description="Overall risk: low/medium/high/critical")
    incident_clusters_crossed: int = Field(
        default=0, description="Number of incident clusters on route"
    )
    high_risk_zones: int = Field(default=0, description="Number of high-risk segments")
    recommended_times: List[str] = Field(
        default_factory=list, description="Safest times: morning/afternoon/evening/night"
    )
    alternative_available: bool = Field(
        default=True, description="Are alternative routes available"
    )
    user_preferences_applied: Dict[str, Any] = Field(
        default_factory=dict, description="User preferences that affected routing"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True
