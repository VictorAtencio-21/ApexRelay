# f1_api/__init__.py
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .config import get_config
from .extensions import cors, cache, limiter
from .utils.exceptions import APIError, DEFAULT_ERROR_CODES

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
    def _response(err: APIError):
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(APIError)
    def handle_api_error(err: APIError):
        return _response(err)

    @app.errorhandler(HTTPException)
    def handle_http_error(err: HTTPException):
        status_code = err.code or 500
        api_err = APIError(
            err.description or "An unexpected error occurred.",
            status_code=status_code,
            code=DEFAULT_ERROR_CODES.get(status_code),
        )
        return _response(api_err)

    @app.errorhandler(Exception)
    def handle_unexpected_error(err: Exception):
        app.logger.exception("Unhandled exception", exc_info=err)
        api_err = APIError(
            "An unexpected error occurred.",
            status_code=500,
            code=DEFAULT_ERROR_CODES.get(500),
        )
        return _response(api_err)

    return app
