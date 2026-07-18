"""Tests for heatmap clustering and risk scoring."""

from datetime import datetime

import pytest

from app.agents import heatmap_agent


@pytest.mark.asyncio
async def test_cluster_complaints_geospatial_groups_nearby_points():
    complaints = [
        {
            "id": "COMP_1",
            "latitude": 22.5726,
            "longitude": 88.3639,
            "severity": "high",
            "timestamp": datetime.utcnow(),
            "issue_type": "pothole",
        },
        {
            "id": "COMP_2",
            "latitude": 22.5727,
            "longitude": 88.3640,
            "severity": "medium",
            "timestamp": datetime.utcnow(),
            "issue_type": "pothole",
        },
    ]

    labels, clusters = await heatmap_agent.cluster_complaints_geospatial(complaints, eps_meters=500)

    assert len(labels) == 2
    assert len(clusters) == 1


@pytest.mark.asyncio
async def test_calculate_cluster_risk_score_uses_severity():
    risk = await heatmap_agent.calculate_cluster_risk_score(
        [{"severity": "critical"}, {"severity": "high"}]
    )

    assert 0.7 <= risk <= 1.0


@pytest.mark.asyncio
async def test_orchestrate_heatmap_generation_uses_fetch_and_store(monkeypatch):
    async def fake_fetch(days_lookback=30, ward_id=None):
        return [
            {
                "id": "COMP_1",
                "latitude": 22.5726,
                "longitude": 88.3639,
                "severity": "high",
                "timestamp": datetime.utcnow(),
                "issue_type": "pothole",
            }
        ]

    async def fake_store(cluster_id, cluster_complaints, risk_score, time_windows):
        return {"cluster_id": cluster_id, "risk_score": risk_score, "point_count": len(cluster_complaints)}

    monkeypatch.setattr(heatmap_agent, "fetch_complaints_for_clustering", fake_fetch)
    monkeypatch.setattr(heatmap_agent, "store_cluster_in_db", fake_store)

    clusters = await heatmap_agent.orchestrate_heatmap_generation()

    assert clusters[0]["cluster_id"] == "cluster_0"
    assert clusters[0]["point_count"] == 1
