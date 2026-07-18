"""Tests for database-backed authority routing."""

from datetime import datetime

import pytest

from app.agents import routing_agent
from app.models.complaint import Classification, Complaint, IssueType, Location, SeverityLevel


class FakeOfficials:
    async def find_one(self, query, sort=None):
        return {
            "_id": "official-db-id",
            "user_id": "OFF_TEST",
            "name": "Test Official",
            "email": "official@example.com",
            "phone": "+910000000000",
            "department": query.get("department", "Public_Works"),
            "ward_id": "ward_001",
            "availability_status": "available",
            "complaints_assigned": 0,
        }

    async def update_one(self, *args, **kwargs):
        return None


class FakeDB:
    def __getitem__(self, name):
        assert name == "officials"
        return FakeOfficials()


@pytest.mark.asyncio
async def test_determine_routing_rules_maps_issue_to_department():
    rules = await routing_agent.determine_routing_rules("pothole", "high")

    assert rules["department"] == "Public_Works"
    assert rules["sla_days"] == 5


@pytest.mark.asyncio
async def test_orchestrate_routing_uses_database_official(monkeypatch):
    async def fake_get_database():
        return FakeDB()

    monkeypatch.setattr(routing_agent, "get_database", fake_get_database)

    async def no_notification(*args, **kwargs):
        return True

    monkeypatch.setattr(routing_agent, "send_assignment_notification", no_notification)

    complaint = Complaint(
        id="COMP_TEST",
        citizen_id="CITI_TEST",
        issue_title="Pothole",
        issue_description="Large pothole",
        location=Location(latitude=22.57, longitude=88.36, address="Test Road", ward_id="ward_001"),
        classification=Classification(
            issue_type=IssueType.POTHOLE,
            severity=SeverityLevel.HIGH,
            confidence=0.9,
            description="Large pothole",
        ),
    )

    result = await routing_agent.orchestrate_routing(complaint)

    assert result["status"] == "assigned"
    assert result["official"]["official_id"] == "OFF_TEST"
    assert result["assignment"]["official_id"] == "OFF_TEST"
