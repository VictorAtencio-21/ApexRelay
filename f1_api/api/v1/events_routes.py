# f1_api/api/v1/events_routes.py

from __future__ import annotations

from flask import Blueprint, jsonify

from ...services.events_service import (
    get_current_and_previous_seasons,
    get_season_events,
)
from ...services.sessions_service import get_event_with_sessions

events_bp = Blueprint("events_bp", __name__)


@events_bp.get("/seasons")
def seasons_index():
    """
    Return the current and previous seasons.
    Example: { "seasons": [2025, 2024] }
    """
    seasons = get_current_and_previous_seasons()
    return jsonify({"seasons": seasons})


@events_bp.get("/<int:year>")
def season_events(year: int):
    """
    Return the race calendar for a given year.
    """
    events = get_season_events(year)
    return jsonify({"year": year, "events": events})


@events_bp.get("/<int:year>/<int:round_>")
def event_detail(year: int, round_: int):
    """
    Return a single event (race weekend) and its sessions.
    """
    data = get_event_with_sessions(year, round_)
    return jsonify(data)
