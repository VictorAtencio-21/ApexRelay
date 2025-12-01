# f1_api/api/v1/sessions_routes.py

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ...services.trackmap_service import get_track_map

sessions_bp = Blueprint("sessions_bp", __name__)


@sessions_bp.get("/<int:year>/<int:round_>/<string:session_code>/track")
def session_track_map(year: int, round_: int, session_code: str):
    """
    Return track map polyline (X/Y) for a session.
    Optional query param:
      - ?driver=VER  -> use that driver's fastest lap
    """
    driver = request.args.get("driver")  # may be None
    data = get_track_map(year, round_, session_code, driver_code=driver)
    return jsonify(data)
