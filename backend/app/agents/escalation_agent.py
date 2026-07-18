"""Agent 5: Autonomous Escalation Agent."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.complaint import Complaint, ComplaintStatus
from app.models.escalation import EscalationRecord, EscalationLevel
from app.utils.notifications import send_escalation_notification
from app.utils.nvidia_nim import generate_escalation_summary
from app.utils.database import get_database, normalize_mongo_document


async def fetch_overdue_complaints(
    overdue_days: int = 7,
) -> List[Dict[str, Any]]:
    """
    Fetch complaints that have exceeded SLA.

    Args:
        overdue_days: Days overdue threshold

    Returns:
        List of overdue complaints
    """
    try:
        db = await get_database()
        now = datetime.utcnow()
        cursor = db["complaints"].find(
            {
                "status": {"$in": ["assigned", "in_progress", "escalated"]},
                "assignment.expected_resolution": {"$lt": now},
            }
        )

        overdue = []
        async for document in cursor:
            complaint = normalize_mongo_document(document) or {}
            assignment = complaint.get("assignment", {})
            assigned_at = assignment.get("assigned_at", complaint.get("created_at", now))
            sla_days = assignment.get("sla_days", overdue_days)
            overdue.append(
                {
                    "id": complaint.get("_id"),
                    "citizen_id": complaint.get("citizen_id"),
                    "issue_title": complaint.get("issue_title"),
                    "status": complaint.get("status"),
                    "assigned_official_id": assignment.get("official_id"),
                    "assigned_at": assigned_at,
                    "sla_days": sla_days,
                    "location": complaint.get("location", {}),
                    "classification": complaint.get("classification", {}),
                    "updates": complaint.get("updates", []),
                }
            )

        print(f"[ESCALATION] Found {len(overdue)} overdue complaints")
        return overdue
    except Exception as e:
        print(f"[ESCALATION] Error fetching overdue complaints: {e}")
        return []


async def check_resolution_progress(
    complaint: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Check progress on resolving a complaint.

    Args:
        complaint: Complaint data

    Returns:
        Progress status information
    """
    try:
        assigned_at = complaint.get("assigned_at", datetime.utcnow())
        sla_days = complaint.get("sla_days", 7)
        days_since_assignment = (datetime.utcnow() - assigned_at).days

        progress = {
            "complaint_id": complaint.get("id"),
            "days_since_assignment": days_since_assignment,
            "sla_days": sla_days,
            "days_overdue": max(0, days_since_assignment - sla_days),
            "status": complaint.get("status"),
            "progress_percentage": min(
                100, (days_since_assignment / sla_days) * 100
            ),
            "has_updates": bool(complaint.get("updates")),
            "last_update_days_ago": max(
                0,
                (
                    datetime.utcnow()
                    - complaint["updates"][-1].get("timestamp", assigned_at)
                ).days,
            )
            if complaint.get("updates")
            else days_since_assignment,
        }

        print(f"[ESCALATION] Progress check: {progress['progress_percentage']:.0f}%")
        return progress
    except Exception as e:
        print(f"[ESCALATION] Error checking progress: {e}")
        return {}


async def generate_escalation_summary_text(
    complaint: Dict[str, Any],
    progress: Dict[str, Any],
) -> str:
    """
    Generate escalation summary using NVIDIA LLM.

    Args:
        complaint: Complaint data
        progress: Progress data

    Returns:
        Escalation summary text
    """
    try:
        summary = await generate_escalation_summary(complaint, progress)
        print(f"[ESCALATION] Generated escalation summary")
        return summary
    except Exception as e:
        print(f"[ESCALATION] Error generating summary: {e}")
        return f"Complaint {complaint.get('id')} has exceeded SLA and requires escalation."


async def escalate_to_higher_authority(
    complaint: Dict[str, Any],
    escalation_level: int = 1,
) -> EscalationRecord:
    """
    Escalate complaint to higher authority.

    Args:
        complaint: Complaint data
        escalation_level: Level to escalate to (1=supervisor, 2=head, 3=commissioner)

    Returns:
        Escalation record
    """
    try:
        db = await get_database()
        level_names = {1: "supervisor", 2: "department_head", 3: "commissioner"}
        level_name = level_names.get(escalation_level, "supervisor")
        department = complaint.get("classification", {}).get("recommended_department")

        query: Dict[str, Any] = {
            "account_status": "active",
            "authority_level": level_name,
        }
        if department and escalation_level < 3:
            query["department"] = department

        target = await db["officials"].find_one(query, sort=[("escalations_received", 1)])
        if target is None:
            target = await db["officials"].find_one(
                {"authority_level": "commissioner", "account_status": "active"}
            )
        if target is None:
            target = await db["officials"].find_one({"account_status": "active"})

        if target is None:
            raise ValueError("No active official available for escalation")

        target = normalize_mongo_document(target) or {}

        escalation_record = EscalationRecord(
            complaint_id=complaint.get("id"),
            citizen_id=complaint.get("citizen_id"),
            original_assignment_official_id=complaint.get("assigned_official_id"),
            initial_escalation_at=datetime.utcnow(),
            escalation_reason=f"Complaint exceeded SLA of {complaint.get('sla_days', 7)} days",
            current_level=escalation_level,
        )

        # Add escalation level
        escalation_record.escalation_history.append(
            EscalationLevel(
                level_number=escalation_level,
                level_name=level_name,
                target_official_id=target["user_id"],
                escalated_at=datetime.utcnow(),
            )
        )

        await db["officials"].update_one(
            {"user_id": target["user_id"]},
            {"$inc": {"escalations_received": 1}, "$set": {"updated_at": datetime.utcnow()}},
        )

        print(f"[ESCALATION] Escalated to level {escalation_level}")
        return escalation_record
    except Exception as e:
        print(f"[ESCALATION] Error escalating: {e}")
        raise


