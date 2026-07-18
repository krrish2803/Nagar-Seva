"""API Router for complaint management (Agents 1 & 2)."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from app.agents.classification_agent import orchestrate_classification, orchestrate_voice_first_report
from app.agents.routing_agent import orchestrate_routing
from app.agents.trust_scoring_agent import score_complaint_trust
from app.models.complaint import Assignment, Complaint, ComplaintStatus, Location
from app.utils.storage import save_upload_file
from app.utils.database import get_database, normalize_mongo_document, to_mongo_document
from app.utils.nvidia_nim import generate_citizen_progress_update
import base64
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _public_complaint(document: dict) -> dict:
    """Return complaint document safe for API responses."""
    return normalize_mongo_document(document) or {}


def _coerce_datetime(value) -> Optional[datetime]:
    """Parse Mongo/API datetime values for SLA calculations."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
    return None


def _extract_sla_days(complaint: dict) -> int:
    """Get SLA days from assignment, classification, or fallback."""
    assignment = complaint.get("assignment") or {}
    classification = complaint.get("classification") or {}
    return int(
        assignment.get("sla_days")
        or classification.get("sla_days")
        or complaint.get("sla_days")
        or 7
    )


def _extract_photo_urls(complaint: dict) -> list[str]:
    """Return image attachment URLs for dashboard thumbnails."""
    photos = []
    for attachment in complaint.get("media_attachments", []) or []:
        if attachment.get("type") == "image" and attachment.get("url"):
            photos.append(attachment["url"])
    return photos


async def _build_dashboard_report(complaint: dict, escalations: list[dict]) -> dict:
    """Enrich one complaint with status, SLA, escalation, media, and AI update fields."""
    public_complaint = _public_complaint(complaint)
    created_at = _coerce_datetime(public_complaint.get("created_at")) or datetime.utcnow()
    sla_days = _extract_sla_days(public_complaint)
    due_at = created_at + timedelta(days=sla_days)
    now = datetime.utcnow()
    days_remaining = max(0, (due_at.date() - now.date()).days)
    status = str(public_complaint.get("status", "submitted"))
    is_resolved = status == ComplaintStatus.RESOLVED.value
    is_overdue = not is_resolved and now > due_at
    assignment = public_complaint.get("assignment") or {}
    classification = public_complaint.get("classification") or {}
    trust_score = public_complaint.get("trust_score") or {}
    public_escalations = [_public_complaint(escalation) for escalation in escalations]

    progress_context = {
        "complaint_id": public_complaint.get("_id") or public_complaint.get("id"),
        "issue_title": public_complaint.get("issue_title"),
        "status": status,
        "department": assignment.get("department") or classification.get("recommended_department"),
        "official_role": assignment.get("official_role") or assignment.get("official_name"),
        "sla_days": sla_days,
        "days_remaining": days_remaining,
        "is_overdue": is_overdue,
        "escalation_status": public_escalations[0].get("status") if public_escalations else None,
    }

    return {
        **public_complaint,
        "ai_progress_update": await generate_citizen_progress_update(progress_context),
        "dashboard_status": {
            "sla_days": sla_days,
            "due_at": due_at.isoformat(),
            "days_remaining": days_remaining,
            "is_overdue": is_overdue,
        },
        "photos": _extract_photo_urls(public_complaint),
        "escalation": {
            "is_escalated": bool(public_escalations) or is_overdue,
            "latest_status": public_escalations[0].get("status") if public_escalations else "not_escalated",
            "history": public_escalations,
        },
        "trust_summary": {
            "score": trust_score.get("overall_score", 0),
            "action": trust_score.get("recommended_action", "not_scored"),
            "flags": trust_score.get("evidence_flags", []),
            "otp_verified": trust_score.get("otp_verified", False),
        },
    }


