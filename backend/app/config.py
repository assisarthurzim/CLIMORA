"""Application configuration objects, selected per environment."""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Long enough to satisfy HS256 without triggering a weak-key warning. Local
# only: production refuses to start without real values.
DEV_SECRET_KEY = "climora-development-secret-key-not-for-production-use"
DEV_JWT_SECRET_KEY = "climora-development-jwt-secret-key-not-for-production-use"


class ConfigurationError(RuntimeError):
    """Raised when the environment is missing a mandatory setting."""


def env(name: str, default: str | None = None) -> str | None:
    """Read a variable, treating a blank value as absent.

    os.getenv only falls back when the name is undefined. A key left empty in
    .env would otherwise override the default with an empty string and fail
    much later, far from the cause.
    """
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


def env_int(name: str, default: int) -> int:
    value = env(name)
    try:
        return int(value) if value is not None else default
    except ValueError:
        raise ConfigurationError(f"{name} must be an integer, got {value!r}.") from None


def env_bool(name: str, default: bool) -> bool:
    value = env(name)
    return value.lower() in {"1", "true", "yes", "on"} if value is not None else default


def env_list(name: str, default: str) -> list[str]:
    return [item.strip() for item in (env(name, default) or "").split(",") if item.strip()]


class BaseConfig:
    ENV_NAME = "base"

    SECRET_KEY = env("SECRET_KEY", DEV_SECRET_KEY)
    JWT_SECRET_KEY = env("JWT_SECRET_KEY", DEV_JWT_SECRET_KEY)

    SQLALCHEMY_DATABASE_URI = env(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'weather.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES_REMEMBER = timedelta(days=30)
    JWT_ACCESS_COOKIE_PATH = "/api"
    JWT_REFRESH_COOKIE_PATH = "/api/v1/auth"

    CORS_ORIGINS = env_list("CORS_ORIGINS", "http://localhost:5173")

    RATELIMIT_STORAGE_URI = env("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "200 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_ENABLED = env_bool("RATELIMIT_ENABLED", True)

    OPENWEATHER_KEY = env("OPENWEATHER_KEY")
    OPENAI_KEY = env("OPENAI_KEY")

    NOMINATIM_USER_AGENT = env("NOMINATIM_USER_AGENT", "Climora/1.0")
    EXTERNAL_API_TIMEOUT = env_int("EXTERNAL_API_TIMEOUT", 10)
    AI_TIMEOUT = env_int("AI_TIMEOUT", 30)
    # Any OpenAI-compatible endpoint works here: OpenAI, Groq, OpenRouter,
    # a local Ollama, or anything else speaking /chat/completions.
    AI_BASE_URL = env("AI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = env("OPENAI_MODEL", "gpt-4o-mini")

    CACHE_TTL_CURRENT_WEATHER = 600
    CACHE_TTL_FORECAST = 1800
    CACHE_TTL_GEOCODING = 86_400
    CACHE_TTL_AIR_QUALITY = 1800

    LOG_LEVEL = env("LOG_LEVEL", "INFO")
    LOG_DIR = BASE_DIR / "logs"

    API_PREFIX = "/api/v1"

    REQUIRED_SETTINGS: tuple[str, ...] = ()

    @classmethod
    def validate(cls) -> None:
        """Fail fast when a mandatory setting is absent."""
        missing = [name for name in cls.REQUIRED_SETTINGS if not getattr(cls, name, None)]
        if missing:
            raise ConfigurationError(
                "Missing required environment variables: " + ", ".join(sorted(missing))
            )

    @classmethod
    def insecure_defaults(cls) -> list[str]:
        """Names of secrets still holding their development placeholder."""
        placeholders = {"SECRET_KEY": DEV_SECRET_KEY, "JWT_SECRET_KEY": DEV_JWT_SECRET_KEY}
        return [name for name, value in placeholders.items() if getattr(cls, name) == value]


class DevelopmentConfig(BaseConfig):
    ENV_NAME = "development"
    DEBUG = True


class TestingConfig(BaseConfig):
    ENV_NAME = "testing"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_COOKIE_CSRF_PROTECT = False
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    ENV_NAME = "production"
    DEBUG = False
    JWT_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    REQUIRED_SETTINGS = ("SECRET_KEY", "JWT_SECRET_KEY", "OPENAI_KEY")

    @classmethod
    def validate(cls) -> None:
        super().validate()
        insecure = cls.insecure_defaults()
        if insecure:
            raise ConfigurationError(
                "Development placeholders are not allowed in production: "
                + ", ".join(sorted(insecure))
            )


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[BaseConfig]:
    """Resolve a configuration class by name, falling back to the environment."""
    resolved = name or env("FLASK_ENV", "development")
    if resolved not in CONFIG_MAP:
        raise ConfigurationError(
            f"Unknown environment '{resolved}'. Expected one of: {', '.join(CONFIG_MAP)}"
        )
    return CONFIG_MAP[resolved]
