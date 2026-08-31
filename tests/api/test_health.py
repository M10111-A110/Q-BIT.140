from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_get_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "qbit-api"


def test_get_root_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