class ReportComplaintRequest(BaseModel):
    """Request to submit a complaint."""

    citizen_id: str = Field(..., description="Submitting citizen ID")
    issue_title: str = Field(..., description="Brief issue title")
    issue_description: str = Field(..., description="Detailed description")
    latitude: float = Field(..., description="Latitude of issue location")
    longitude: float = Field(..., description="Longitude of issue location")
    address: str = Field(..., description="Human-readable address")
    ward_id: Optional[str] = Field(None, description="Ward ID (optional)")
    pin_code: Optional[str] = Field(None, description="PIN code (optional)")


class ComplaintResponse(BaseModel):
    """Response after complaint submission."""

    complaint_id: str
    status: str
    issue_type: str
    severity: str
    assigned_to_official_id: str
    sla_days: int
    trust_score: float
    trust_action: str
    evidence_flags: list[str]
    message: str


class VoiceComplaintResponse(ComplaintResponse):
    """Response after a voice-first complaint submission."""

    transcribed_text: str
    detected_language: str
    drafted_title: str
    drafted_description: str
    needs_human_review: bool


async def _process_media_uploads(
    image_file: Optional[UploadFile],
    audio_file: Optional[UploadFile],
) -> tuple[Optional[str], Optional[str], list]:
    """Save uploaded media and return image base64, audio path, and attachment metadata."""
    image_base64 = None
    audio_file_path = None
    media_attachments = []

    if image_file:
        image_content = await image_file.read()
        image_base64 = base64.b64encode(image_content).decode()
        image_path = await save_upload_file(
            image_content, image_file.filename or "image.jpg", "image"
        )
        media_attachments.append(
            {
                "type": "image",
                "url": image_path,
                "file_name": image_file.filename or "image.jpg",
                "size_bytes": len(image_content),
            }
        )

    if audio_file:
        audio_content = await audio_file.read()
        audio_file_path = await save_upload_file(
            audio_content, audio_file.filename or "audio.wav", "audio"
        )
        media_attachments.append(
            {
                "type": "audio",
                "url": audio_file_path,
                "file_name": audio_file.filename or "audio.wav",
                "size_bytes": len(audio_content),
            }
        )

    return image_base64, audio_file_path, media_attachments


async def _route_and_persist_complaint(
    complaint: Complaint,
    latitude: float,
    longitude: float,
    image_base64: Optional[str] = None,
    audio_file_path: Optional[str] = None,
    transcript: str = "",
    otp_verified: bool = False,
) -> tuple[Complaint, dict]:
    """Route complaint, persist it, and create its safety incident."""
    import uuid

    complaint.id = str(uuid.uuid4())
    routing_result = await orchestrate_routing(complaint)

    if "error" in routing_result:
        raise HTTPException(status_code=500, detail=routing_result["error"])

    complaint.trust_score = await score_complaint_trust(
        complaint,
        image_base64=image_base64,
        audio_file_path=audio_file_path,
        transcript=transcript,
        otp_verified=otp_verified,
    )
    complaint.status = ComplaintStatus.ASSIGNED
    complaint.assignment = Assignment(**routing_result["assignment"])

    db = await get_database()
    complaint_doc = to_mongo_document(complaint)
    complaint_doc["_id"] = complaint.id
    complaint_doc["status"] = ComplaintStatus.ASSIGNED.value
    complaint_doc["assignment"] = routing_result["assignment"]
    complaint_doc["location_point"] = {
        "type": "Point",
        "coordinates": [longitude, latitude],
    }
    complaint_doc["updated_at"] = datetime.utcnow()

    await db["complaints"].insert_one(complaint_doc)
    await db["citizens"].update_one(
        {"user_id": complaint.citizen_id},
        {
            "$inc": {"complaints_submitted": 1},
            "$set": {"updated_at": datetime.utcnow()},
        },
    )

    if complaint.classification:
        await db["safety_incidents"].insert_one(
            {
                "complaint_id": complaint.id,
                "incident_type": complaint.classification.issue_type,
                "latitude": latitude,
                "longitude": longitude,
                "location_point": {
                    "type": "Point",
                    "coordinates": [longitude, latitude],
                },
                "severity": complaint.classification.severity,
                "timestamp": complaint.created_at,
                "description": complaint.classification.description,
                "reported_by": complaint.citizen_id,
                "resolved": False,
                "metadata": {
                    "source": "voice_first"
                    if complaint.metadata.get("reporting_mode") == "voice_first"
                    else "complaint_report"
                },
            }
        )

    return complaint, routing_result


