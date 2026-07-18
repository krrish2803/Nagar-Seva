"""Geospatial utilities for distance calculations and coordinate operations."""

import math
from typing import List, Tuple, Dict, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in meters using haversine formula.

    Args:
        lat1: Starting latitude
        lon1: Starting longitude
        lat2: Ending latitude
        lon2: Ending longitude

    Returns:
        Distance in meters
    """
    earth_radius_meters = 6371000
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_meters * c


def calculate_cluster_center(
    points: List[Tuple[float, float]],
) -> Tuple[float, float]:
    """
    Calculate the geographic center of a list of coordinates.

    Args:
        points: List of (latitude, longitude) tuples

    Returns:
        Tuple of (center_latitude, center_longitude)
    """
    if not points:
        raise ValueError("Cannot calculate center of empty point list")

    lats = [p[0] for p in points]
    lons = [p[1] for p in points]

    return (sum(lats) / len(lats), sum(lons) / len(lons))


def get_points_within_radius(
    center_lat: float, center_lon: float, radius_meters: float, points: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter points within radius of center coordinate.

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_meters: Search radius in meters
        points: List of point dicts with 'latitude' and 'longitude'

    Returns:
        List of points within radius, sorted by distance
    """
    points_with_distance = []

    for point in points:
        dist = haversine_distance(
            center_lat, center_lon, point["latitude"], point["longitude"]
        )
        if dist <= radius_meters:
            point_copy = point.copy()
            point_copy["distance_meters"] = dist
            points_with_distance.append(point_copy)

    # Sort by distance
    points_with_distance.sort(key=lambda p: p["distance_meters"])
    return points_with_distance


def calculate_bearing(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate bearing from point 1 to point 2 in degrees (0-360).

    Args:
        lat1: Starting latitude
        lon1: Starting longitude
        lat2: Ending latitude
        lon2: Ending longitude

    Returns:
        Bearing in degrees (0=North, 90=East, 180=South, 270=West)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(
        lat2_rad
    ) * math.cos(dlon)

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def calculate_midpoint(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> Tuple[float, float]:
    """
    Calculate midpoint between two coordinates.

    Args:
        lat1: Starting latitude
        lon1: Starting longitude
        lat2: Ending latitude
        lon2: Ending longitude

    Returns:
        Tuple of (midpoint_latitude, midpoint_longitude)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)

    x = math.cos(lat2_rad) * math.cos(lon2_rad - lon1_rad)
    y = math.cos(lat2_rad) * math.sin(lon2_rad - lon1_rad)

    lat3 = math.atan2(
        math.sin(lat1_rad) + math.sin(lat2_rad),
        math.sqrt((math.cos(lat1_rad) + x) ** 2 + y**2),
    )
    lon3 = lon1_rad + math.atan2(y, math.cos(lat1_rad) + x)

    return (math.degrees(lat3), math.degrees(lon3))


def create_bounding_box(
    center_lat: float, center_lon: float, radius_meters: float
) -> Dict[str, float]:
    """
    Create a bounding box (approximate) around a center point.

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_meters: Radius in meters

    Returns:
        Dict with min/max latitude and longitude
    """
    # Rough approximation: 1 degree of latitude ≈ 111 km, 1 degree of longitude ≈ 111 km * cos(latitude)
    lat_offset = radius_meters / 111000  # Convert to degrees
    lon_offset = radius_meters / (111000 * math.cos(math.radians(center_lat)))

    return {
        "min_latitude": center_lat - lat_offset,
        "max_latitude": center_lat + lat_offset,
        "min_longitude": center_lon - lon_offset,
        "max_longitude": center_lon + lon_offset,
    }


def interpolate_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    num_waypoints: int = 10,
) -> List[Tuple[float, float]]:
    """
    Interpolate waypoints between two coordinates.

    Args:
        start_lat: Start latitude
        start_lon: Start longitude
        end_lat: End latitude
        end_lon: End longitude
        num_waypoints: Number of waypoints to generate (including start and end)

    Returns:
        List of (latitude, longitude) waypoints
    """
    waypoints = []
    for i in range(num_waypoints):
        fraction = i / (num_waypoints - 1) if num_waypoints > 1 else 0
        lat = start_lat + (end_lat - start_lat) * fraction
        lon = start_lon + (end_lon - start_lon) * fraction
        waypoints.append((lat, lon))

    return waypoints
