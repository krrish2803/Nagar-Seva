"""Tests for AI trust scoring and OTP verification."""

from datetime import datetime, timedelta

import pytest

from app.agents import trust_scoring_agent
from app.models.complaint import Classification, Complaint, IssueType, Location, SeverityLevel
from app.utils import auth


class FakeResult:
    matched_count = 1


class FakeCollection:
    def __init__(self, document=None):
        self.document = document
        self.updated = []

    async def find_one(self, query, sort=None):
        return self.document

    async def update_one(self, *args, **kwargs):
        self.updated.append((args, kwargs))
        return FakeResult()


class FakeDB:
    def __init__(self, citizen=None, otp=None):
        self.collections = {
            "citizens": FakeCollection(citizen),
            "otp_verifications": FakeCollection(otp),
        }

    def __getitem__(self, name):
        return self.collections[name]


def _complaint():
    return Complaint(
        citizen_id="CITI_TEST",
        issue_title="Large pothole",
        issue_description="Large pothole near school",
        location=Location(latitude=22.57, longitude=88.36, address="Test Road", ward_id="ward_001"),
        classification=Classification(
            issue_type=IssueType.POTHOLE,
            severity=SeverityLevel.HIGH,
            confidence=0.9,
            description="Large pothole",
        ),
        media_attachments=[{"type": "image", "url": "x", "file_name": "photo.jpg"}],
    )


@pytest.mark.asyncio
async def test_score_complaint_trust_combines_ai_reputation_and_otp(monkeypatch):
    async def fake_ai(*args, **kwargs):
        return {
            "photo_quality_score": 0.9,
            "voice_clarity_score": 0.8,
            "location_accuracy_score": 0.85,
            "evidence_flags": [],
            "recommended_action": "accept",
            "explanation": "Evidence is strong.",
        }

    async def fake_reputation(citizen_id):
        return 0.75

    monkeypatch.setattr(trust_scoring_agent, "generate_trust_score_analysis", fake_ai)
    monkeypatch.setattr(trust_scoring_agent, "calculate_citizen_reputation_score", fake_reputation)

    score = await trust_scoring_agent.score_complaint_trust(
        _complaint(),
        image_base64="abc",
        transcript="Clear voice report",
        otp_verified=True,
    )

    assert score.overall_score >= 0.8
    assert score.otp_verified is True
    assert score.recommended_action == "accept"


@pytest.mark.asyncio
async def test_score_complaint_trust_flags_low_evidence(monkeypatch):
    async def fake_ai(*args, **kwargs):
        return {
            "photo_quality_score": 0.2,
            "voice_clarity_score": 0.1,
            "location_accuracy_score": 0.4,
            "evidence_flags": ["missing_photo", "unclear_voice"],
            "recommended_action": "manual_review",
            "explanation": "Evidence is weak.",
        }

    async def fake_reputation(citizen_id):
        return 0.4

    monkeypatch.setattr(trust_scoring_agent, "generate_trust_score_analysis", fake_ai)
    monkeypatch.setattr(trust_scoring_agent, "calculate_citizen_reputation_score", fake_reputation)

    score = await trust_scoring_agent.score_complaint_trust(_complaint())

    assert score.overall_score < 0.5
    assert "missing_photo" in score.evidence_flags
    assert score.recommended_action == "manual_review"


@pytest.mark.asyncio
async def test_request_mobile_otp_sends_sms(monkeypatch):
    fake_db = FakeDB()

    async def fake_get_database():
        return fake_db

    sent = {}

    async def fake_sms(phone, message):
        sent["phone"] = phone
        sent["message"] = message
        return True

    monkeypatch.setattr(auth, "get_database", fake_get_database)
    monkeypatch.setattr(auth, "send_sms", fake_sms)

    result = await auth.request_mobile_otp(
        auth.OTPRequest(user_id="CITI_TEST", phone="+910000000000")
    )

    assert result["status"] == "sent"
    assert sent["phone"] == "+910000000000"
    assert fake_db["otp_verifications"].updated


@pytest.mark.asyncio
async def test_verify_mobile_otp_marks_user_verified(monkeypatch):
    otp_hash = auth.hash_password("123456")
    fake_db = FakeDB(
        otp={
            "_id": "OTP_1",
            "user_id": "CITI_TEST",
            "phone": "+910000000000",
            "purpose": "complaint_trust",
            "otp_hash": otp_hash,
            "expires_at": datetime.utcnow() + timedelta(minutes=5),
            "attempts": 0,
            "verified": False,
        }
    )

    async def fake_get_database():
        return fake_db

    monkeypatch.setattr(auth, "get_database", fake_get_database)

    result = await auth.verify_mobile_otp(
        auth.OTPVerifyRequest(
            user_id="CITI_TEST",
            phone="+910000000000",
            otp_code="123456",
        )
    )

    assert result["status"] == "verified"
    assert fake_db["otp_verifications"].updated
    assert fake_db["citizens"].updated
