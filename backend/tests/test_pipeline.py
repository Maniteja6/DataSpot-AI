"""Tests for the LangGraph pipeline end-to-end (validate -> clean -> analyze
-> predict -> decide -> summarize -> index)."""

from __future__ import annotations


def test_pipeline_reaches_ready_status(client, uploaded_dataset_id):
    response = client.get(f"/api/v1/datasets/{uploaded_dataset_id}")
    assert response.json()["status"] == "ready"


def test_pipeline_status_reports_all_stages_complete(client, uploaded_dataset_id):
    response = client.get("/api/v1/agents/pipeline-status", params={"datasetId": uploaded_dataset_id})
    assert response.status_code == 200
    stages = response.json()["stages"]
    assert len(stages) == 7
    assert all(s["status"] == "complete" for s in stages)


def test_pipeline_produces_insights(client, uploaded_dataset_id):
    response = client.get("/api/v1/insights", params={"datasetId": uploaded_dataset_id})
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_pipeline_produces_decisions(client, uploaded_dataset_id):
    response = client.get("/api/v1/decisions", params={"datasetId": uploaded_dataset_id})
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_pipeline_produces_predictive_run(client, uploaded_dataset_id):
    response = client.get(f"/api/v1/predictive/{uploaded_dataset_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["target"]
    assert len(body["candidates"]) > 0


def test_data_quality_issues_reflect_injected_duplicates_and_missing_values(client, uploaded_dataset_id):
    response = client.get(f"/api/v1/data-quality/{uploaded_dataset_id}/issues")
    assert response.status_code == 200
    issue_types = [issue["type"] for issue in response.json()]
    assert "deduplicate" in issue_types
    assert any(t.startswith("impute") for t in issue_types)
