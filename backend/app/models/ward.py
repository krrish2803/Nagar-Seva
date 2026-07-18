"""Ward model for MongoDB."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class WardBoundary(BaseModel):
    """Geographic boundary of ward."""

    center_latitude: float = Field(..., description="Center latitude")
    center_longitude: float = Field(..., description="Center longitude")
    radius_meters: Optional[float] = Field(None, description="Radius if circular")
    polygon_coordinates: Optional[List[tuple]] = Field(
        None, description="List of (lat, lon) for boundary"
    )


class Department(BaseModel):
    """Department information within ward."""

    code: str = Field(..., description="Department code")
    name: str = Field(..., description="Department name")
    phone: Optional[str] = Field(None)
    email: Optional[str] = Field(None)


class WardOfficer(BaseModel):
    """Officer managing the ward."""

    officer_id: str = Field(..., description="Officer user ID")
    name: str = Field(..., description="Officer name")
    designation: str = Field(..., description="Officer designation")
    phone: Optional[str] = Field(None)
    email: Optional[str] = Field(None)


class Ward(BaseModel):
    """Ward model for MongoDB."""

    id: Optional[str] = Field(default=None, alias="_id")
    ward_number: int = Field(..., description="Ward number")
    ward_name: str = Field(..., description="Ward name")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State name")
    boundary: WardBoundary = Field(..., description="Ward geographic boundary")
    population: int = Field(default=0, description="Estimated population")
    area_sq_km: float = Field(..., description="Ward area in square kilometers")
    primary_officer: WardOfficer = Field(..., description="Primary ward officer")
    departments: List[Department] = Field(default_factory=list, description="Responsible departments")
    complaint_count: int = Field(default=0, description="Total complaints in this ward")
    average_resolution_days: float = Field(default=0, description="Average resolution time")
    current_issues_count: int = Field(default=0, description="Open/unresolved issues")
    risk_level: str = Field(default="low", description="Overall risk level: low/medium/high")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = True
        populate_by_name = True
