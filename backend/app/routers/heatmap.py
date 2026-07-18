"""API Router for heatmap and analytics (Agent 3)."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.agents.heatmap_agent import orchestrate_heatmap_generation
from app.utils.database import get_database, normalize_mongo_document
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/heatmap", tags=["heatmap"])


@router.get("/data")
async def get_heatmap_data(
    days_lookback: int = Query(30, ge=1, le=365),
    ward_id: Optional[str] = None,
    eps_meters: int = Query(500, ge=100, le=2000),
) -> dict:
    """
    Get safety heatmap data with clustered incidents.

    Orchestrates Agent 3: Safety Heatmap & Analytics Agent

    Args:
        days_lookback: Number of days to look back (default 30)
        ward_id: Optional ward filter
        eps_meters: DBSCAN epsilon in meters (default 500)

    Returns:
        Heatmap data with clusters and risk scores
    """
    try:
        print(
            f"[API] Heatmap request: lookback={days_lookback}d, ward={ward_id}, eps={eps_meters}m"
        )

        # Run Agent 3
        clusters = await orchestrate_heatmap_generation(
            days_lookback=days_lookback,
            ward_id=ward_id,
            eps_meters=eps_meters,
        )

        return {
            "status": "success",
            "generated_at": __import__("datetime").datetime.utcnow().isoformat(),
            "parameters": {
                "days_lookback": days_lookback,
                "ward_id": ward_id,
                "eps_meters": eps_meters,
            },
            "total_clusters": len(clusters),
            "clusters": clusters,
        }

    except Exception as e:
        print(f"[API] Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cluster/{cluster_id}")
async def get_cluster_details(cluster_id: str) -> dict:
    """
    Get detailed information about a specific cluster.

    Args:
        cluster_id: Cluster ID

    Returns:
        Cluster details with all incidents
    """
    try:
        db = await get_database()
        cluster = await db["safety_heatmaps"].find_one({"cluster_id": cluster_id})
        if cluster is None:
            raise HTTPException(status_code=404, detail="Cluster not found")
        return normalize_mongo_document(cluster) or {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/risk-distribution")
async def get_risk_distribution(
    days_lookback: int = Query(30, ge=1, le=365),
    ward_id: Optional[str] = None,
) -> dict:
    """
    Get risk distribution analytics.

    Args:
        days_lookback: Days to look back
        ward_id: Optional ward filter

    Returns:
        Risk distribution statistics
    """
    try:
        db = await get_database()
        since = datetime.utcnow() - timedelta(days=days_lookback)
        query = {"created_at": {"$gte": since}, "classification": {"$ne": None}}
        if ward_id:
            query["location.ward_id"] = ward_id

        distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        severity_values = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}
        total_score = 0.0
        total = 0
        async for complaint in db["complaints"].find(query):
            classification = complaint.get("classification", {})
            severity = classification.get("severity", "medium")
            distribution[severity] = distribution.get(severity, 0) + 1
            total_score += severity_values.get(severity, 0.4)
            total += 1

        return {
            "status": "success",
            "period_days": days_lookback,
            "ward_id": ward_id,
            "risk_distribution": distribution,
            "total_incidents": total,
            "average_risk_score": round(total_score / total, 3) if total else 0.0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/incident-types")
async def get_incident_type_distribution(
    days_lookback: int = Query(30, ge=1, le=365),
    ward_id: Optional[str] = None,
) -> dict:
    """
    Get distribution of incidents by type.

    Args:
        days_lookback: Days to look back
        ward_id: Optional ward filter

    Returns:
        Incident type distribution
    """
    try:
        db = await get_database()
        since = datetime.utcnow() - timedelta(days=days_lookback)
        query = {"created_at": {"$gte": since}, "classification": {"$ne": None}}
        if ward_id:
            query["location.ward_id"] = ward_id

        issue_types = {
            "pothole": 0,
            "water_leak": 0,
            "garbage": 0,
            "streetlight": 0,
            "traffic_signal": 0,
            "tree_hazard": 0,
            "drainage": 0,
            "public_safety": 0,
            "other": 0,
        }
        total = 0
        async for complaint in db["complaints"].find(query):
            issue_type = complaint.get("classification", {}).get("issue_type", "other")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            total += 1

        return {
            "status": "success",
            "period_days": days_lookback,
            "ward_id": ward_id,
            "incident_types": issue_types,
            "total_incidents": total,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/time-patterns")
async def get_time_patterns(
    days_lookback: int = Query(30, ge=1, le=365),
    ward_id: Optional[str] = None,
) -> dict:
    """
    Get time-based incident patterns.

    Args:
        days_lookback: Days to look back
        ward_id: Optional ward filter

    Returns:
        Time-based patterns (peak hours, etc)
    """
    try:
        db = await get_database()
        since = datetime.utcnow() - timedelta(days=days_lookback)
        query = {"created_at": {"$gte": since}, "classification": {"$ne": None}}
        if ward_id:
            query["location.ward_id"] = ward_id

        severity_values = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.2}
        buckets = {
            "morning": {"incident_count": 0, "severity_total": 0.0},
            "afternoon": {"incident_count": 0, "severity_total": 0.0},
            "evening": {"incident_count": 0, "severity_total": 0.0},
            "night": {"incident_count": 0, "severity_total": 0.0},
        }
        async for complaint in db["complaints"].find(query):
            created_at = complaint.get("created_at", datetime.utcnow())
            hour = created_at.hour
            period = (
                "morning"
                if 6 <= hour < 12
                else "afternoon"
                if 12 <= hour < 17
                else "evening"
                if 17 <= hour < 21
                else "night"
            )
            severity = complaint.get("classification", {}).get("severity", "medium")
            buckets[period]["incident_count"] += 1
            buckets[period]["severity_total"] += severity_values.get(severity, 0.4)

        patterns = {}
        for period, data in buckets.items():
            count = data["incident_count"]
            patterns[period] = {
                "incident_count": count,
                "average_severity": round(data["severity_total"] / count, 3) if count else 0.0,
            }
        peak_hour = max(patterns, key=lambda key: patterns[key]["incident_count"])
        if patterns[peak_hour]["incident_count"] == 0:
            peak_hour = None

        return {
            "status": "success",
            "period_days": days_lookback,
            "ward_id": ward_id,
            "patterns": patterns,
            "peak_hour": peak_hour,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
