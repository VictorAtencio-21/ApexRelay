# f1_api/tests/test_races_api.py
import pytest
from f1_api import create_app


@pytest.fixture
def app():
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_endpoint(client):
    resp = client.get("/api/v1/races/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "races"


def test_health_rejects_query_params(client):
    resp = client.get("/api/v1/races/health?foo=bar")

    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "invalid_query_params"
    assert "unexpected" in data["error"].get("details", {})
