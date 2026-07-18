"""Agent 3: Safety Heatmap & Analytics Agent."""

import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
from app.models.complaint import Complaint
from app.models.safety import SafetyCluster, ClusterPoint, TimeWindow
from app.utils.geospatial import haversine_distance, calculate_cluster_center
from app.utils.database import get_database, normalize_mongo_document


async def fetch_complaints_for_clustering(
    days_lookback: int = 30,
    ward_id: str = None,
) -> List[Dict[str, Any]]:
    """
    Fetch complaints for clustering from database.

    Args:
        days_lookback: Number of days to look back
        ward_id: Optional ward filter

    Returns:
        List of complaint data for clustering
    """
    try:
        db = await get_database()
        since = datetime.utcnow() - timedelta(days=days_lookback)
        query: Dict[str, Any] = {
            "created_at": {"$gte": since},
            "status": {"$ne": "resolved"},
            "classification": {"$ne": None},
        }
        if ward_id:
            query["location.ward_id"] = ward_id

        cursor = db["complaints"].find(query)
        complaints = []
        async for document in cursor:
            complaint = normalize_mongo_document(document) or {}
            location = complaint.get("location", {})
            classification = complaint.get("classification", {})
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            if latitude is None or longitude is None:
                continue

            complaints.append(
                {
                    "id": complaint.get("_id"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "severity": classification.get("severity", "medium"),
                    "timestamp": complaint.get("created_at", datetime.utcnow()),
                    "issue_type": classification.get("issue_type", "other"),
                    "ward_id": location.get("ward_id"),
                }
            )

        print(f"[HEATMAP] Fetched {len(complaints)} complaints for clustering")
        return complaints
    except Exception as e:
        print(f"[HEATMAP] Error fetching complaints: {e}")
        return []


async def cluster_complaints_geospatial(
    complaints: List[Dict[str, Any]],
    eps_meters: int = 500,
) -> Tuple[np.ndarray, List[List[Dict[str, Any]]]]:
    """
    Cluster complaints using DBSCAN geospatial clustering.

    Args:
        complaints: List of complaint data
        eps_meters: DBSCAN epsilon in meters

    Returns:
        Tuple of (cluster_labels, clustered_complaints)
    """
    try:
        if not complaints:
            return np.array([]), []

        # Convert to radians for earth's surface distance calculation
        coords = np.array(
            [[c["latitude"], c["longitude"]] for c in complaints]
        )
        coords_rad = np.radians(coords)

        # Earth's radius in meters
        earth_radius = 6371000

        # DBSCAN clustering with haversine metric
        # eps in meters needs to be converted to radians
        eps_rad = eps_meters / earth_radius

        db = DBSCAN(eps=eps_rad, min_samples=1, metric="haversine")
        labels = db.fit_predict(coords_rad)

        # Group complaints by cluster
        clustered = {}
        for idx, complaint in enumerate(complaints):
            label = labels[idx]
            if label not in clustered:
                clustered[label] = []
            clustered[label].append(complaint)

        clusters_list = [clustered[i] for i in sorted(clustered.keys())]

        print(
            f"[HEATMAP] Clustered {len(complaints)} complaints into {len(clusters_list)} clusters"
        )
        return labels, clusters_list
    except Exception as e:
        print(f"[HEATMAP] Error clustering: {e}")
        return np.array([]), []


async def calculate_cluster_risk_score(
    cluster_complaints: List[Dict[str, Any]],
    ward_data: Dict[str, Any] = None,
) -> float:
    """
    Calculate risk score for a cluster.

    Args:
        cluster_complaints: List of complaints in cluster
        ward_data: Optional ward metadata

    Returns:
        Risk score (0-1)
    """
    try:
        if not cluster_complaints:
            return 0.0

        # Calculate risk based on severity and density
        severity_weights = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}

        total_risk = 0.0
        for complaint in cluster_complaints:
            severity = complaint.get("severity", "medium")
            weight = severity_weights.get(severity, 0.5)
            total_risk += weight

        # Normalize by cluster size and add density factor
        density_factor = min(1.0, len(cluster_complaints) / 10)
        risk_score = min(
            1.0, (total_risk / len(cluster_complaints)) * (1 + density_factor * 0.5)
        )

        print(f"[HEATMAP] Cluster risk score: {risk_score:.2f}")
        return risk_score
    except Exception as e:
        print(f"[HEATMAP] Error calculating risk score: {e}")
        return 0.5


