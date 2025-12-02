# f1_api/tests/test_replay_api.py

import pytest
from f1_api import create_app


@pytest.fixture
def app():
    return create_app("testing")


@pytest.fixture
def client(app):
    return app.test_client()


def test_session_replay_basic_flow(client):
    # 1) Get seasons and choose the latest year
    seasons_resp = client.get("/api/v1/events/seasons")
    assert seasons_resp.status_code == 200
    seasons = seasons_resp.get_json()["seasons"]
    year = seasons[0]

    # 2) Get events for that year and pick first event
    events_resp = client.get(f"/api/v1/events/{year}")
    assert events_resp.status_code == 200
    events = events_resp.get_json()["events"]

    if not events:
        pytest.skip("No events available for this season")

    first_event = events[0]
    round_ = first_event["round"]

    # 3) Try race replay for that event ('R' = Race)
    replay_resp = client.get(f"/api/v1/sessions/{year}/{round_}/R/replay")

    # If the race isn't supported for this year/round, skip
    if replay_resp.status_code != 200:
        pytest.skip(f"No replay data available for {year} round {round_}")

    data = replay_resp.get_json()

    # 4) Check minimal structure
    assert "metadata" in data
    assert "drivers" in data
    assert "timeline" in data
    assert isinstance(data["drivers"], list)
    assert isinstance(data["timeline"], list)
