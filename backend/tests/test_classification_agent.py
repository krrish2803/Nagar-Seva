"""Tests for the current classification agent."""

import pytest

from app.agents import classification_agent
from app.models.complaint import IssueType, Location, SeverityLevel


@pytest.mark.asyncio
async def test_orchestrate_classification_uses_nim_summary(monkeypatch):
    async def fake_summary(vision_analysis, voice_text, location_text):
        return {
            "final_issue_type": "garbage",
            "severity_level": "medium",
            "confidence": 0.91,
            "summary": "Garbage pile reported",
            "keywords": ["garbage", "waste"],
        }

    monkeypatch.setattr(classification_agent, "generate_classification_summary", fake_summary)

    complaint = await classification_agent.orchestrate_classification(
        citizen_id="CITI_TEST",
        issue_title="Garbage pile",
        issue_description="Garbage is blocking the road",
        location=Location(latitude=22.57, longitude=88.36, address="Test Road"),
    )

    assert complaint.classification.issue_type == IssueType.GARBAGE
    assert complaint.classification.severity == SeverityLevel.MEDIUM
    assert complaint.classification.confidence == 0.91


@pytest.mark.asyncio
async def test_classify_issue_severity_defaults_to_other():
    classification = await classification_agent.classify_issue_severity(
        {"final_issue_type": "unknown", "severity_level": "strange"},
        Location(latitude=1, longitude=1, address="Anywhere"),
    )

    assert classification.issue_type == IssueType.OTHER
    assert classification.severity == SeverityLevel.MEDIUM
