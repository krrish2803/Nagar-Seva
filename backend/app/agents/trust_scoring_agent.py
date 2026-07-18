"""AI Trust Scoring and Complaint Verification Agent."""

from typing import Any, Dict, Optional

from app.models.complaint import Complaint, TrustScore
from app.utils.database import get_database, normalize_mongo_document
from app.utils.nvidia_nim import generate_trust_score_analysis


def _score_to_action(score: float, flags: list[str], otp_verified: bool) -> str:
    """Map final score and flags to an operational action."""
    if score >= 0.75 and not flags:
        return "accept"
    if score >= 0.75 and otp_verified:
        return "accept"
    if score >= 0.55:
        return "request_more_evidence" if flags else "accept"
    if score >= 0.35:
        return "manual_review"
    return "reject"


async def calculate_citizen_reputation_score(citizen_id: str) -> float:
    """Calculate reporter reputation from historical complaint behavior."""
    try:
        db = await get_database()
        citizen = await db["citizens"].find_one({"user_id": citizen_id})
        citizen = normalize_mongo_document(citizen) or {}
        submitted = citizen.get("complaints_submitted", 0)
        resolved = citizen.get("complaints_resolved", 0)
        impact_score = citizen.get("impact_score", 0)
        verified = citizen.get("verified", False)

        if submitted <= 0:
            return 0.65 if verified else 0.55

        resolution_ratio = min(1.0, resolved / max(submitted, 1))
        activity_bonus = min(0.15, submitted * 0.01)
        impact_bonus = min(0.15, impact_score / 100)
        verification_bonus = 0.1 if verified else 0.0
        return min(1.0, 0.35 + resolution_ratio * 0.35 + activity_bonus + impact_bonus + verification_bonus)
    except Exception as e:
        print(f"[TRUST] Could not calculate citizen reputation: {e}")
        return 0.5


async def score_complaint_trust(
    complaint: Complaint,
    *,
    image_base64: Optional[str] = None,
    audio_file_path: Optional[str] = None,
    vision_analysis: Optional[Dict[str, Any]] = None,
    transcript: str = "",
    otp_verified: bool = False,
) -> TrustScore:
    """Score a complaint for trust, evidence quality, and verification readiness."""
    media_types = {attachment.type for attachment in complaint.media_attachments}
    context = {
        "citizen_id": complaint.citizen_id,
        "issue_title": complaint.issue_title,
        "issue_description": complaint.issue_description,
        "classification": complaint.classification.model_dump(mode="python") if complaint.classification else None,
        "latitude": complaint.location.latitude,
        "longitude": complaint.location.longitude,
        "address": complaint.location.address,
        "ward_id": complaint.location.ward_id,
        "has_image": bool(image_base64) or "image" in media_types,
        "has_audio": bool(audio_file_path) or "audio" in media_types,
        "voice_draft": complaint.voice_draft.model_dump(mode="python") if complaint.voice_draft else None,
    }

    ai_result = await generate_trust_score_analysis(
        complaint_context=context,
        vision_analysis=vision_analysis or complaint.metadata.get("vision_analysis", {}),
        transcript=transcript
        or (complaint.voice_draft.original_transcript if complaint.voice_draft else ""),
    )
    reputation_score = await calculate_citizen_reputation_score(complaint.citizen_id)

    photo_score = float(ai_result.get("photo_quality_score", 0.5))
    voice_score = float(ai_result.get("voice_clarity_score", 0.5 if context["has_audio"] else 0.0))
    location_score = float(ai_result.get("location_accuracy_score", 0.7))
    flags = list(ai_result.get("evidence_flags", []))

    weighted_score = (
        photo_score * 0.3
        + max(voice_score, 0.5 if not context["has_audio"] else voice_score) * 0.2
        + location_score * 0.25
        + reputation_score * 0.15
        + (0.1 if otp_verified else 0.0)
    )
    weighted_score = min(1.0, max(0.0, weighted_score))

    recommended_action = ai_result.get("recommended_action") or _score_to_action(
        weighted_score, flags, otp_verified
    )
    if recommended_action == "accept":
        recommended_action = _score_to_action(weighted_score, flags, otp_verified)

    explanation = ai_result.get("explanation", "Trust score calculated from evidence and reporter history.")
    if otp_verified:
        explanation = f"{explanation} Mobile OTP verification completed."

    return TrustScore(
        overall_score=round(weighted_score, 3),
        photo_quality_score=round(photo_score, 3),
        voice_clarity_score=round(voice_score, 3),
        location_accuracy_score=round(location_score, 3),
        citizen_reputation_score=round(reputation_score, 3),
        otp_verified=otp_verified,
        evidence_flags=flags,
        recommended_action=recommended_action,
        explanation=explanation,
    )