async def extract_time_aware_risks(
    cluster_complaints: List[Dict[str, Any]],
) -> List[TimeWindow]:
    """
    Extract time-aware risk patterns from cluster.

    Args:
        cluster_complaints: List of complaints in cluster

    Returns:
        List of TimeWindow objects with time analysis
    """
    try:
        # Categorize by time periods
        time_periods = {
            "morning": {"hours": range(6, 12), "incidents": [], "severity": 0},
            "afternoon": {"hours": range(12, 17), "incidents": [], "severity": 0},
            "evening": {"hours": range(17, 21), "incidents": [], "severity": 0},
            "night": {"hours": range(21, 6), "incidents": [], "severity": 0},
        }

        severity_values = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}

        # Bin complaints by time
        for complaint in cluster_complaints:
            timestamp = complaint.get("timestamp", datetime.utcnow())
            hour = timestamp.hour
            severity = complaint.get("severity", "medium")
            sev_val = severity_values.get(severity, 0.5)

            for period, data in time_periods.items():
                if period == "night":
                    if hour >= 21 or hour < 6:
                        data["incidents"].append(complaint)
                        data["severity"] += sev_val
                elif hour in data["hours"]:
                    data["incidents"].append(complaint)
                    data["severity"] += sev_val

        # Create TimeWindow objects
        time_windows = []
        for period, data in time_periods.items():
            if data["incidents"]:
                avg_severity = data["severity"] / len(data["incidents"])
                peak_hours = [
                    dt.hour
                    for dt in [c["timestamp"] for c in data["incidents"]]
                ]
                time_windows.append(
                    TimeWindow(
                        period=period,
                        incident_count=len(data["incidents"]),
                        average_severity=avg_severity,
                        peak_hours=peak_hours,
                    )
                )

        print(f"[HEATMAP] Extracted {len(time_windows)} time windows")
        return time_windows
    except Exception as e:
        print(f"[HEATMAP] Error extracting time patterns: {e}")
        return []


async def store_cluster_in_db(
    cluster_id: str,
    cluster_complaints: List[Dict[str, Any]],
    risk_score: float,
    time_windows: List[TimeWindow],
) -> Dict[str, Any]:
    """
    Store cluster in database.

    Args:
        cluster_id: Unique cluster ID
        cluster_complaints: Complaints in cluster
        risk_score: Calculated risk score
        time_windows: Time window analysis

    Returns:
        Stored cluster data
    """
    try:
        # Calculate cluster center
        coords = [(c["latitude"], c["longitude"]) for c in cluster_complaints]
        center_lat, center_lon = calculate_cluster_center(coords)

        # Calculate cluster radius (max distance from center)
        max_dist = 0
        for lat, lon in coords:
            dist = haversine_distance(center_lat, center_lon, lat, lon)
            max_dist = max(max_dist, dist)

        # Count by issue type and severity
        issue_types = {}
        severity_dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for complaint in cluster_complaints:
            issue = complaint.get("issue_type", "other")
            issue_types[issue] = issue_types.get(issue, 0) + 1
            sev = complaint.get("severity", "medium")
            severity_dist[sev] = severity_dist.get(sev, 0) + 1

        # Determine risk level
        if risk_score >= 0.8:
            risk_level = "critical"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Create cluster data
        cluster_data = {
            "cluster_id": cluster_id,
            "center_latitude": center_lat,
            "center_longitude": center_lon,
            "radius_meters": max_dist,
            "point_count": len(cluster_complaints),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "incident_types": issue_types,
            "severity_distribution": severity_dist,
            "time_analysis": [tw.dict() for tw in time_windows],
            "first_incident_at": min(
                c["timestamp"] for c in cluster_complaints
            ),
            "last_incident_at": max(
                c["timestamp"] for c in cluster_complaints
            ),
            "stored_at": datetime.utcnow().isoformat(),
        }

        db = await get_database()
        await db["safety_heatmaps"].update_one(
            {"cluster_id": cluster_id},
            {
                "$set": {
                    **cluster_data,
                    "cluster_center": {
                        "type": "Point",
                        "coordinates": [center_lon, center_lat],
                    },
                    "generated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )

        print(f"[HEATMAP] Stored cluster {cluster_id} with risk score {risk_score:.2f}")
        return cluster_data
    except Exception as e:
        print(f"[HEATMAP] Error storing cluster: {e}")
        return {"error": str(e)}


async def orchestrate_heatmap_generation(
    days_lookback: int = 30,
    ward_id: str = None,
    eps_meters: int = 500,
) -> List[Dict[str, Any]]:
    """
    Orchestrate complete heatmap generation pipeline.

    Args:
        days_lookback: Days to look back
        ward_id: Optional ward filter
        eps_meters: DBSCAN epsilon in meters

    Returns:
        List of cluster data
    """
    print(
        f"[HEATMAP] Starting heatmap generation: lookback={days_lookback}, ward={ward_id}"
    )

    try:
        # Step 1: Fetch complaints
        complaints = await fetch_complaints_for_clustering(days_lookback, ward_id)

        if not complaints:
            print("[HEATMAP] No complaints found")
            return []

        # Step 2: Cluster complaints
        labels, clusters = await cluster_complaints_geospatial(
            complaints, eps_meters
        )

        # Step 3-5: Process each cluster
        cluster_data = []
        for idx, cluster in enumerate(clusters):
            # Calculate risk score
            risk_score = await calculate_cluster_risk_score(cluster)

            # Extract time patterns
            time_windows = await extract_time_aware_risks(cluster)

            # Store in DB
            stored = await store_cluster_in_db(
                f"cluster_{idx}",
                cluster,
                risk_score,
                time_windows,
            )
            cluster_data.append(stored)

        print(f"[HEATMAP] Generated {len(cluster_data)} heatmap clusters")
        return cluster_data

    except Exception as e:
        print(f"[HEATMAP] Error in orchestration: {e}")
        return []
