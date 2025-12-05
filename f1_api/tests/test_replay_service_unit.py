# f1_api/tests/test_replay_service_unit.py

from __future__ import annotations

import pandas as pd

from f1_api.services import replay_service


class _StubSession:
    """Lightweight stand-in for a FastF1 session."""

    def __init__(self):
        self.drivers = [44, 1]
        self.event = {
            "EventName": "Test GP",
            "Country": "Somewhere",
            "Location": "Race City",
        }

        self._drivers_data = {
            44: {
                "Abbreviation": "HAM",
                "FirstName": "Lewis",
                "LastName": "Hamilton",
                "TeamName": "Mercedes",
            },
            1: {
                "Abbreviation": "VER",
                "FirstName": "Max",
                "LastName": "Verstappen",
                "TeamName": "Red Bull",
            },
        }

        self.laps = pd.DataFrame(
            [
                {
                    "LapNumber": 1,
                    "DriverNumber": 44,
                    "Driver": "HAM",
                    "Position": 1,
                    "LapTime": pd.Timedelta(seconds=90),
                    "Time": pd.Timedelta(seconds=0),
                },
                {
                    "LapNumber": 1,
                    "DriverNumber": 1,
                    "Driver": "VER",
                    "Position": 2,
                    "LapTime": pd.Timedelta(seconds=91),
                    "Time": pd.Timedelta(seconds=1),
                },
                {
                    "LapNumber": 2,
                    "DriverNumber": 44,
                    "Driver": "HAM",
                    "Position": 1,
                    "LapTime": pd.Timedelta(seconds=89.5),
                    "Time": pd.Timedelta(seconds=90),
                },
                {
                    "LapNumber": 2,
                    "DriverNumber": 1,
                    "Driver": "VER",
                    "Position": 2,
                    "LapTime": pd.NaT,
                    "Time": pd.NaT,
                },
            ]
        )

    def get_driver(self, driver_number):
        return self._drivers_data[driver_number]


def test_replay_response_formats_missing_values(monkeypatch):
    """Replay payload should omit NaN values and give leader no interval gap."""

    def _fake_get_session(year, round_, code):
        assert (year, round_, code) == (2024, 1, "R")
        return _StubSession()

    monkeypatch.setattr(replay_service, "get_session", _fake_get_session)

    data = replay_service.get_session_replay(2024, 1, "R")

    assert data["metadata"] == {
        "year": 2024,
        "round": 1,
        "session_code": "R",
        "event_name": "Test GP",
        "country": "Somewhere",
        "location": "Race City",
    }

    assert data["drivers"] == [
        {
            "driver_id": "44",
            "code": "HAM",
            "name": "Lewis Hamilton",
            "team": "Mercedes",
        },
        {
            "driver_id": "1",
            "code": "VER",
            "name": "Max Verstappen",
            "team": "Red Bull",
        },
    ]

    lap1 = data["timeline"][0]["driver_timings"]
    assert lap1[0]["interval_to_front_s"] is None  # leader has no front gap
    assert lap1[0]["gap_to_leader_s"] == 0.0
    assert lap1[1]["gap_to_leader_s"] == 1.0
    assert lap1[1]["interval_to_front_s"] == 1.0

    lap2_driver2 = data["timeline"][1]["driver_timings"][1]
    assert lap2_driver2["lap_time_s"] is None
    assert lap2_driver2["gap_to_leader_s"] is None
    assert lap2_driver2["driver_code"] == "VER"
