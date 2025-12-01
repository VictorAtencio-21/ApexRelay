# f1_api/services/fastf1_client.py

from __future__ import annotations

import os
from pathlib import Path

import fastf1

_fastf1_initialized = False


def init_fastf1(app) -> None:
    """
    Initialize FastF1 once for the whole app.

    - Reads the cache directory from app.config["FASTF1_CACHE_DIR"]
    - Creates the directory if it does not exist
    - Enables FastF1's on-disk cache
    """
    global _fastf1_initialized
    if _fastf1_initialized:
        return  # already initialized

    # 1) Get cache dir from config (or default)
    cache_dir = app.config.get("FASTF1_CACHE_DIR", "./fastf1_cache")

    # 2) Turn it into a Path object (nice for filesystem operations)
    cache_path = Path(cache_dir)

    # 3) Create the directory if needed (parents=True allows nested paths)
    cache_path.mkdir(parents=True, exist_ok=True)

    # 4) Enable FastF1 cache using this path
    fastf1.Cache.enable_cache(str(cache_path))

    _fastf1_initialized = True


def get_session(year: int, round_: int, session_code: str):
    """
    Convenience helper to load a FastF1 session.

    session_code examples: 'FP1', 'FP2', 'Q', 'R', 'S', 'SQ'
    """
    session = fastf1.get_session(year, round_, session_code)
    session.load()
    return session
