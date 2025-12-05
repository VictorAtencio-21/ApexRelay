# f1_api/services/sessions_service.py

from __future__ import annotations

from typing import Any

import fastf1
import pandas as pd

from ..extensions import cache

from ..utils.exceptions import APIError, DEFAULT_ERROR_CODES


# Map human-readable session names from FastF1 → short codes we will use in URLs
SESSION_NAME_TO_CODE = {
    "Practice 1": "FP1",
    "Practice 2": "FP2",
    "Practice 3": "FP3",
    "Free Practice 1": "FP1",
    "Free Practice 2": "FP2",
    "Free Practice 3": "FP3",
    "Qualifying": "Q",
    "Race": "R",
    "Sprint": "S",
    "Sprint Qualifying": "SQ",
    "Sprint Shootout": "SQ",
}


def _map_session_name_to_code(name: str | None) -> str | None:
    """Internal helper to convert FastF1 session names into short codes."""
    if not name:
        return None
    return SESSION_NAME_TO_CODE.get(name)


@cache.memoize()
def get_event_with_sessions(year: int, round_: int) -> dict[str, Any]:
    """
    Load a single event (race weekend) and extract its sessions.

    This uses fastf1.get_event(year, round_), which returns something like
    a single row of the schedule (pandas Series).
    """
    try:
        event = fastf1.get_event(year, round_)
    except Exception as exc:
        raise APIError(
            f"Unable to load event for {year} round {round_}",
            status_code=404,
            code=DEFAULT_ERROR_CODES.get(404),
        ) from exc

    base = {
        "year": int(year),
        "round": int(event["RoundNumber"]),
        "country": str(event["Country"]),
        "location": str(event["Location"]),
        "name": str(event["EventName"]),
        "official_name": str(event["OfficialEventName"]),
        "event_format": str(event["EventFormat"]),
        "event_date": event["EventDate"].isoformat()
        if not pd.isna(event["EventDate"])
        else None,
        "f1_api_support": bool(event.get("F1ApiSupport", False)),
    }

    sessions: list[dict[str, Any]] = []

    # FastF1 event has columns Session1..Session5 and Session1DateUtc..Session5DateUtc
    for i in range(1, 6):
        name_key = f"Session{i}"
        date_key = f"Session{i}DateUtc"

        name = event.get(name_key)
        if not isinstance(name, str) or not name.strip():
            continue  # skip empty sessions

        code = _map_session_name_to_code(name)
        start_utc = event.get(date_key)

        sessions.append(
            {
                "index": i,
                "name": name,        # e.g. "Practice 1"
                "code": code,        # e.g. "FP1" (what you use in URLs)
                "start_utc": start_utc.isoformat()
                if not pd.isna(start_utc)
                else None,
            }
        )

    base["sessions"] = sessions
    return base
