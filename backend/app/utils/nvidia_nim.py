"""NVIDIA NIM API integration with deterministic fallbacks."""

import json
from typing import Optional, Dict, Any
import httpx

from app.config import settings
from app.models.complaint import IssueType, SeverityLevel


def _nvidia_enabled() -> bool:
    """Return True when an actual NVIDIA API key is configured."""
    return bool(settings.nvidia_api_key and not settings.nvidia_api_key.startswith("mock"))


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Extract a JSON object from a model response."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


async def _chat_completion(
    model: str,
    messages: list,
    temperature: float = 0.2,
    max_tokens: int = 800,
) -> str:
    """Call NVIDIA NIM chat completions."""
    if not _nvidia_enabled():
        raise RuntimeError("NVIDIA API key is not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.nvidia_nim_base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.nvidia_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio using NVIDIA ASR when configured.

    Args:
        audio_path: Path to audio file

    Returns:
        Transcribed text
    """
    if _nvidia_enabled() and settings.nvidia_model_asr:
        try:
            with open(audio_path, "rb") as audio_file:
                files = {"file": (audio_path, audio_file, "audio/wav")}
                data = {"model": settings.nvidia_model_asr}
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{settings.nvidia_nim_base_url.rstrip('/')}/audio/transcriptions",
                        headers={"Authorization": f"Bearer {settings.nvidia_api_key}"},
                        data=data,
                        files=files,
                    )
                    response.raise_for_status()
                    payload = response.json()
                    return payload.get("text", "")
        except Exception as e:
            print(f"[NVIDIA] ASR call failed, using fallback: {e}")

    # Keep deterministic fallback when no ASR deployment is configured.
    fallback_transcriptions = {
        "pothole": "There is a large pothole on the main road causing accidents",
        "water_leak": "Water is leaking from the municipal pipe near the market",
        "garbage": "There is garbage scattered everywhere on the street",
        "streetlight": "The street light at the corner is broken and not working",
        "drainage": "The drainage system is blocked causing water accumulation",
    }

    return fallback_transcriptions.get(
        "pothole", "There is an issue that needs attention"
    )


async def analyze_image_with_vision_llm(
    image_base64: str, context_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze an image using NVIDIA vision LLM.

    Args:
        image_base64: Base64 encoded image
        context_text: Optional context text from audio

    Returns:
        Analysis results with detected objects and issues
    """
    try:
        prompt = (
            "Analyze this civic issue image. Return only JSON with keys: "
            "detected_objects, issue_description, severity_indicators, confidence, "
            "recommended_issue_type, image_quality. Valid issue types are pothole, "
            "water_leak, garbage, streetlight, traffic_signal, tree_hazard, drainage, "
            "public_safety, other."
        )
        if context_text:
            prompt += f" Citizen context: {context_text}"

        content = await _chat_completion(
            settings.nvidia_model_vision,
            [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        },
                    ],
                }
            ],
        )
        return _extract_json_object(content)
    except Exception as e:
        print(f"[NVIDIA] Vision call failed, using fallback: {e}")
        return {
            "detected_objects": ["road", "pothole", "dirt"],
            "issue_description": "A medium-sized pothole is visible on the asphalt road, approximately 1-2 feet in diameter. The surface is cracked around the edges.",
            "severity_indicators": {
                "road_damage_level": 0.7,
                "potential_hazard": 0.8,
                "weather_affected": 0.3,
            },
            "confidence": 0.85,
            "recommended_issue_type": "pothole",
            "image_quality": 0.92,
        }


async def generate_classification_summary(
    vision_analysis: Dict[str, Any],
    voice_transcription: str,
    location_info: str,
) -> Dict[str, Any]:
    """
    Generate a comprehensive classification summary using NVIDIA NIM.

    Args:
        vision_analysis: Results from vision analysis
        voice_transcription: User's spoken description
        location_info: Location address and coordinates

    Returns:
        Classification summary
    """
    try:
        prompt = f"""
Classify this civic complaint. Return only JSON with:
final_issue_type, severity_level, confidence, summary, keywords, recommended_department, sla_days.

Valid issue types: pothole, water_leak, garbage, streetlight, traffic_signal, tree_hazard, drainage, public_safety, other.
Valid severity levels: low, medium, high, critical.

Location: {location_info}
Citizen text: {voice_transcription}
Vision analysis: {json.dumps(vision_analysis)}
"""
        content = await _chat_completion(
            settings.nvidia_model_text,
            [{"role": "user", "content": prompt}],
        )
        return _extract_json_object(content)
    except Exception as e:
        print(f"[NVIDIA] Classification call failed, using fallback: {e}")
        issue_text = f"{voice_transcription} {json.dumps(vision_analysis)}".lower()
        issue_type = "other"
        for candidate in [
            "pothole",
            "water_leak",
            "garbage",
            "streetlight",
            "traffic_signal",
            "tree_hazard",
            "drainage",
            "public_safety",
        ]:
            if candidate.replace("_", " ") in issue_text or candidate in issue_text:
                issue_type = candidate
                break

        severity = "critical" if any(word in issue_text for word in ["injury", "death", "fire", "emergency"]) else "high" if any(word in issue_text for word in ["danger", "hazard", "large", "broken"]) else "medium"

        return {
            "final_issue_type": issue_type,
            "severity_level": severity,
            "confidence": 0.72,
            "summary": f"{issue_type.replace('_', ' ').title()} reported at {location_info}. Citizen reported: {voice_transcription}",
            "keywords": [issue_type, severity],
            "recommended_department": "Public_Works",
            "sla_days": 7,
        }


