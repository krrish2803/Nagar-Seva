"""Agent 4: Safer Route Advisor Agent."""

from typing import List, Dict, Any, Tuple
from datetime import datetime
import httpx

from app.models.route import SaferRoute, RouteSegment, Waypoint
from app.utils.geospatial import (
    haversine_distance,
    interpolate_route,
    create_bounding_box,
    get_points_within_radius,
)
from app.utils.nvidia_nim import generate_route_safety_analysis
from app.utils.database import get_database, normalize_mongo_document


async def get_base_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    mode: str = "walking",
) -> List[Waypoint]:
    """
    Generate base route waypoints between start and end.

    Args:
        start_lat: Start latitude
        start_lon: Start longitude
        end_lat: End latitude
        end_lon: End longitude
        mode: Travel mode (walking, cycling, public_transport)

    Returns:
        List of waypoints
    """
    try:
        osrm_url = (
            "http://router.project-osrm.org/route/v1/"
            f"{'foot' if mode == 'walking' else 'driving'}/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}"
        )
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(
                    osrm_url,
                    params={
                        "overview": "full",
                        "geometries": "geojson",
                        "steps": "false",
                    },
                )
                response.raise_for_status()
                data = response.json()
                coordinates = data["routes"][0]["geometry"]["coordinates"]
                if len(coordinates) > 25:
                    stride = max(1, len(coordinates) // 25)
                    coordinates = coordinates[::stride]
                    if coordinates[-1] != data["routes"][0]["geometry"]["coordinates"][-1]:
                        coordinates.append(data["routes"][0]["geometry"]["coordinates"][-1])

                waypoints = []
                total_distance = 0.0
                previous = None
                for order, (lon, lat) in enumerate(coordinates):
                    if previous:
                        total_distance += haversine_distance(previous[0], previous[1], lat, lon)
                    previous = (lat, lon)
                    waypoints.append(
                        Waypoint(
                            latitude=lat,
                            longitude=lon,
                            order=order,
                            distance_from_start_meters=total_distance,
                        )
                    )

                print(f"[ROUTE] Generated provider route with {len(waypoints)} waypoints")
                return waypoints
        except Exception as provider_error:
            print(f"[ROUTE] Routing provider unavailable, using interpolation: {provider_error}")

        # Interpolate waypoints as a local fallback
        num_waypoints = 5 if mode == "walking" else 10
        coords = interpolate_route(
            start_lat, start_lon, end_lat, end_lon, num_waypoints
        )

        waypoints = []
        total_distance = 0
        for order, (lat, lon) in enumerate(coords):
            if order > 0:
                prev_lat, prev_lon = coords[order - 1]
                segment_dist = haversine_distance(prev_lat, prev_lon, lat, lon)
                total_distance += segment_dist
            else:
                segment_dist = 0

            waypoint = Waypoint(
                latitude=lat,
                longitude=lon,
                order=order,
                distance_from_start_meters=total_distance,
            )
            waypoints.append(waypoint)

        print(f"[ROUTE] Generated base route with {len(waypoints)} waypoints")
        return waypoints
    except Exception as e:
        print(f"[ROUTE] Error generating base route: {e}")
        return []


async def query_safety_along_route(
    waypoints: List[Waypoint],
    buffer_radius: int = 300,
    mock_clusters: List[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Query safety incidents along route.

    Args:
        waypoints: Route waypoints
        buffer_radius: Search radius around route in meters
        mock_clusters: Optional mock safety clusters

    Returns:
        Safety data along route
    """
    try:
        db = await get_database()
        incident_points = []
        async for document in db["safety_incidents"].find({"resolved": False}):
            incident = normalize_mongo_document(document) or {}
            if incident.get("latitude") is None or incident.get("longitude") is None:
                continue
            severity = incident.get("severity", "medium")
            risk_score = {
                "critical": 1.0,
                "high": 0.75,
                "medium": 0.45,
                "low": 0.2,
            }.get(severity, 0.45)
            incident_points.append(
                {
                    "latitude": incident["latitude"],
                    "longitude": incident["longitude"],
                    "risk_score": risk_score,
                    "incident_type": incident.get("incident_type"),
                    "complaint_id": incident.get("complaint_id"),
                    "severity": severity,
                }
            )

        if mock_clusters:
            incident_points.extend(mock_clusters)

        route_safety = {}
        for waypoint in waypoints:
            points_in_buffer = get_points_within_radius(
                waypoint.latitude,
                waypoint.longitude,
                buffer_radius,
                incident_points,
            )

            route_safety[f"waypoint_{waypoint.order}"] = {
                "latitude": waypoint.latitude,
                "longitude": waypoint.longitude,
                "incident_count": len(points_in_buffer),
                "nearby_clusters": points_in_buffer,
            }

        print(f"[ROUTE] Queried safety for {len(waypoints)} waypoints")
        return route_safety
    except Exception as e:
        print(f"[ROUTE] Error querying safety: {e}")
        return {}


async def calculate_segment_risk(
    segment_data: Dict[str, Any],
    time_of_day: str = "afternoon",
) -> float:
    """
    Calculate risk score for a route segment.

    Args:
        segment_data: Segment safety data
        time_of_day: Time period (morning, afternoon, evening, night)

    Returns:
        Risk score (0-1)
    """
    try:
        # Get analysis from NVIDIA LLM
        analysis = await generate_route_safety_analysis(
            segment_data, time_of_day
        )

        risk_score = analysis.get("risk_score", 0.5)
        print(f"[ROUTE] Calculated segment risk: {risk_score:.2f}")
        return risk_score
    except Exception as e:
        print(f"[ROUTE] Error calculating segment risk: {e}")
        return 0.5


async def apply_user_preferences(
    route_segments: List[Dict[str, Any]],
    preferences: Dict[str, Any],
    current_time: datetime = None,
) -> List[Dict[str, Any]]:
    """
    Apply user preferences to route segments.

    Args:
        route_segments: List of route segments
        preferences: User preferences (e.g., avoid_dark_areas, prefer_main_roads)
        current_time: Current time for context

    Returns:
        Modified segments with preferences applied
    """
    try:
        current_time = current_time or datetime.utcnow()
        hour = current_time.hour

        modified_segments = []
        for segment in route_segments:
            seg_copy = segment.copy()

            # Apply preferences
            if preferences.get("avoid_dark_areas") and hour > 20:
                seg_copy["safety_factor"] = seg_copy.get("risk_score", 0.5) * 1.3

            if preferences.get("prefer_main_roads"):
                # Bonus for main roads
                seg_copy["safety_factor"] = seg_copy.get("risk_score", 0.5) * 0.8

            if preferences.get("avoid_busy_areas"):
                # Adjust for time (peak hours are busier)
                if 8 <= hour <= 10 or 17 <= hour <= 19:
                    seg_copy["safety_factor"] = seg_copy.get("risk_score", 0.5) * 1.2

            modified_segments.append(seg_copy)

        print(f"[ROUTE] Applied preferences to {len(modified_segments)} segments")
        return modified_segments
    except Exception as e:
        print(f"[ROUTE] Error applying preferences: {e}")
        return route_segments


async def generate_alternative_routes(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    primary_waypoints: List[Waypoint],
    num_alternatives: int = 2,
) -> List[List[Waypoint]]:
    """
    Generate alternative routes.

    Args:
        start_lat: Start latitude
        start_lon: Start longitude
        end_lat: End latitude
        end_lon: End longitude
        primary_waypoints: Primary route waypoints
        num_alternatives: Number of alternatives to generate

    Returns:
        List of alternative routes
    """
    try:
        alternatives = []

        # Generate offset routes (simple lateral offsets for demo)
        for i in range(num_alternatives):
            offset = 0.001 * (i + 1)  # Small coordinate offset
            alt_waypoints = []

            for wp in primary_waypoints:
                alt_wp = Waypoint(
                    latitude=wp.latitude + (offset if i % 2 == 0 else -offset),
                    longitude=wp.longitude + (offset if i % 2 == 1 else -offset),
                    order=wp.order,
                    distance_from_start_meters=wp.distance_from_start_meters,
                )
                alt_waypoints.append(alt_wp)

            alternatives.append(alt_waypoints)

        print(f"[ROUTE] Generated {len(alternatives)} alternative routes")
        return alternatives
    except Exception as e:
        print(f"[ROUTE] Error generating alternatives: {e}")
        return []


async def rank_routes_by_safety(
    routes: List[List[Waypoint]],
    user_preferences: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Rank routes by safety score.

    Args:
        routes: List of routes (each is list of waypoints)
        user_preferences: User preferences for ranking

    Returns:
        Ranked routes with safety scores
    """
    try:
        ranked_routes = []

        for route_idx, route in enumerate(routes):
            route_safety = await query_safety_along_route(route)
            total_risk = 0.0
            total_incidents = 0
            for waypoint_data in route_safety.values():
                nearby_clusters = waypoint_data.get("nearby_clusters", [])
                total_incidents += len(nearby_clusters)
                if nearby_clusters:
                    total_risk += max(point.get("risk_score", 0.45) for point in nearby_clusters)
                else:
                    total_risk += 0.15

            avg_risk = total_risk / len(route) if route else 0.5
            safety_score = 1.0 - min(avg_risk, 1.0)

            route_data = {
                "route_index": route_idx + 1,
                "waypoints": [wp.dict() for wp in route],
                "total_distance_meters": route[-1].distance_from_start_meters if route else 0,
                "overall_safety_score": safety_score,
                "risk_level": "low"
                if safety_score > 0.7
                else "medium"
                if safety_score > 0.4
                else "high",
                "estimated_duration_minutes": int(
                    (route[-1].distance_from_start_meters / 1000 * 12)
                    if route
                    else 0
                ),
                "incident_count": total_incidents,
            }
            ranked_routes.append(route_data)

        # Sort by safety score (highest first)
        ranked_routes.sort(key=lambda x: x["overall_safety_score"], reverse=True)

        # Re-index after sorting
        for idx, route in enumerate(ranked_routes):
            route["route_index"] = idx + 1

        print(f"[ROUTE] Ranked {len(ranked_routes)} routes by safety")
        return ranked_routes
    except Exception as e:
        print(f"[ROUTE] Error ranking routes: {e}")
        return []


async def orchestrate_safer_routing(
    start_lat: float,
    start_lon: float,
    start_address: str,
    end_lat: float,
    end_lon: float,
    end_address: str,
    mode: str = "walking",
    user_preferences: Dict[str, Any] = None,
) -> List[Dict[str, Any]]:
    """
    Orchestrate complete safer route generation.

    Args:
        start_lat: Start latitude
        start_lon: Start longitude
        start_address: Start address
        end_lat: End latitude
        end_lon: End longitude
        end_address: End address
        mode: Travel mode
        user_preferences: User preferences

    Returns:
        List of ranked safer routes
    """
    print(f"[ROUTE] Starting safer route orchestration")

    try:
        user_preferences = user_preferences or {}

        # Step 1: Generate base route
        primary_waypoints = await get_base_route(
            start_lat, start_lon, end_lat, end_lon, mode
        )

        if not primary_waypoints:
            return []

        # Step 2: Query safety along route
        route_safety = await query_safety_along_route(primary_waypoints)

        # Step 3: Calculate segment risks
        segments_with_risk = []
        for waypoint in primary_waypoints:
            segment = {
                "waypoint": waypoint.dict(),
                "risk_score": await calculate_segment_risk(
                    route_safety.get(f"waypoint_{waypoint.order}", {})
                ),
            }
            segments_with_risk.append(segment)

        # Step 4: Apply user preferences
        adjusted_segments = await apply_user_preferences(
            segments_with_risk, user_preferences
        )

        # Step 5: Generate alternatives
        alternatives = await generate_alternative_routes(
            start_lat,
            start_lon,
            end_lat,
            end_lon,
            primary_waypoints,
        )

        # Create routes list with primary + alternatives
        all_routes = [primary_waypoints] + alternatives

        # Step 6: Rank routes
        ranked = await rank_routes_by_safety(all_routes, user_preferences)

        # Add start/end addresses to each route
        for route in ranked:
            route["start_latitude"] = start_lat
            route["start_longitude"] = start_lon
            route["start_address"] = start_address
            route["end_latitude"] = end_lat
            route["end_longitude"] = end_lon
            route["end_address"] = end_address
            route["mode"] = mode
            route["created_at"] = datetime.utcnow()

        db = await get_database()
        if ranked:
            await db["routes"].insert_many(
                [
                    {
                        **route,
                        "origin": {
                            "type": "Point",
                            "coordinates": [start_lon, start_lat],
                        },
                        "destination": {
                            "type": "Point",
                            "coordinates": [end_lon, end_lat],
                        },
                    }
                    for route in ranked
                ]
            )

        print(f"[ROUTE] Orchestration complete: {len(ranked)} routes")
        return ranked

    except Exception as e:
        print(f"[ROUTE] Error in orchestration: {e}")
        return []
