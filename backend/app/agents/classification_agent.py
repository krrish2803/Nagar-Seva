"""Agent 1: Multimodal Issue Intelligence Agent."""

import base64
from typing import Optional, Dict, Any
from app.models.complaint import (
    Complaint,
    Classification,
    IssueType,
    SeverityLevel,
    Location,
    MediaAttachment,
    VoiceDraft,
)
from app.utils.nvidia_nim import (
    transcribe_audio,
    analyze_image_with_vision_llm,
    generate_voice_complaint_draft,
    generate_classification_summary,
)
from app.utils.storage import save_upload_file
from datetime import datetime


async def extract_voice_text(audio_file_path: str) -> str:
    """
    Extract text from voice/audio file using NVIDIA speech-to-text.

    Args:
        audio_file_path: Path to audio file

    Returns:
        Transcribed text
    """
    try:
        text = await transcribe_audio(audio_file_path)
        print(f"[CLASSIFICATION] Voice extracted: {text}")
        return text
    except Exception as e:
        print(f"[CLASSIFICATION] Error extracting voice: {e}")
        return ""


async def analyze_image_vision(
    image_base64: str, voice_text: str
) -> Dict[str, Any]:
    """
    Analyze image using NVIDIA vision LLM with voice context.

    Args:
        image_base64: Base64 encoded image
        voice_text: Transcribed voice text for context

    Returns:
        Vision analysis results
    """
    try:
        analysis = await analyze_image_with_vision_llm(image_base64, voice_text)
        print(f"[CLASSIFICATION] Vision analysis complete: {analysis}")
        return analysis
    except Exception as e:
        print(f"[CLASSIFICATION] Error in vision analysis: {e}")
        return {}


async def fuse_multimodal_context(
    vision_analysis: Dict[str, Any], voice_text: str, location: Location
) -> Dict[str, Any]:
    """
    Fuse vision and voice context to create comprehensive understanding.

    Args:
        vision_analysis: Results from vision analysis
        voice_text: Transcribed voice text
        location: Location information

    Returns:
        Fused multimodal context
    """
    try:
        location_str = f"{location.address} ({location.latitude}, {location.longitude})"
        fused = await generate_classification_summary(
            vision_analysis, voice_text, location_str
        )
        print(f"[CLASSIFICATION] Multimodal fusion complete: {fused}")
        return fused
    except Exception as e:
        print(f"[CLASSIFICATION] Error fusing context: {e}")
        return {}


async def classify_issue_severity(
    fused_context: Dict[str, Any], location: Location
) -> Classification:
    """
    Classify issue type and severity from fused context.

    Args:
        fused_context: Fused multimodal understanding
        location: Location information

    Returns:
        Classification object
    """
    try:
        issue_type_str = fused_context.get("final_issue_type", "other").upper()
        severity_str = fused_context.get("severity_level", "medium").lower()

        # Map to enum values
        try:
            issue_type = IssueType[issue_type_str]
        except KeyError:
            issue_type = IssueType.OTHER

        try:
            severity = SeverityLevel[severity_str.upper()]
        except KeyError:
            severity = SeverityLevel.MEDIUM

        classification = Classification(
            issue_type=issue_type,
            severity=severity,
            confidence=fused_context.get("confidence", 0.7),
            description=fused_context.get("summary", "Issue detected"),
            extracted_keywords=fused_context.get("keywords", []),
        )
        print(f"[CLASSIFICATION] Issue classified: {issue_type} - {severity}")
        return classification
    except Exception as e:
        print(f"[CLASSIFICATION] Error in severity classification: {e}")
        return Classification(
            issue_type=IssueType.OTHER,
            severity=SeverityLevel.MEDIUM,
            confidence=0.5,
            description="Unable to classify",
        )


async def store_complaint_classification(
    complaint_id: str,
    classification: Classification,
    image_url: Optional[str] = None,
    location: Optional[Location] = None,
) -> Dict[str, Any]:
    """
    Store complaint classification results in database.

    Args:
        complaint_id: Complaint ID
        classification: Classification results
        image_url: URL of uploaded image
        location: Location information

    Returns:
        Stored complaint data
    """
    try:
        result = {
            "complaint_id": complaint_id,
            "classification": classification.dict(),
            "image_url": image_url,
            "location": location.dict() if location else None,
            "stored_at": datetime.utcnow().isoformat(),
            "status": "classified",
        }
        print(f"[CLASSIFICATION] Complaint {complaint_id} stored with classification")
        return result
    except Exception as e:
        print(f"[CLASSIFICATION] Error storing classification: {e}")
        return {"error": str(e)}