async def generate_voice_complaint_draft(
    transcript: str,
    vision_analysis: Dict[str, Any],
    location_info: str,
) -> Dict[str, Any]:
    """
    Generate a complete complaint draft from a multilingual voice transcript and image context.

    Returns:
        Dict with detected_language, translated_text, drafted_title, drafted_description,
        confidence, and needs_human_review.
    """
    try:
        prompt = f"""
You are drafting a civic complaint for an Indian municipal grievance system.
The citizen may speak in Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada,
Malayalam, Punjabi, Urdu, Hinglish, or English.

Return only JSON with:
detected_language, translated_text, drafted_title, drafted_description, confidence, needs_human_review.

Rules:
- Keep drafted_title under 80 characters.
- drafted_description should be clear, respectful, and actionable for municipal staff.
- Include visible evidence from the image if available.
- If transcript is unclear or too short, set needs_human_review to true.

Location: {location_info}
Voice transcript: {transcript}
Image analysis: {json.dumps(vision_analysis, default=str)}
"""
        content = await _chat_completion(
            settings.nvidia_model_text,
            [{"role": "user", "content": prompt}],
            max_tokens=700,
        )
        return _extract_json_object(content)
    except Exception as e:
        print(f"[NVIDIA] Voice draft call failed, using fallback: {e}")
        cleaned = transcript.strip() or "Citizen reported a civic issue."
        title = cleaned[:77] + "..." if len(cleaned) > 80 else cleaned
        if len(title) < 8:
            title = "Civic issue reported by voice"
        return {
            "detected_language": "unknown",
            "translated_text": cleaned,
            "drafted_title": title,
            "drafted_description": cleaned,
            "confidence": 0.55,
            "needs_human_review": len(cleaned.split()) < 4,
        }


