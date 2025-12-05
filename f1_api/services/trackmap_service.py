# f1_api/services/trackmap_service.py

from __future__ import annotations

from typing import Any

from .fastf1_client import get_session
from ..utils.exceptions import APIError, DEFAULT_ERROR_CODES


def get_track_map(
    year: int,
    round_: int,
    session_code: str,
    driver_code: str | None = None,
) -> dict[str, Any]:
    """
    Return X/Y coordinates for the track map polyline.

    - If driver_code is provided, use that driver's fastest lap.
    - Otherwise, use the overall fastest lap in the session.
    """
    try:
        session = get_session(year, round_, session_code)
    except Exception as exc:
        raise APIError(
            f"Unable to load session {year} round {round_} ({session_code})",
            status_code=404,
            code=DEFAULT_ERROR_CODES.get(404),
        ) from exc

    # Choose which laps to consider
    if driver_code:
        laps = session.laps.pick_driver(driver_code)
        if laps.empty:
            raise APIError(
                f"No laps found for driver {driver_code}",
                status_code=404,
                code="driver_laps_not_found",
            )
        lap = laps.pick_fastest()
    else:
        # Overall fastest lap in the entire session
        lap = session.laps.pick_fastest()

    # Telemetry for that lap; contains X and Y among other columns
    if lap is None:
        raise APIError(
            "No lap found for the specified session/driver",
            status_code=404,
            code="lap_not_found",
        )
    tel = lap.get_telemetry()
    if tel is None:
        raise APIError(
            "Telemetry is not available for the selected lap",
            status_code=404,
            code="telemetry_unavailable",
        )

    # Convert to plain Python lists for JSON
    x = tel["X"].astype(float).tolist()
    y = tel["Y"].astype(float).tolist()

    return {
        "year": year,
        "round": round_,
        "session_code": session_code,
        "driver": driver_code or lap["Driver"],
        "polyline": {
            "x": x,
            "y": y,
        },
    }
