"""Application factory."""

from __future__ import annotations

from flask import Flask

from app.auth.jwt_callbacks import register_jwt_callbacks
from app.config import BaseConfig, get_config
from app.extensions import cors, db, jwt, limiter, migrate
from app.middleware.error_handler import register_error_handlers, register_jwt_handlers
from app.middleware.request_logger import register_request_logging
from app.middleware.security import register_security_headers
from app.utils.logger import configure_logging


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    config_class = get_config(config_name)
    config_class.validate()
    app.config.from_object(config_class)

    configure_logging(app)
    _register_extensions(app)
    _register_blueprints(app)

    register_request_logging(app)
    register_security_headers(app)
    register_jwt_callbacks(app)
    register_jwt_handlers(app)
    register_error_handlers(app)

    app.logger.info("Climora started in %s mode", app.config["ENV_NAME"])
    _warn_about_placeholders(app, config_class)
    return app


def _warn_about_placeholders(app: Flask, config_class: type[BaseConfig]) -> None:
    """Make it obvious when secrets were never filled in."""
    insecure = config_class.insecure_defaults()
    if insecure and not app.config.get("TESTING"):
        app.logger.warning(
            "Using development placeholders for %s. Generate real values with: "
            'python -c "import secrets; print(secrets.token_hex(32))"',
            ", ".join(sorted(insecure)),
        )


def _register_extensions(app: Flask) -> None:
    # Importing the registry binds every mapper before Migrate inspects
    # the metadata, and installs the SQLite foreign-key pragma.
    from app import models  # noqa: F401
    from app.models import events  # noqa: F401

    db.init_app(app)
    # render_as_batch lets Alembic alter tables on SQLite.
    migrate.init_app(app, db, render_as_batch=True)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )


def _register_blueprints(app: Flask) -> None:
    """Mount every domain blueprint under the versioned API prefix."""
    from app.ai.routes import ai_bp
    from app.auth.routes import auth_bp
    from app.favorites.routes import favorites_bp
    from app.history.routes import history_bp
    from app.insights.routes import insights_bp
    from app.profile.routes import profile_bp
    from app.system.routes import system_bp
    from app.weather.routes import weather_bp

    prefix: str = app.config["API_PREFIX"]
    app.register_blueprint(system_bp, url_prefix=f"{prefix}/system")
    app.register_blueprint(auth_bp, url_prefix=f"{prefix}/auth")
    app.register_blueprint(weather_bp, url_prefix=f"{prefix}/weather")
    app.register_blueprint(favorites_bp, url_prefix=f"{prefix}/favorites")
    app.register_blueprint(history_bp, url_prefix=f"{prefix}/history")
    app.register_blueprint(insights_bp, url_prefix=f"{prefix}/insights")
    app.register_blueprint(ai_bp, url_prefix=f"{prefix}/ai")
    app.register_blueprint(profile_bp, url_prefix=f"{prefix}/profile")


__all__ = ["create_app", "BaseConfig"]
