"""Tests for database-backed API helpers."""

from datetime import datetime

import pytest

from app.routers import complaints, escalation, heatmap


class AsyncCursor:
    def __init__(self, documents):
        self.documents = documents

    def sort(self, *args, **kwargs):
        return self

    def skip(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def __aiter__(self):
        self.index = 0
        return self

    async def __anext__(self):
        if self.index >= len(self.documents):
            raise StopAsyncIteration
        document = self.documents[self.index]
        self.index += 1
        return document


class FakeResult:
    matched_count = 1
    modified_count = 1


class FakeCollection:
    def __init__(self, documents=None):
        self.documents = documents or []
        self.last_update = None

    async def count_documents(self, query):
        return len(self.documents)

    def find(self, query=None):
        return AsyncCursor(self.documents)

    async def find_one(self, query):
        return self.documents[0] if self.documents else None

    async def update_one(self, *args, **kwargs):
        self.last_update = (args, kwargs)
        return FakeResult()

    async def update_many(self, *args, **kwargs):
        self.last_update = (args, kwargs)
        return FakeResult()


class FakeDB:
    def __init__(self):
        self.complaint = {
            "_id": "COMP_1",
            "status": "assigned",
            "citizen_id": "CITI_1",
            "issue_title": "Broken streetlight",
            "issue_description": "Streetlight is not working near the market",
            "location": {"ward_id": "ward_001"},
            "classification": {"severity": "high", "issue_type": "pothole"},
            "assignment": {
                "department": "Public Works",
                "official_role": "road supervisor",
                "sla_days": 7,
            },
            "trust_score": {
                "overall_score": 0.8,
                "recommended_action": "accept",
                "evidence_flags": [],
                "otp_verified": True,
            },
            "media_attachments": [
                {"type": "image", "url": "/uploads/image.jpg"},
            ],
            "created_at": datetime.utcnow(),
        }
        self.collections = {
            "complaints": FakeCollection([self.complaint]),
            "safety_incidents": FakeCollection([]),
            "escalations": FakeCollection([
                {
                    "_id": "ESC_1",
                    "complaint_id": "COMP_1",
                    "escalation_level": 1,
                    "created_at": datetime.utcnow(),
                    "status": "pending",
                }
            ]),
        }

    def __getitem__(self, name):
        return self.collections[name]


@pytest.mark.asyncio
async def test_list_and_get_complaints_read_database(monkeypatch):
    fake_db = FakeDB()
    async def fake_get_database():
        return fake_db

    monkeypatch.setattr(complaints, "get_database", fake_get_database)

    listed = await complaints.list_complaints()
    detail = await complaints.get_complaint("COMP_1")

    assert listed["total"] == 1
    assert listed["complaints"][0]["_id"] == "COMP_1"
    assert detail["_id"] == "COMP_1"


@pytest.mark.asyncio
async def test_citizen_dashboard_enriches_reports(monkeypatch):
    fake_db = FakeDB()

    async def fake_get_database():
        return fake_db

    async def fake_progress_update(context):
        return f"Your {context['issue_title']} is with {context['official_role']}."

    monkeypatch.setattr(complaints, "get_database", fake_get_database)
    monkeypatch.setattr(complaints, "generate_citizen_progress_update", fake_progress_update)

    result = await complaints.get_citizen_dashboard("CITI_1")

    assert result["citizen_id"] == "CITI_1"
    assert result["total_reports"] == 1
    assert result["active_reports"] == 1
    assert result["escalated_reports"] == 1
    assert result["reports"][0]["ai_progress_update"] == "Your Broken streetlight is with road supervisor."
    assert result["reports"][0]["photos"] == ["/uploads/image.jpg"]
    assert result["reports"][0]["trust_summary"]["score"] == 0.8


@pytest.mark.asyncio
async def test_update_complaint_status_writes_database(monkeypatch):
    fake_db = FakeDB()
    async def fake_get_database():
        return fake_db

    monkeypatch.setattr(complaints, "get_database", fake_get_database)

    result = await complaints.update_complaint_status("COMP_1", "resolved", "Fixed", "OFF_1")

    assert result["status"] == "resolved"
    assert fake_db["complaints"].last_update is not None


@pytest.mark.asyncio
async def test_heatmap_risk_distribution_uses_database(monkeypatch):
    fake_db = FakeDB()
    async def fake_get_database():
        return fake_db

    monkeypatch.setattr(heatmap, "get_database", fake_get_database)

    result = await heatmap.get_risk_distribution(days_lookback=30)

    assert result["total_incidents"] == 1
    assert result["risk_distribution"]["high"] == 1


@pytest.mark.asyncio
async def test_escalation_pending_count_uses_database(monkeypatch):
    fake_db = FakeDB()
    async def fake_get_database():
        return fake_db

    monkeypatch.setattr(escalation, "get_database", fake_get_database)

    result = await escalation.get_pending_escalation_count()

    assert result["pending_count"] == 1
