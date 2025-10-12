import pytest
from fastapi.testclient import TestClient
from api.index import app, get_data

client = TestClient(app)

def mock_get_data():
    return [
        {"region": "amer", "latency_ms": 174.09, "uptime_pct": 99.361},
        {"region": "amer", "latency_ms": 188.01, "uptime_pct": 97.939},
        {"region": "amer", "latency_ms": 159.92, "uptime_pct": 98.372},
    ]

app.dependency_overrides[get_data] = mock_get_data

def test_calculate_metrics():
    response = client.post(
        "/metrics",
        json={"regions": ["amer"], "threshold_ms": 180}
    )
    assert response.status_code == 200
    data = response.json()
    assert "amer" in data
    assert data["amer"]["avg_latency"] == 174.01
    assert data["amer"]["p95_latency"] == 186.62
    assert data["amer"]["avg_uptime"] == 98.56
    assert data["amer"]["breaches"] == 1

def test_calculate_metrics_no_region():
    response = client.post(
        "/metrics",
        json={"regions": ["non-existent-region"], "threshold_ms": 100}
    )
    assert response.status_code == 200
    data = response.json()
    assert "non-existent-region" not in data