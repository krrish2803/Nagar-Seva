"""Agent 2: Authority Router Agent."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.complaint import Complaint, Assignment, ComplaintStatus
from app.utils.notifications import send_assignment_notification
from app.utils.database import get_database, normalize_mongo_document


def _as_value(value: Any) -> str:
    """Return enum values or strings as plain strings."""
    return getattr(value, "value", value)


async def extract_routing_params(complaint: Complaint) -> Dict[str, Any]:
    """
    Extract routing parameters from complaint.

    Args:
        complaint: Complaint object

    Returns:
        Routing parameters
    """
    try:
        params = {
            "complaint_id": str(complaint.id),
            "issue_type": _as_value(complaint.classification.issue_type)
            if complaint.classification
            else "other",
            "severity": _as_value(complaint.classification.severity)
            if complaint.classification
            else "medium",
            "location": complaint.location.dict(),
            "ward_id": complaint.location.ward_id,
            "citizen_id": complaint.citizen_id,
        }
        print(f"[ROUTING] Extracted params for {complaint.id}: {params}")
        return params
    except Exception as e:
        print(f"[ROUTING] Error extracting routing params: {e}")
        return {}


async def determine_routing_rules(
    issue_type: str, severity: str
) -> Dict[str, Any]:
    """
    Determine routing rules based on issue type and severity.

    Args:
        issue_type: Type of issue
        severity: Severity level

    Returns:
        Routing rules
    """
    # Define routing rules
    routing_rules = {
        "pothole": {
            "department": "Public_Works",
            "escalation_levels": ["field_staff", "supervisor", "commissioner"],
        },
        "water_leak": {
            "department": "Water_Supply",
            "escalation_levels": ["technician", "supervisor", "commissioner"],
        },
        "garbage": {
            "department": "Sanitation",
            "escalation_levels": ["worker", "supervisor", "commissioner"],
        },
        "streetlight": {
            "department": "Utilities",
            "escalation_levels": ["technician", "supervisor", "commissioner"],
        },
        "traffic_signal": {
            "department": "Traffic_Management",
            "escalation_levels": ["technician", "supervisor", "commissioner"],
        },
        "tree_hazard": {
            "department": "Parks_Horticulture",
            "escalation_levels": ["worker", "supervisor", "commissioner"],
        },
        "drainage": {
            "department": "Engineering",
            "escalation_levels": ["technician", "supervisor", "commissioner"],
        },
        "public_safety": {
            "department": "Police",
            "escalation_levels": ["patrol", "supervisor", "commissioner"],
        },
        "other": {
            "department": "General_Services",
            "escalation_levels": ["staff", "supervisor", "commissioner"],
        },
    }

    # SLA days based on severity
    sla_mapping = {
        "critical": 2,
        "high": 5,
        "medium": 7,
        "low": 14,
    }

    rules = routing_rules.get(issue_type, routing_rules["other"])
    rules["sla_days"] = sla_mapping.get(severity, 7)
    rules["priority"] = severity

    print(f"[ROUTING] Rules for {issue_type}/{severity}: {rules}")
    return rules


async def find_responsible_official(
    ward_id: Optional[str], department: str
) -> Dict[str, Any]:
    """
    Find responsible official for department/ward combination.

    Args:
        ward_id: Ward ID (optional)
        department: Department name

    Returns:
        Official information
    """
    try:
        db = await get_database()
        base_filter = {
            "department": department,
            "account_status": "active",
            "availability_status": {"$in": ["available", "busy"]},
        }

        ward_filter = {**base_filter}
        if ward_id:
            ward_filter["ward_id"] = {"$in": [ward_id, "all"]}

        official = await db["officials"].find_one(
            ward_filter,
            sort=[("complaints_assigned", 1), ("performance_rating", -1)],
        )

        if official is None:
            official = await db["officials"].find_one(
                base_filter,
                sort=[("complaints_assigned", 1), ("performance_rating", -1)],
            )

        if official is None:
            now = datetime.utcnow()
            fallback = {
                "user_id": f"OFF_{department.upper()}_DEFAULT",
                "name": f"{department.replace('_', ' ')} Officer",
                "email": f"default-{department.lower()}@municipal.local",
                "phone": "+91-1234567890",
                "user_type": "official",
                "designation": f"{department.replace('_', ' ')} Officer",
                "department": department,
                "ward_id": ward_id or "all",
                "authority_level": "field_staff",
                "office_address": "Municipal Office",
                "office_latitude": 0.0,
                "office_longitude": 0.0,
                "verified": True,
                "account_status": "active",
                "complaints_assigned": 0,
                "complaints_resolved": 0,
                "average_resolution_days": 0,
                "performance_rating": 0,
                "escalations_received": 0,
                "escalations_handled": 0,
                "availability_status": "available",
                "shift_start_hour": 9,
                "shift_end_hour": 17,
                "response_time_minutes": 60,
                "specializations": [],
                "team_members": [],
                "notification_preferences": {"email": True, "sms": False},
                "metadata": {"auto_created": True},
                "created_at": now,
                "updated_at": now,
            }
            await db["officials"].update_one(
                {"email": fallback["email"]},
                {"$setOnInsert": fallback},
                upsert=True,
            )
            official = await db["officials"].find_one({"email": fallback["email"]})

        normalized = normalize_mongo_document(official) or {}
        normalized["official_id"] = normalized.get("user_id")
        print(f"[ROUTING] Found official for {ward_id}/{department}: {normalized.get('name')}")
        return normalized
    except Exception as e:
        print(f"[ROUTING] Error finding official: {e}")
        return {}


async def assign_complaint_to_official(
    complaint_id: str,
    official_id: str,
    department: str,
    sla_days: int,
) -> Assignment:
    """
    Create assignment record for complaint.

    Args:
        complaint_id: Complaint ID
        official_id: Official ID
        department: Department name
        sla_days: Service level agreement days

    Returns:
        Assignment object
    """
    try:
        assignment = Assignment(
            official_id=official_id,
            department=department,
            sla_days=sla_days,
            expected_resolution=datetime.utcnow() + timedelta(days=sla_days),
        )
        db = await get_database()
        await db["officials"].update_one(
            {"user_id": official_id},
            {
                "$inc": {"complaints_assigned": 1},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )
        print(
            f"[ROUTING] Assigned complaint {complaint_id} to {official_id} in {department}"
        )
        return assignment
    except Exception as e:
        print(f"[ROUTING] Error creating assignment: {e}")
        raise


async def notify_official_assignment(
    official_data: Dict[str, Any],
    complaint: Complaint,
) -> bool:
    """
    Notify official about assignment.

    Args:
        official_data: Official information
        complaint: Complaint object

    Returns:
        True if notification sent successfully
    """
    try:
        success = await send_assignment_notification(
            official_email=official_data.get("email", ""),
            official_name=official_data.get("name", ""),
            complaint_id=str(complaint.id),
            issue_title=complaint.issue_title,
            location=complaint.location.address,
        )
        print(
            f"[ROUTING] Notified {official_data.get('name')} about assignment"
        )
        return success
    except Exception as e:
        print(f"[ROUTING] Error notifying official: {e}")
        return False


async def orchestrate_routing(
    complaint: Complaint,
) -> Dict[str, Any]:
    """
    Orchestrate complete routing pipeline.

    Args:
        complaint: Complaint object

    Returns:
        Routing result with assignment
    """
    print(f"[ROUTING] Starting orchestration for complaint {complaint.id}")

    try:
        # Step 1: Extract routing parameters
        params = await extract_routing_params(complaint)

        # Step 2: Determine routing rules
        rules = await determine_routing_rules(
            params.get("issue_type"),
            params.get("severity"),
        )

        # Step 3: Find responsible official
        official = await find_responsible_official(
            params.get("ward_id"),
            rules.get("department"),
        )

        # Step 4: Create assignment
        assignment = await assign_complaint_to_official(
            str(complaint.id),
            official.get("official_id"),
            rules.get("department"),
            rules.get("sla_days"),
        )

        # Step 5: Notify official
        notification_sent = await notify_official_assignment(official, complaint)

        result = {
            "complaint_id": str(complaint.id),
            "status": "assigned",
            "assignment": assignment.dict(),
            "official": official,
            "routing_rules": rules,
            "notification_sent": notification_sent,
        }

        print(f"[ROUTING] Orchestration complete for {complaint.id}")
        return result

    except Exception as e:
        print(f"[ROUTING] Error in orchestration: {e}")
        return {"error": str(e), "complaint_id": str(complaint.id)}