async def send_escalation_notifications(
    complaint: Dict[str, Any],
    summary: str,
    target_official_id: str,
    escalation_level: int,
) -> bool:
    """
    Send notifications about escalation.

    Args:
        complaint: Complaint data
        summary: Escalation summary
        target_official_id: Target official ID
        escalation_level: Escalation level

    Returns:
        True if notifications sent
    """
    try:
        db = await get_database()
        official = await db["officials"].find_one({"user_id": target_official_id})
        official = normalize_mongo_document(official) or {
            "email": "official@municipal.local",
            "name": "Official",
        }

        level_names = ["", "Ward Supervisor", "Department Head", "Commissioner"]

        # Send to escalated official
        await send_escalation_notification(
            official_email=official["email"],
            official_name=official["name"],
            complaint_id=complaint.get("id"),
            reason=f"Exceeded SLA of {complaint.get('sla_days', 7)} days",
            escalation_level=level_names[escalation_level],
        )

        print(f"[ESCALATION] Sent notifications to {official['name']}")
        return True
    except Exception as e:
        print(f"[ESCALATION] Error sending notifications: {e}")
        return False


async def record_escalation_in_db(
    complaint_id: str,
    escalation_level: int,
    target_official_id: str,
    summary: str,
) -> Dict[str, Any]:
    """
    Record escalation in database.

    Args:
        complaint_id: Complaint ID
        escalation_level: Escalation level
        target_official_id: Target official ID
        summary: Escalation summary

    Returns:
        Recorded escalation data
    """
    try:
        db = await get_database()
        record = {
            "complaint_id": complaint_id,
            "escalation_level": escalation_level,
            "target_official_id": target_official_id,
            "escalated_to_official_id": target_official_id,
            "summary": summary,
            "escalated_at": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "pending",
        }

        await db["escalations"].insert_one(record)
        await db["complaints"].update_one(
            {"_id": complaint_id},
            {
                "$set": {
                    "status": "escalated",
                    "updated_at": datetime.utcnow(),
                },
                "$push": {
                    "escalations": {
                        "level": escalation_level,
                        "escalated_at": datetime.utcnow(),
                        "escalated_to_official_id": target_official_id,
                        "reason": "SLA exceeded",
                        "summary": summary,
                    }
                },
            },
        )

        print(f"[ESCALATION] Recorded escalation for {complaint_id}")
        return record
    except Exception as e:
        print(f"[ESCALATION] Error recording escalation: {e}")
        return {"error": str(e)}


async def orchestrate_escalation_check() -> Dict[str, Any]:
    """
    Orchestrate complete escalation check and processing.

    Returns:
        Results of escalation processing
    """
    print("[ESCALATION] Starting escalation check orchestration")

    try:
        results = {
            "checked_at": datetime.utcnow().isoformat(),
            "total_overdue": 0,
            "escalated": 0,
            "escalations": [],
            "errors": [],
        }

        # Step 1: Fetch overdue complaints
        overdue = await fetch_overdue_complaints()
        results["total_overdue"] = len(overdue)

        for complaint in overdue:
            try:
                # Step 2: Check progress
                progress = await check_resolution_progress(complaint)

                # Step 3: Generate summary
                summary = await generate_escalation_summary_text(complaint, progress)

                # Step 4: Escalate
                escalation = await escalate_to_higher_authority(complaint, escalation_level=1)

                # Step 5: Notify
                await send_escalation_notifications(
                    complaint,
                    summary,
                    escalation.escalation_history[0].target_official_id,
                    1,
                )

                # Step 6: Record
                record = await record_escalation_in_db(
                    complaint.get("id"),
                    1,
                    escalation.escalation_history[0].target_official_id,
                    summary,
                )

                results["escalations"].append(record)
                results["escalated"] += 1

            except Exception as e:
                results["errors"].append(
                    {
                        "complaint_id": complaint.get("id"),
                        "error": str(e),
                    }
                )

        print(
            f"[ESCALATION] Orchestration complete: "
            f"escalated {results['escalated']}/{results['total_overdue']}"
        )
        return results

    except Exception as e:
        print(f"[ESCALATION] Error in orchestration: {e}")
        return {"error": str(e), "checked_at": datetime.utcnow().isoformat()}