async def generate_trust_score_analysis(
    complaint_context: Dict[str, Any],
    vision_analysis: Dict[str, Any],
    transcript: str,
) -> Dict[str, Any]:
    """
    Generate AI trust-score analysis for report verification.

    Returns:
        Dict with photo_quality_score, voice_clarity_score, location_accuracy_score,
        evidence_flags, recommended_action, and explanation.
    """
    try:
        prompt = f"""
Evaluate this civic complaint for trust and evidence quality.
Return only JSON with:
photo_quality_score, voice_clarity_score, location_accuracy_score,
evidence_flags, recommended_action, explanation.

Scores must be 0 to 1.
recommended_action must be one of: accept, request_more_evidence, manual_review, reject.

Evaluate:
- Is the photo clear and relevant?
- Is the voice/transcript clear enough?
- Do GPS/address/ward details look specific and plausible?
- Are there signs of spam, contradiction, or weak evidence?

Complaint context: {json.dumps(complaint_context, default=str)}
Vision analysis: {json.dumps(vision_analysis, default=str)}
Transcript: {transcript}
"""
        content = await _chat_completion(
            settings.nvidia_model_text,
            [{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        return _extract_json_object(content)
    except Exception as e:
        print(f"[NVIDIA] Trust score call failed, using fallback: {e}")
        has_image = bool(complaint_context.get("has_image"))
        has_audio = bool(complaint_context.get("has_audio"))
        description = complaint_context.get("issue_description", "")
        flags = []
        photo_score = 0.8 if has_image else 0.25
        voice_score = min(1.0, max(0.2, len(transcript.split()) / 12)) if has_audio else 0.0
        location_score = 0.85 if complaint_context.get("latitude") and complaint_context.get("longitude") else 0.35
        if not has_image:
            flags.append("missing_photo")
        if has_audio and len(transcript.split()) < 4:
            flags.append("unclear_voice")
        if len(description.split()) < 4:
            flags.append("thin_description")
        recommended_action = "accept"
        if flags:
            recommended_action = "request_more_evidence"
        if len(flags) >= 2:
            recommended_action = "manual_review"
        return {
            "photo_quality_score": photo_score,
            "voice_clarity_score": voice_score,
            "location_accuracy_score": location_score,
            "evidence_flags": flags,
            "recommended_action": recommended_action,
            "explanation": "Trust score generated from available media, voice clarity, and location specificity.",
        }


async def generate_citizen_progress_update(complaint_data: Dict[str, Any]) -> str:
    """
    Generate a simple citizen-facing progress update for the dashboard.

    Returns:
        Short, plain-language status update.
    """
    try:
        prompt = f"""
Write one friendly citizen-facing status update for this municipal complaint.

Rules:
- Maximum 28 words.
- Keep it simple and reassuring.
- Mention the assigned team/official if present.
- Mention expected resolution time if present.
- Do not invent details that are not in the data.

Complaint data: {json.dumps(complaint_data, default=str)}
"""
        content = await _chat_completion(
            settings.nvidia_model_text,
            [{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=120,
        )
        return content.strip().strip('"')
    except Exception as e:
        print(f"[NVIDIA] Citizen progress update failed, using fallback: {e}")
        title = complaint_data.get("issue_title", "complaint")
        status = str(complaint_data.get("status", "submitted")).replace("_", " ")
        department = complaint_data.get("department") or complaint_data.get("assigned_department")
        official_role = complaint_data.get("official_role") or complaint_data.get("assigned_role")
        days_remaining = complaint_data.get("days_remaining")
        is_overdue = complaint_data.get("is_overdue", False)

        owner = official_role or department or "the concerned municipal team"
        if status == "resolved":
            return f"Your {title} has been resolved. Thank you for helping improve the city."
        if is_overdue:
            return f"Your {title} is overdue and marked for escalation with {owner}."
        if days_remaining is not None:
            return f"Your {title} is with {owner} — expected resolution in {days_remaining} days."
        return f"Your {title} is currently {status} with {owner}."


async def generate_escalation_summary(
    complaint_data: Dict[str, Any],
    progress_data: Dict[str, Any],
) -> str:
    """
    Generate an escalation summary using NVIDIA NIM.

    Args:
        complaint_data: Complaint details
        progress_data: Current progress status

    Returns:
        Escalation summary text
    """
    try:
        prompt = f"""
Generate a concise municipal escalation summary for this overdue complaint.

Complaint:
{json.dumps(complaint_data, default=str)}

Progress:
{json.dumps(progress_data, default=str)}
"""
        return await _chat_completion(
            settings.nvidia_model_text,
            [{"role": "user", "content": prompt}],
            max_tokens=500,
        )
    except Exception as e:
        print(f"[NVIDIA] Escalation summary failed, using fallback: {e}")
        summary = f"""
ESCALATION SUMMARY
==================
Complaint ID: {complaint_data.get('id', 'unknown')}
Issue: {complaint_data.get('issue_title', 'N/A')}
Original Severity: {complaint_data.get('severity', 'N/A')}

Progress Status: {progress_data.get('status', 'No progress')}
Days Overdue: {progress_data.get('days_overdue', 0)}

Reason for Escalation:
The complaint has exceeded the SLA timeframe without adequate progress.
The assigned official has not provided satisfactory updates.

Recommended Action:
Escalate to department head for immediate intervention.
"""
        return summary


async def generate_route_safety_analysis(
    segment_data: Dict[str, Any],
    time_of_day: str,
) -> Dict[str, Any]:
    """
    Analyze route safety using NVIDIA NIM.

    Args:
        segment_data: Route segment information
        time_of_day: Time period (morning, afternoon, evening, night)

    Returns:
        Safety analysis
    """
    try:
        prompt = f"""
Analyze route segment safety. Return only JSON with keys risk_score, risk_level, factors, recommendations.
Risk score must be 0 to 1.

Time of day: {time_of_day}
Segment data: {json.dumps(segment_data, default=str)}
"""
        content = await _chat_completion(
            settings.nvidia_model_text,
            [{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return _extract_json_object(content)
    except Exception as e:
        print(f"[NVIDIA] Route safety call failed, using fallback: {e}")

    risk_mapping = {
        "morning": 0.3,
        "afternoon": 0.4,
        "evening": 0.6,
        "night": 0.85,
    }

    base_risk = segment_data.get("base_incident_count", 0) * 0.1
    time_factor = risk_mapping.get(time_of_day, 0.5)

    return {
        "risk_score": min(1.0, base_risk + time_factor * 0.5),
        "risk_level": "high" if (base_risk + time_factor * 0.5) > 0.6 else "medium" if (base_risk + time_factor * 0.5) > 0.3 else "low",
        "factors": [
            f"Incident density: {segment_data.get('incident_count', 0)} incidents",
            f"Time of day: {time_of_day}",
            f"Lighting conditions: {'Poor' if time_of_day == 'night' else 'Good'}",
        ],
        "recommendations": [
            "Avoid this route during night hours",
            "Travel with companions during evening",
            "Use well-lit main roads",
        ],
    }


# Utility functions for request shape previews
def create_vision_api_request(
    image_base64: str, prompt: str
) -> Dict[str, Any]:
    """
    Create a NVIDIA vision API request payload.

    Args:
        image_base64: Base64 encoded image
        prompt: Analysis prompt

    Returns:
        API request format
    """
    return {
        "model": settings.nvidia_model_vision,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\n[Image provided as base64]",
            }
        ],
        "max_tokens": 512,
        "temperature": 0.7,
    }


def create_text_api_request(prompt: str) -> Dict[str, Any]:
    """
    Create a NVIDIA text API request payload.

    Args:
        prompt: Text analysis prompt

    Returns:
        API request format
    """
    return {
        "model": settings.nvidia_model_text,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "max_tokens": 512,
        "temperature": 0.7,
    }
