# f1_api/services/replay_service.py

from __future__ import annotations

from typing import Any

import pandas as pd

from .fastf1_client import get_session
from ..utils.exceptions import APIError


def _to_seconds(value) -> float | None:
    """
    Convert a pandas Timedelta (or similar) to seconds as float.
    Return None if the value is missing (NaT / NaN).
    """
    if pd.isna(value):
        return None
    # FastF1 uses pandas.Timedelta for Time/LapTime
    return float(value.total_seconds())


def get_session_replay(year: int, round_: int, session_code: str) -> dict[str, Any]:
    """
    Build a lap-based replay dataset for a session.

    - year: e.g. 2024
    - round_: e.g. 1
    - session_code: 'R', 'Q', 'FP1', etc.
    """
    try:
        session = get_session(year, round_, session_code)
    except Exception as exc:
        # If FastF1 can't load this session, turn it into a clean API error
        raise APIError(
            f"Unable to load session {year} round {round_} ({session_code})",
            status_code=404,
            code="session_not_found",
        ) from exc

    laps = session.laps  # Laps DataFrame with all laps in the session

    # If FastF1 has no laps (e.g. cancelled session), return an empty timeline
    if laps.empty:
        return {
            "metadata": {
                "year": year,
                "round": round_,
                "session_code": session_code,
                "event_name": session.event["EventName"],
                "country": session.event["Country"],
                "location": session.event["Location"],
            },
            "drivers": [],
            "timeline": [],
        }

    # 1) Build driver metadata list
    drivers_meta: list[dict[str, Any]] = []
    for drv_number in session.drivers:
        info = session.get_driver(drv_number)
        drivers_meta.append(
            {
                "driver_id": str(drv_number),
                "code": str(info["Abbreviation"]),
                "name": f"{info['FirstName']} {info['LastName']}",
                "team": str(info["TeamName"]),
            }
        )

    # 2) Build lap-by-lap timeline
    timeline: list[dict[str, Any]] = []

    # Group all rows by LapNumber → each group is one lap across all drivers
    for lap_number, group in laps.groupby("LapNumber"):
        group = group.copy()

        # Sort drivers in the lap: ideally by 'Position'; fallback to 'LapTime'
        if "Position" in group.columns:
            group = group.sort_values("Position")
        else:
            group = group.sort_values("LapTime")

        # Leader = first row after sorting
        leader_time = group.iloc[0]["Time"] if "Time" in group.columns else None
        leader_time_s = _to_seconds(leader_time)

        driver_timings: list[dict[str, Any]] = []
        prev_time_s = leader_time_s

        # Iterate over each driver's row for this lap
        for _, row in group.iterrows():
            lap_time_s = _to_seconds(row.get("LapTime"))
            end_time_s = _to_seconds(row.get("Time"))

            # Gap to leader: difference in 'Time' from leader's Time
            gap_to_leader = None
            if leader_time_s is not None and end_time_s is not None:
                gap_to_leader = end_time_s - leader_time_s

            # Interval to car in front: difference from previous car in order
            interval_to_front = None
            if prev_time_s is not None and end_time_s is not None:
                interval_to_front = end_time_s - prev_time_s

            driver_timings.append(
                {
                    "driver_id": str(row.get("DriverNumber")),
                    "driver_code": str(row.get("Driver")),
                    "position": int(row["Position"])
                    if "Position" in row and not pd.isna(row["Position"])
                    else None,
                    "lap_time_s": lap_time_s,
                    "gap_to_leader_s": gap_to_leader,
                    "interval_to_front_s": interval_to_front,
                }
            )

            prev_time_s = end_time_s

        timeline.append(
            {
                "lap": int(lap_number),
                "driver_timings": driver_timings,
            }
        )

    return {
        "metadata": {
            "year": year,
            "round": round_,
            "session_code": session_code,
            "event_name": session.event["EventName"],
            "country": session.event["Country"],
            "location": session.event["Location"],
        },
        "drivers": drivers_meta,
        "timeline": timeline,
    }
