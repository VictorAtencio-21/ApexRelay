# f1_api/tests/test_events_api.py

import pytest
from f1_api import create_app


@pytest.fixture
def app():
    # Use testing configuration (no real cache if you want)
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_seasons(client):
    resp = client.get("/api/v1/events/seasons")

    assert resp.status_code == 200
    data = resp.get_json()

    assert "seasons" in data
    assert isinstance(data["seasons"], list)
    assert len(data["seasons"]) >= 2  # current + previous


def test_get_season_events(client):
    # First, get seasons
    seasons_resp = client.get("/api/v1/events/seasons")
    seasons = seasons_resp.get_json()["seasons"]
    year = seasons[0]

    resp = client.get(f"/api/v1/events/{year}")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["year"] == year
    assert "events" in data
    assert isinstance(data["events"], list)


def test_get_event_with_sessions(client):
    # Get seasons and choose a year
    seasons_resp = client.get("/api/v1/events/seasons")
    seasons = seasons_resp.get_json()["seasons"]
    year = seasons[0]

    # Get events for that year
    events_resp = client.get(f"/api/v1/events/{year}")
    events = events_resp.get_json()["events"]

    # If there are no events, skip the test
    if not events:
        pytest.skip("No events available for this season")

    first_event = events[0]
    round_ = first_event["round"]

    resp = client.get(f"/api/v1/events/{year}/{round_}")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["year"] == year
    assert data["round"] == round_
    assert "sessions" in data
    assert isinstance(data["sessions"], list)
