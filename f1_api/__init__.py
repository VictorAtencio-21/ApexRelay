# f1_api/__init__.py
from flask import Flask

from .config import get_config
from .extensions import cors, cache, limiter
from .utils.exceptions import APIError

# Route blueprints
from .api.v1.races_routes import races_bp
from .api.v1.events_routes import events_bp
from .api.v1.sessions_routes import sessions_bp

# Services initialization
from .services.fastf1_client import init_fastf1 # initialize FastF1 client

def create_app(config_name: str | None = None) -> Flask:
    """
    Application factory.

    config_name: "development", "testing", "production", or None
                 (None → uses FLASK_ENV or defaults to development)
    """
    app = Flask(
        __name__,
        instance_relative_config=True,  # allows instance/ directory usage
    )

    # Load configuration class
    app.config.from_object(get_config(config_name))

    # Initialize extensions with this app instance
    cors.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    init_fastf1(app)  # Initialize FastF1 client

    # Register route blueprints (versioned) 
    app.register_blueprint(races_bp, url_prefix="/api/v1/races")
    app.register_blueprint(events_bp, url_prefix="/api/v1/events")
    app.register_blueprint(sessions_bp, url_prefix="/api/v1/sessions")

    # Register error handlers
    @app.errorhandler(APIError)
    def handle_api_error(err: APIError):
        return err.to_dict(), err.status_code

    return app