async def orchestrate_classification(
    citizen_id: str,
    issue_title: str,
    issue_description: str,
    location: Location,
    audio_file_path: Optional[str] = None,
    image_base64: Optional[str] = None,
    media_attachments: list = None,
) -> Complaint:
    """
    Orchestrate the complete classification pipeline.

    Args:
        citizen_id: Submitting citizen ID
        issue_title: Brief issue title
        issue_description: Issue description
        location: Location object
        audio_file_path: Optional path to audio file
        image_base64: Optional base64 encoded image
        media_attachments: Optional list of media attachments

    Returns:
        Complete Complaint object with classification
    """
    print(f"[CLASSIFICATION] Starting orchestration for complaint from {citizen_id}")

    # Step 1: Extract voice if audio provided
    voice_text = ""
    if audio_file_path:
        voice_text = await extract_voice_text(audio_file_path)

    # Step 2: Analyze image if provided
    vision_analysis = {}
    if image_base64:
        vision_analysis = await analyze_image_vision(image_base64, voice_text)

    # Step 3: Fuse multimodal context
    fused_context = await fuse_multimodal_context(
        vision_analysis, voice_text or issue_description, location
    )

    # Step 4: Classify severity
    classification = await classify_issue_severity(fused_context, location)

    # Step 5: Create complaint object
    complaint = Complaint(
        citizen_id=citizen_id,
        issue_title=issue_title,
        issue_description=issue_description,
        location=location,
        classification=classification,
        media_attachments=media_attachments or [],
        status="classified",
    )

    print(f"[CLASSIFICATION] Orchestration complete: {complaint.issue_title}")
    return complaint


async def orchestrate_voice_first_report(
    citizen_id: str,
    location: Location,
    audio_file_path: str,
    image_base64: Optional[str] = None,
    media_attachments: list = None,
    user_language_hint: Optional[str] = None,
) -> Complaint:
    """
    Orchestrate a voice-first complaint report.

    This flow lets a citizen submit only a voice note and optional photo. The agent:
    1. Transcribes the audio.
    2. Analyzes the image with transcript context.
    3. Drafts title/description from multilingual voice.
    4. Classifies severity and issue type.
    5. Returns a Complaint ready for routing and persistence.
    """
    print(f"[VOICE-FIRST] Starting voice-first report for {citizen_id}")

    voice_text = await extract_voice_text(audio_file_path)
    if user_language_hint:
        voice_text = f"[Language hint: {user_language_hint}] {voice_text}"

    vision_analysis = {}
    if image_base64:
        vision_analysis = await analyze_image_vision(image_base64, voice_text)

    location_str = f"{location.address} ({location.latitude}, {location.longitude})"
    draft_data = await generate_voice_complaint_draft(
        transcript=voice_text,
        vision_analysis=vision_analysis,
        location_info=location_str,
    )
    voice_draft = VoiceDraft(
        original_transcript=voice_text,
        detected_language=draft_data.get("detected_language", user_language_hint or "unknown"),
        translated_text=draft_data.get("translated_text", voice_text),
        drafted_title=draft_data.get("drafted_title", "Civic issue reported by voice"),
        drafted_description=draft_data.get("drafted_description", voice_text),
        confidence=draft_data.get("confidence", 0.7),
        needs_human_review=draft_data.get("needs_human_review", False),
    )

    fused_context = await fuse_multimodal_context(
        vision_analysis,
        voice_draft.translated_text or voice_draft.drafted_description,
        location,
    )
    classification = await classify_issue_severity(fused_context, location)

    complaint = Complaint(
        citizen_id=citizen_id,
        issue_title=voice_draft.drafted_title,
        issue_description=voice_draft.drafted_description,
        location=location,
        classification=classification,
        voice_draft=voice_draft,
        media_attachments=media_attachments or [],
        status="classified",
        metadata={
            "reporting_mode": "voice_first",
            "language_hint": user_language_hint,
            "vision_analysis": vision_analysis,
        },
    )

    print(f"[VOICE-FIRST] Drafted complaint: {complaint.issue_title}")
    return complaint
