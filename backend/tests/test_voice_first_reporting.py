"""Tests for voice-first complaint reporting."""

from app.agents import classification_agent
from app.models.complaint import Classification, Complaint, IssueType, Location, SeverityLevel, TrustScore, VoiceDraft
from app.routers import complaints

import pytest


class FakeUpload:
    def __init__(self, filename, content):
        self.filename = filename
        self.content = content

    async def read(self):
        return self.content


class FakeCollection:
    def __init__(self):
        self.inserted = []

    async def insert_one(self, document):
        self.inserted.append(document)

        class Result:
            inserted_id = document.get("_id", "inserted")

        return Result()

    async def update_one(self, *args, **kwargs):
        return None


class FakeDB:
    def __init__(self):
        self.collections = {
            "complaints": FakeCollection(),
            "citizens": FakeCollection(),
            "safety_incidents": FakeCollection(),
        }

    def __getitem__(self, name):
        return self.collections[name]


@pytest.mark.asyncio
async def test_orchestrate_voice_first_report_drafts_complaint(monkeypatch):
    async def fake_transcribe(path):
        return "Sadak par bada gaddha hai"

    async def fake_draft(transcript, vision_analysis, location_info):
        return {
            "detected_language": "hi",
            "translated_text": "There is a large pothole on the road",
            "drafted_title": "Large pothole on road",
            "drafted_description": "A large pothole is creating a traffic hazard.",
            "confidence": 0.92,
            "needs_human_review": False,
        }

    async def fake_summary(vision_analysis, voice_text, location_text):
        return {
            "final_issue_type": "pothole",
            "severity_level": "high",
            "confidence": 0.9,
            "summary": "Large pothole on road",
            "keywords": ["pothole"],
        }

    monkeypatch.setattr(classification_agent, "transcribe_audio", fake_transcribe)
    monkeypatch.setattr(classification_agent, "generate_voice_complaint_draft", fake_draft)
    monkeypatch.setattr(classification_agent, "generate_classification_summary", fake_summary)

    complaint = await classification_agent.orchestrate_voice_first_report(
        citizen_id="CITI_TEST",
        location=Location(latitude=22.57, longitude=88.36, address="Test Road"),
        audio_file_path="/tmp/audio.wav",
    )

    assert complaint.issue_title == "Large pothole on road"
    assert complaint.voice_draft.detected_language == "hi"
    assert complaint.classification.issue_type == IssueType.POTHOLE


@pytest.mark.asyncio
async def test_voice_endpoint_routes_and_persists(monkeypatch):
    fake_db = FakeDB()

    async def fake_get_database():
        return fake_db

    async def fake_save_upload_file(content, file_name, file_type="image"):
        return f"uploads/{file_type}/{file_name}"

    async def fake_voice_report(**kwargs):
        return Complaint(
            citizen_id=kwargs["citizen_id"],
            issue_title="Large pothole on road",
            issue_description="A large pothole is creating a hazard.",
            location=kwargs["location"],
            classification=Classification(
                issue_type=IssueType.POTHOLE,
                severity=SeverityLevel.HIGH,
                confidence=0.9,
                description="Large pothole",
            ),
            voice_draft=VoiceDraft(
                original_transcript="Sadak par bada gaddha hai",
                detected_language="hi",
                translated_text="There is a large pothole on the road",
                drafted_title="Large pothole on road",
                drafted_description="A large pothole is creating a hazard.",
                confidence=0.9,
                needs_human_review=False,
            ),
            media_attachments=kwargs["media_attachments"],
        )

    async def fake_routing(complaint):
        return {
            "status": "assigned",
            "assignment": {
                "official_id": "OFF_TEST",
                "department": "Public_Works",
                "sla_days": 5,
                "expected_resolution": complaint.created_at,
            },
            "official": {"official_id": "OFF_TEST"},
            "routing_rules": {"sla_days": 5},
        }

    async def fake_trust(*args, **kwargs):
        return TrustScore(
            overall_score=0.86,
            photo_quality_score=0.9,
            voice_clarity_score=0.8,
            location_accuracy_score=0.85,
            citizen_reputation_score=0.7,
            otp_verified=False,
            evidence_flags=[],
            recommended_action="accept",
            explanation="Strong evidence.",
        )

    monkeypatch.setattr(complaints, "get_database", fake_get_database)
    monkeypatch.setattr(complaints, "save_upload_file", fake_save_upload_file)
    monkeypatch.setattr(complaints, "orchestrate_voice_first_report", fake_voice_report)
    monkeypatch.setattr(complaints, "orchestrate_routing", fake_routing)
    monkeypatch.setattr(complaints, "score_complaint_trust", fake_trust)

    response = await complaints.report_complaint_by_voice(
        citizen_id="CITI_TEST",
        latitude=22.57,
        longitude=88.36,
        address="Test Road",
        ward_id=None,
        pin_code=None,
        language_hint=None,
        audio_file=FakeUpload("voice.wav", b"audio"),
        image_file=FakeUpload("photo.jpg", b"image"),
    )

    assert response.issue_type == "pothole"
    assert response.trust_score == 0.86
    assert response.trust_action == "accept"
    assert response.detected_language == "hi"
    assert response.drafted_title == "Large pothole on road"
    assert fake_db["complaints"].inserted
    assert fake_db["safety_incidents"].inserted
