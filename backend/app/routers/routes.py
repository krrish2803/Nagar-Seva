"""API Router for safer route recommendations (Agent 4)."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.agents.route_advisor_agent import orchestrate_safer_routing
from app.utils.database import get_database, normalize_mongo_document
from app.utils.geospatial import haversine_distance

router = APIRouter(prefix="/api/routes", tags=["routes"])


class SaferRouteRequest(BaseModel):
    """Request for safer route recommendation."""

    start_latitude: float = Field(..., description="Start latitude")
    start_longitude: float = Field(..., description="Start longitude")
    start_address: str = Field(..., description="Start address")
    end_latitude: float = Field(..., description="End latitude")
    end_longitude: float = Field(..., description="End longitude")
    end_address: str = Field(..., description="End address")
    mode: str = Field(default="walking", description="Travel mode: walking, cycling, public_transport")
    avoid_dark_areas: bool = Field(default=True, description="Avoid poorly lit areas")
    prefer_main_roads: bool = Field(default=True, description="Prefer main/busy roads")
    avoid_busy_areas: bool = Field(default=False, description="Avoid peak hour congestion")


class SaferRouteResponse(BaseModel):
    """Response with safer route recommendations."""

    status: str
    total_routes: int
    routes: list


@router.post("/safer-path", response_model=SaferRouteResponse)
async def get_safer_route(request: SaferRouteRequest) -> SaferRouteResponse:
    """
    Get safer route recommendations with safety analysis.

    Orchestrates Agent 4: Safer Route Advisor Agent

    This endpoint:
    1. Generates base route with waypoints
    2. Queries safety incidents along route
    3. Calculates segment risk scores
    4. Applies user preferences
    5. Generates alternative routes
    6. Ranks routes by safety score

    Args:
        request: Route request with start/end points and preferences

    Returns:
        List of routes ranked by safety score
    """
    try:
        print(
            f"[API] Safer route request: {request.start_address} -> {request.end_address}"
        )

        # Prepare user preferences
        preferences = {
            "avoid_dark_areas": request.avoid_dark_areas,
            "prefer_main_roads": request.prefer_main_roads,
            "avoid_busy_areas": request.avoid_busy_areas,
        }

        # Run Agent 4
        routes = await orchestrate_safer_routing(
            start_lat=request.start_latitude,
            start_lon=request.start_longitude,
            start_address=request.start_address,
            end_lat=request.end_latitude,
            end_lon=request.end_longitude,
            end_address=request.end_address,
            mode=request.mode,
            user_preferences=preferences,
        )

        if not routes:
            raise HTTPException(status_code=404, detail="No routes found")

        return SaferRouteResponse(
            status="success",
            total_routes=len(routes),
            routes=routes,
        )

    except Exception as e:
        print(f"[API] Error generating safer route: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison")
async def compare_routes(
    start_latitude: float = Query(...),
    start_longitude: float = Query(...),
    end_latitude: float = Query(...),
    end_longitude: float = Query(...),
    mode: str = Query(default="walking"),
) -> dict:
    """
    Compare multiple routes with safety metrics.

    Args:
        start_latitude: Start latitude
        start_longitude: Start longitude
        end_latitude: End latitude
        end_longitude: End longitude
        mode: Travel mode

    Returns:
        Comparison of routes
    """
    try:
        db = await get_database()
        cursor = (
            db["routes"]
            .find(
                {
                    "start_latitude": start_latitude,
                    "start_longitude": start_longitude,
                    "end_latitude": end_latitude,
                    "end_longitude": end_longitude,
                    "mode": mode,
                }
            )
            .sort("created_at", -1)
            .limit(10)
        )
        routes = [normalize_mongo_document(route) async for route in cursor]
        if not routes:
            routes = await orchestrate_safer_routing(
                start_latitude,
                start_longitude,
                "Start",
                end_latitude,
                end_longitude,
                "End",
                mode,
                {},
            )

        safest = max(routes, key=lambda route: route.get("overall_safety_score", 0), default=None)
        fastest = min(routes, key=lambda route: route.get("estimated_duration_minutes", 0), default=None)
        least_incidents = min(routes, key=lambda route: route.get("incident_count", 0), default=None)
        return {
            "status": "success",
            "comparison": {
                "safest_route": safest,
                "fastest_route": fastest,
                "least_incident_route": least_incidents,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segment/{segment_id}/incidents")
async def get_segment_incidents(
    segment_id: str,
    buffer_radius: int = Query(300, ge=100, le=1000),
) -> dict:
    """
    Get incidents near a specific route segment.

    Args:
        segment_id: Segment ID
        buffer_radius: Search radius in meters

    Returns:
        Incidents near segment
    """
    try:
        db = await get_database()
        route = await db["routes"].find_one({"_id": segment_id})
        center_points = []
        if route:
            route = normalize_mongo_document(route) or {}
            center_points = route.get("waypoints", [])

        incidents = []
        async for incident_doc in db["safety_incidents"].find({"resolved": False}):
            incident = normalize_mongo_document(incident_doc) or {}
            for point in center_points:
                distance = haversine_distance(
                    point["latitude"],
                    point["longitude"],
                    incident.get("latitude", 0),
                    incident.get("longitude", 0),
                )
                if distance <= buffer_radius:
                    incident["distance_meters"] = distance
                    incidents.append(incident)
                    break

        return {
            "segment_id": segment_id,
            "buffer_radius_meters": buffer_radius,
            "incident_count": len(incidents),
            "incidents": incidents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/time-analysis")
async def analyze_route_by_time(
    start_latitude: float = Query(...),
    start_longitude: float = Query(...),
    end_latitude: float = Query(...),
    end_longitude: float = Query(...),
) -> dict:
    """
    Analyze route safety across different times of day.

    Args:
        start_latitude: Start latitude
        start_longitude: Start longitude
        end_latitude: End latitude
        end_longitude: End longitude

    Returns:
        Time-based safety analysis
    """
    try:
        db = await get_database()
        incidents = []
        async for incident_doc in db["safety_incidents"].find({"resolved": False}):
            incident = normalize_mongo_document(incident_doc) or {}
            incidents.append(incident)

        def count_near_route() -> int:
            count = 0
            for incident in incidents:
                start_dist = haversine_distance(
                    start_latitude,
                    start_longitude,
                    incident.get("latitude", 0),
                    incident.get("longitude", 0),
                )
                end_dist = haversine_distance(
                    end_latitude,
                    end_longitude,
                    incident.get("latitude", 0),
                    incident.get("longitude", 0),
                )
                if min(start_dist, end_dist) <= 1000:
                    count += 1
            return count

        incident_count = count_near_route()
        base_scores = {
            "morning": 0.85,
            "afternoon": 0.72,
            "evening": 0.58,
            "night": 0.38,
        }
        analysis = {}
        for period, score in base_scores.items():
            adjusted = max(0.05, score - min(0.5, incident_count * 0.04))
            analysis[period] = {
                "safest_time": False,
                "safety_score": round(adjusted, 2),
                "incident_count": incident_count,
            }
        safest_period = max(analysis, key=lambda key: analysis[key]["safety_score"])
        analysis[safest_period]["safest_time"] = True

        return {
            "status": "success",
            "time_analysis": analysis,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
