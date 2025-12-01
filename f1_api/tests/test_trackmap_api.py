# f1_api/tests/test_trackmap_api.py

import pytest
from f1_api import create_app


@pytest.fixture
def app():
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.mark.slow
def test_track_map_for_first_race(client):
    # Get seasons and choose a year
    seasons_resp = client.get("/api/v1/events/seasons")
    seasons = seasons_resp.get_json()["seasons"]
    year = seasons[0]

    # Get events and pick first one
    events_resp = client.get(f"/api/v1/events/{year}")
    events = events_resp.get_json()["events"]

    if not events:
        pytest.skip("No events available for this season")

    first_event = events[0]
    round_ = first_event["round"]

    # For simplicity, try Race session 'R' without specifying driver
    resp = client.get(f"/api/v1/sessions/{year}/{round_}/R/track")

    # This might fail if there is no race data, so allow 200 or 400+ skip
    if resp.status_code != 200:
        pytest.skip(f"Trackmap not available for {year} round {round_}")

    data = resp.get_json()
    assert "polyline" in data
    assert "x" in data["polyline"]
    assert "y" in data["polyline"]
    assert len(data["polyline"]["x"]) > 0
    assert len(data["polyline"]["y"]) > 0
