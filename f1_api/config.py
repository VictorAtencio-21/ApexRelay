# f1_api/config.py
import os


class BaseConfig:
    """Shared configuration for all environments."""

    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False  # keep JSON keys in the order we return them

    # Example of something we might need later:
    # Where to put FastF1 cache on disk
    FASTF1_CACHE_DIR = os.getenv("FASTF1_CACHE_DIR", "./fastf1_cache")

    # Flask-Caching: by default, simple in-memory cache
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = 300  # seconds

    # Rate limiting default (we'll use this with flask-limiter)
    RATELIMIT_DEFAULT = "60/minute"


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    CACHE_TYPE = "NullCache"  # no caching during tests


class ProductionConfig(BaseConfig):
    """Production-safe defaults."""
    RATELIMIT_DEFAULT = "1000/hour"


def get_config(name: str | None):
    """Return the config class based on a name or FLASK_ENV env var."""
    name = (name or os.getenv("FLASK_ENV", "development")).lower()
    if name == "production":
        return ProductionConfig
    if name == "testing":
        return TestingConfig
    return DevelopmentConfig
