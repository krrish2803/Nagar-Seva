"""API Router for escalation management (Agent 5)."""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from app.agents.escalation_agent import orchestrate_escalation_check
from app.utils.database import get_database, normalize_mongo_document

router = APIRouter(prefix="/api/escalation", tags=["escalation"])


@router.get("/queue")
async def get_escalation_queue(
    include_history: bool = Query(False),
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=100),
) -> dict:
    """
    Get queue of escalation-pending complaints.

    Orchestrates Agent 5: Autonomous Escalation Agent

    Args:
        include_history: Include escalation history
        status: Filter by status (pending, acknowledged, resolved)
        limit: Maximum results to return

    Returns:
        Queue of escalation-pending complaints
    """
    try:
        print(f"[API] Escalation queue request: limit={limit}, status={status}")

        # Run Agent 5
        results = await orchestrate_escalation_check()

        return {
            "status": "success",
            "checked_at": results.get("checked_at"),
            "total_overdue": results.get("total_overdue", 0),
            "total_escalated": results.get("escalated", 0),
            "escalations": results.get("escalations", []),
            "errors": results.get("errors", []),
        }

    except Exception as e:
        print(f"[API] Error fetching escalation queue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-count")
async def get_pending_escalation_count() -> dict:
    """
    Get count of pending escalations.

    Returns:
        Count of pending escalations
    """
    try:
        db = await get_database()
        pending_count = await db["escalations"].count_documents({"status": "pending"})
        critical_count = await db["complaints"].count_documents(
            {"status": "escalated", "classification.severity": "critical"}
        )
        return {
            "pending_count": pending_count,
            "critical_count": critical_count,
            "queried_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual/{complaint_id}")
async def manually_escalate_complaint(
    complaint_id: str,
    escalation_level: int = Query(1, ge=1, le=3),
    reason: str = "",
) -> dict:
    """
    Manually escalate a complaint.

    Args:
        complaint_id: Complaint ID to escalate
        escalation_level: Level to escalate to (1-3)
        reason: Reason for escalation

    Returns:
        Escalation result
    """
    try:
        db = await get_database()
        complaint = await db["complaints"].find_one({"_id": complaint_id})
        if complaint is None:
            raise HTTPException(status_code=404, detail="Complaint not found")

        target = await db["officials"].find_one(
            {
                "account_status": "active",
                "authority_level": "commissioner" if escalation_level == 3 else "department_head" if escalation_level == 2 else "supervisor",
            }
        )
        if target is None:
            target = await db["officials"].find_one({"account_status": "active"})
        if target is None:
            raise HTTPException(status_code=404, detail="No active official available")

        target = normalize_mongo_document(target) or {}
        record = {
            "complaint_id": complaint_id,
            "escalation_level": escalation_level,
            "target_official_id": target["user_id"],
            "escalated_to_official_id": target["user_id"],
            "summary": reason or "Manual escalation requested",
            "escalated_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "pending",
            "manual": True,
        }
        await db["escalations"].insert_one(record)
        await db["complaints"].update_one(
            {"_id": complaint_id},
            {
                "$set": {"status": "escalated", "updated_at": datetime.utcnow()},
                "$push": {
                    "escalations": {
                        "level": escalation_level,
                        "escalated_at": datetime.utcnow(),
                        "escalated_to_official_id": target["user_id"],
                        "reason": reason or "Manual escalation requested",
                        "summary": reason or "Manual escalation requested",
                    }
                },
            },
        )
        return {
            "status": "success",
            "complaint_id": complaint_id,
            "escalation_level": escalation_level,
            "reason": reason,
            "target_official_id": target["user_id"],
            "escalated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{complaint_id}/status")
async def get_escalation_status(complaint_id: str) -> dict:
    """
    Get escalation status for a complaint.

    Args:
        complaint_id: Complaint ID

    Returns:
        Escalation status and history
    """
    try:
        db = await get_database()
        cursor = db["escalations"].find({"complaint_id": complaint_id}).sort("created_at", -1)
        records = [normalize_mongo_document(record) async for record in cursor]
        if not records:
            return {
                "complaint_id": complaint_id,
                "is_escalated": False,
                "current_level": 0,
                "escalation_history": [],
            }

        return {
            "complaint_id": complaint_id,
            "is_escalated": True,
            "current_level": max(record.get("escalation_level", 0) for record in records),
            "escalation_history": records,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{complaint_id}/acknowledge")
async def acknowledge_escalation(
    complaint_id: str,
    official_id: str = Query(...),
) -> dict:
    """
    Acknowledge receipt of escalation.

    Args:
        complaint_id: Complaint ID
        official_id: Official acknowledging escalation

    Returns:
        Acknowledgment result
    """
    try:
        db = await get_database()
        result = await db["escalations"].update_one(
            {
                "complaint_id": complaint_id,
                "target_official_id": official_id,
                "status": "pending",
            },
            {
                "$set": {
                    "status": "acknowledged",
                    "acknowledged_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pending escalation not found")

        return {
            "status": "success",
            "complaint_id": complaint_id,
            "acknowledged_by": official_id,
            "acknowledged_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/escalation-rate")
async def get_escalation_rate(
    days_lookback: int = Query(30, ge=1, le=365),
) -> dict:
    """
    Get escalation rate analytics.

    Args:
        days_lookback: Days to analyze

    Returns:
        Escalation statistics
    """
    try:
        db = await get_database()
        since = datetime.utcnow() - timedelta(days=days_lookback)
        total_complaints = await db["complaints"].count_documents({"created_at": {"$gte": since}})
        total_escalated = await db["escalations"].count_documents({"created_at": {"$gte": since}})
        levels = {"level_1": 0, "level_2": 0, "level_3": 0}
        async for record in db["escalations"].find({"created_at": {"$gte": since}}):
            level = record.get("escalation_level", 1)
            levels[f"level_{level}"] = levels.get(f"level_{level}", 0) + 1

        return {
            "status": "success",
            "period_days": days_lookback,
            "total_complaints": total_complaints,
            "total_escalated": total_escalated,
            "escalation_rate_percent": round((total_escalated / total_complaints) * 100, 2)
            if total_complaints
            else 0.0,
            "average_days_to_escalation": 0.0,
            "escalation_levels": levels,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
