# f1_api/api/v1/sessions_routes.py

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ...services.trackmap_service import get_track_map
from ...services.replay_service import get_session_replay
from ...utils.validators import validate_query_params


sessions_bp = Blueprint("sessions_bp", __name__)


@sessions_bp.get("/<int:year>/<int:round_>/<string:session_code>/track")
def session_track_map(year: int, round_: int, session_code: str):
    """
    Return track map polyline (X/Y) for a session.
    Optional query param:
      - ?driver=VER  -> use that driver's fastest lap
    """
    params = validate_query_params(
        request.args,
        {
            "driver": {
                "type": str,
                "validator": lambda value: len(value) == 3 and value.isalpha(),
                "message": "driver must be a 3-letter driver code",
                "transform": str.upper,
                "default": None,
            }
        },
    )
    data = get_track_map(
        year, round_, session_code, driver_code=params.get("driver")
    )
    return jsonify(data)

@sessions_bp.get("/<int:year>/<int:round_>/<string:session_code>/replay")
def session_replay(year: int, round_: int, session_code: str):
    """
    Return lap-by-lap replay data for a session.

    Example:
    GET /api/v1/sessions/2024/1/R/replay
    """
    validate_query_params(request.args, {})
    data = get_session_replay(year, round_, session_code)
    return jsonify(data)
