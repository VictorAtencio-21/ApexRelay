# f1_api/services/events_service.py

from __future__ import annotations

import datetime as dt
from typing import Any

import fastf1
import pandas as pd

from ..utils.exceptions import APIError, DEFAULT_ERROR_CODES


def get_current_and_previous_seasons() -> list[int]:
    """
    Return [current_year, previous_year].
    Example: if today is 2025, this returns [2025, 2024].
    """
    current_year = dt.date.today().year
    return [current_year, current_year - 1]


def get_season_events(year: int) -> list[dict[str, Any]]:
    """
    Use FastF1 to fetch the race calendar for a given year.

    Returns a list of simplified event dicts that your frontend can consume.
    """
    # This returns an EventSchedule (pandas DataFrame)
    try:
        schedule = fastf1.get_event_schedule(
            year,
            include_testing=False,  # ignore preseason / test events for now
        )
    except Exception as exc:
        raise APIError(
            f"Unable to load schedule for {year}",
            status_code=502,
            code=DEFAULT_ERROR_CODES.get(502),
        ) from exc

    events: list[dict[str, Any]] = []

    # schedule.iterrows() gives you (index, row) where row behaves like a dict
    for _, event in schedule.iterrows():
        events.append(
            {
                "year": int(year),
                "round": int(event["RoundNumber"]),
                "country": str(event["Country"]),
                "location": str(event["Location"]),
                "name": str(event["EventName"]),
                "official_name": str(event["OfficialEventName"]),
                "event_format": str(event["EventFormat"]),  # "conventional" / "sprint"
                "event_date": event["EventDate"].isoformat()
                if not pd.isna(event["EventDate"])
                else None,
                "f1_api_support": bool(event.get("F1ApiSupport", False)),
            }
        )

    return events