@router.post("/report", response_model=ComplaintResponse)
async def report_complaint(
    citizen_id: str = Form(...),
    issue_title: str = Form(...),
    issue_description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    ward_id: Optional[str] = Form(None),
    pin_code: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    audio_file: Optional[UploadFile] = File(None),
    otp_verified: bool = Form(False),
) -> ComplaintResponse:
    """
    Submit a new complaint with optional media attachments.

    This endpoint orchestrates:
    - Agent 1: Multimodal Issue Intelligence (classification)
    - Agent 2: Authority Router (assignment)

    Args:
        citizen_id: Submitting citizen ID
        issue_title: Brief issue title
        issue_description: Issue description
        latitude: Issue latitude
        longitude: Issue longitude
        address: Human-readable address
        ward_id: Optional ward ID
        pin_code: Optional PIN code
        image_file: Optional image file
        audio_file: Optional audio file

    Returns:
        Complaint response with assignment details
    """
    try:
        # Create location object
        location = Location(
            latitude=latitude,
            longitude=longitude,
            address=address,
            ward_id=ward_id,
            pin_code=pin_code,
        )

        image_base64, audio_file_path, media_attachments = await _process_media_uploads(
            image_file, audio_file
        )

        # Step 1: Run Agent 1 - Classification
        complaint = await orchestrate_classification(
            citizen_id=citizen_id,
            issue_title=issue_title,
            issue_description=issue_description,
            location=location,
            audio_file_path=audio_file_path,
            image_base64=image_base64,
            media_attachments=media_attachments,
        )

        complaint, routing_result = await _route_and_persist_complaint(
            complaint,
            latitude,
            longitude,
            image_base64=image_base64,
            audio_file_path=audio_file_path,
            otp_verified=otp_verified,
        )

        # Return response
        return ComplaintResponse(
            complaint_id=complaint.id,
            status=complaint.status,
            issue_type=complaint.classification.issue_type if complaint.classification else "unknown",
            severity=complaint.classification.severity if complaint.classification else "unknown",
            assigned_to_official_id=routing_result["official"]["official_id"],
            sla_days=routing_result["routing_rules"]["sla_days"],
            trust_score=complaint.trust_score.overall_score if complaint.trust_score else 0.0,
            trust_action=complaint.trust_score.recommended_action if complaint.trust_score else "manual_review",
            evidence_flags=complaint.trust_score.evidence_flags if complaint.trust_score else [],
            message=f"Complaint {complaint.id} successfully submitted and assigned",
        )

    except Exception as e:
        print(f"[API] Error in report_complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report/voice", response_model=VoiceComplaintResponse)
