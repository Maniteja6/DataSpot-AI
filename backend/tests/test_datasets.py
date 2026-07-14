"""Tests for dataset upload, retrieval, and validation."""

from __future__ import annotations


def test_upload_dataset_returns_processing_status(client, sample_csv_path):
    with open(sample_csv_path, "rb") as f:
        response = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("sample_orders.csv", f, "text/csv")},
            data={"projectId": "proj_default"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "sample_orders.csv"
    assert body["status"] in ("processing", "ready")


def test_upload_rejects_unsupported_file_type(client, tmp_path):
    bad_file = tmp_path / "not_a_dataset.txt"
    bad_file.write_text("hello world")
    with open(bad_file, "rb") as f:
        response = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("not_a_dataset.txt", f, "text/plain")},
        )
    assert response.status_code == 422


def test_get_dataset_after_pipeline_completes(client, uploaded_dataset_id):
    response = client.get(f"/api/v1/datasets/{uploaded_dataset_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["rowCount"] > 0
    assert 0 <= body["qualityScore"] <= 100


def test_get_unknown_dataset_returns_404(client):
    response = client.get("/api/v1/datasets/does-not-exist")
    assert response.status_code == 404


def test_list_datasets_includes_uploaded_dataset(client, uploaded_dataset_id):
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    ids = [d["id"] for d in response.json()]
    assert uploaded_dataset_id in ids
