"""
Shared pytest fixtures. Generates a small synthetic CSV and a TestClient
bound to the real FastAPI app — no mocking of the app itself, since the
whole point of this prototype is that it runs fully offline already.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def app():
    from app.main import app as fastapi_app

    return fastapi_app


@pytest.fixture(scope="session")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="session")
def sample_csv_path(tmp_path_factory):
    np.random.seed(0)
    n = 150
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    df = pd.DataFrame(
        {
            "order_id": [f"ORD-{i}" for i in range(n)],
            "order_date": dates,
            "region": np.random.choice(["West", "East", "Midwest", "South"], n),
            "revenue": np.random.normal(800, 200, n).round(2) + np.arange(n) * 2,
            "units": np.random.randint(1, 50, n),
        }
    )
    df.loc[5:8, "revenue"] = np.nan
    df = pd.concat([df, df.iloc[:5]], ignore_index=True)

    path = tmp_path_factory.mktemp("data") / "sample_orders.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def uploaded_dataset_id(client, sample_csv_path):
    with open(sample_csv_path, "rb") as f:
        response = client.post(
            "/api/v1/datasets/upload",
            files={"file": ("sample_orders.csv", f, "text/csv")},
            data={"projectId": "proj_default"},
        )
    assert response.status_code == 200
    return response.json()["id"]