async def report_complaint_by_voice(
    citizen_id: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    ward_id: Optional[str] = Form(None),
    pin_code: Optional[str] = Form(None),
    language_hint: Optional[str] = Form(None),
    otp_verified: bool = Form(False),
    audio_file: UploadFile = File(...),
    image_file: Optional[UploadFile] = File(None),
) -> VoiceComplaintResponse:
    """
    Submit a voice-first complaint with required audio and optional photo.

    The agent transcribes the voice note, drafts a complaint, analyzes the photo,
    classifies the issue, routes it, and persists the final complaint.
    """
    try:
        location = Location(
            latitude=latitude,
            longitude=longitude,
            address=address,
            ward_id=ward_id,
            pin_code=pin_code,
        )
        image_base64, audio_file_path, media_attachments = await _process_media_uploads(
            image_file, audio_file
        )
        if not audio_file_path:
            raise HTTPException(status_code=400, detail="audio_file is required")

        complaint = await orchestrate_voice_first_report(
            citizen_id=citizen_id,
            location=location,
            audio_file_path=audio_file_path,
            image_base64=image_base64,
            media_attachments=media_attachments,
            user_language_hint=language_hint,
        )
        complaint, routing_result = await _route_and_persist_complaint(
            complaint,
            latitude,
            longitude,
            image_base64=image_base64,
            audio_file_path=audio_file_path,
            transcript=complaint.voice_draft.original_transcript if complaint.voice_draft else "",
            otp_verified=otp_verified,
        )
        voice_draft = complaint.voice_draft

        return VoiceComplaintResponse(
            complaint_id=complaint.id,
            status=complaint.status,
            issue_type=complaint.classification.issue_type if complaint.classification else "unknown",
            severity=complaint.classification.severity if complaint.classification else "unknown",
            assigned_to_official_id=routing_result["official"]["official_id"],
            sla_days=routing_result["routing_rules"]["sla_days"],
            trust_score=complaint.trust_score.overall_score if complaint.trust_score else 0.0,
            trust_action=complaint.trust_score.recommended_action if complaint.trust_score else "manual_review",
            evidence_flags=complaint.trust_score.evidence_flags if complaint.trust_score else [],
            message=f"Voice complaint {complaint.id} successfully drafted and assigned",
            transcribed_text=voice_draft.original_transcript if voice_draft else "",
            detected_language=voice_draft.detected_language if voice_draft else "unknown",
            drafted_title=voice_draft.drafted_title if voice_draft else complaint.issue_title,
            drafted_description=voice_draft.drafted_description if voice_draft else complaint.issue_description,
            needs_human_review=voice_draft.needs_human_review if voice_draft else False,
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error in report_complaint_by_voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_complaints(
    status: Optional[str] = None,
    ward_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
) -> dict:
    """
    List complaints with optional filters.

    Args:
        status: Filter by status
        ward_id: Filter by ward
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of complaints
    """
    try:
        db = await get_database()
        query = {}
        if status:
            query["status"] = status
        if ward_id:
            query["location.ward_id"] = ward_id

        total = await db["complaints"].count_documents(query)
        cursor = (
            db["complaints"]
            .find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        complaints = [_public_complaint(doc) async for doc in cursor]

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "complaints": complaints,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/citizen/{citizen_id}/dashboard")
async def get_citizen_dashboard(citizen_id: str, limit: int = 25) -> dict:
    """Return a personalized citizen dashboard with AI progress updates."""
    try:
        db = await get_database()
        query = {"citizen_id": citizen_id}
        bounded_limit = min(max(limit, 1), 100)
        cursor = (
            db["complaints"]
            .find(query)
            .sort("created_at", -1)
            .limit(bounded_limit)
        )
        complaint_documents = [_public_complaint(doc) async for doc in cursor]
        reports = []

        for complaint in complaint_documents:
            complaint_id = complaint.get("_id") or complaint.get("id")
            escalation_cursor = (
                db["escalations"]
                .find({"complaint_id": complaint_id})
                .sort("created_at", -1)
                .limit(10)
            )
            escalations = [_public_complaint(doc) async for doc in escalation_cursor]
            reports.append(await _build_dashboard_report(complaint, escalations))

        active_statuses = {
            ComplaintStatus.SUBMITTED.value,
            ComplaintStatus.CLASSIFIED.value,
            ComplaintStatus.ASSIGNED.value,
            ComplaintStatus.IN_PROGRESS.value,
        }
        resolved_reports = [
            report for report in reports if report.get("status") == ComplaintStatus.RESOLVED.value
        ]
        active_reports = [
            report for report in reports if report.get("status") in active_statuses
        ]
        escalated_reports = [
            report for report in reports if report.get("escalation", {}).get("is_escalated")
        ]

        return {
            "citizen_id": citizen_id,
            "total_reports": await db["complaints"].count_documents(query),
            "active_reports": len(active_reports),
            "resolved_reports": len(resolved_reports),
            "escalated_reports": len(escalated_reports),
            "reports": reports,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{complaint_id}")
async def get_complaint(complaint_id: str) -> dict:
    """
    Get complaint details by ID.

    Args:
        complaint_id: Complaint ID

    Returns:
        Complaint details
    """
    try:
        db = await get_database()
        complaint = await db["complaints"].find_one({"_id": complaint_id})
        if complaint is None:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return _public_complaint(complaint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{complaint_id}/trust")
async def get_complaint_trust_score(complaint_id: str) -> dict:
    """Get trust score details for a complaint."""
    try:
        db = await get_database()
        complaint = await db["complaints"].find_one(
            {"_id": complaint_id},
            {"trust_score": 1, "citizen_id": 1, "issue_title": 1},
        )
        if complaint is None:
            raise HTTPException(status_code=404, detail="Complaint not found")
        complaint = _public_complaint(complaint)
        return {
            "complaint_id": complaint_id,
            "citizen_id": complaint.get("citizen_id"),
            "issue_title": complaint.get("issue_title"),
            "trust_score": complaint.get("trust_score"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{complaint_id}/trust/rescore")
async def rescore_complaint_trust(
    complaint_id: str,
    otp_verified: bool = False,
) -> dict:
    """Recalculate trust score for an existing complaint."""
    try:
        db = await get_database()
        document = await db["complaints"].find_one({"_id": complaint_id})
        if document is None:
            raise HTTPException(status_code=404, detail="Complaint not found")

        normalized = _public_complaint(document)
        complaint = Complaint.model_validate(normalized)
        trust_score = await score_complaint_trust(
            complaint,
            transcript=complaint.voice_draft.original_transcript if complaint.voice_draft else "",
            otp_verified=otp_verified or (complaint.trust_score.otp_verified if complaint.trust_score else False),
        )
        await db["complaints"].update_one(
            {"_id": complaint_id},
            {
                "$set": {
                    "trust_score": trust_score.model_dump(mode="python"),
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        return {
            "complaint_id": complaint_id,
            "trust_score": trust_score.model_dump(mode="python"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{complaint_id}/trust/otp-verified")
async def mark_complaint_otp_verified(
    complaint_id: str,
    verified_by: str,
) -> dict:
    """Mark an existing complaint as OTP verified and recalculate trust."""
    try:
        db = await get_database()
        result = await db["complaints"].update_one(
            {"_id": complaint_id},
            {
                "$set": {
                    "trust_score.otp_verified": True,
                    "trust_score.scored_at": datetime.utcnow(),
                    "metadata.otp_verified_by": verified_by,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return await rescore_complaint_trust(complaint_id, otp_verified=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: str,
    new_status: str,
    update_note: str = "",
    updated_by: str = "",
) -> dict:
    """
    Update complaint status.

    Args:
        complaint_id: Complaint ID
        new_status: New status value
        update_note: Update note
        updated_by: User ID making update

    Returns:
        Updated complaint
    """
    try:
        db = await get_database()
        update = {
            "status": new_status,
            "updated_at": datetime.utcnow(),
        }
        update_entry = {
            "timestamp": datetime.utcnow(),
            "status": new_status,
            "message": update_note,
            "updated_by": updated_by,
        }

        if new_status == ComplaintStatus.RESOLVED.value:
            update["resolution_note"] = update_note
            update["resolved_at"] = datetime.utcnow()
            await db["safety_incidents"].update_many(
                {"complaint_id": complaint_id},
                {"$set": {"resolved": True}},
            )

        result = await db["complaints"].update_one(
            {"_id": complaint_id},
            {
                "$set": update,
                "$push": {"updates": update_entry},
            },
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Complaint not found")

        return {
            "complaint_id": complaint_id,
            "status": new_status,
            "message": "Status updated",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
