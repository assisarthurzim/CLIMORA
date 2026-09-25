"""Environment parsing rules.

These exist because a blank value in .env silently overrode a default and
broke token signing at runtime while the suite stayed green.
"""

import pytest

from app.config import (
    DEV_JWT_SECRET_KEY,
    BaseConfig,
    ConfigurationError,
    ProductionConfig,
    env,
    env_bool,
    env_int,
    env_list,
)


def test_blank_value_falls_back_to_the_default(monkeypatch):
    monkeypatch.setenv("CLIMORA_SAMPLE", "")

    assert env("CLIMORA_SAMPLE", "fallback") == "fallback"


def test_whitespace_only_value_falls_back_to_the_default(monkeypatch):
    monkeypatch.setenv("CLIMORA_SAMPLE", "   ")

    assert env("CLIMORA_SAMPLE", "fallback") == "fallback"


def test_real_value_wins_and_is_trimmed(monkeypatch):
    monkeypatch.setenv("CLIMORA_SAMPLE", "  actual  ")

    assert env("CLIMORA_SAMPLE", "fallback") == "actual"


def test_blank_integer_falls_back(monkeypatch):
    monkeypatch.setenv("CLIMORA_TIMEOUT", "")

    assert env_int("CLIMORA_TIMEOUT", 10) == 10


def test_invalid_integer_is_rejected_at_startup(monkeypatch):
    monkeypatch.setenv("CLIMORA_TIMEOUT", "dez")

    with pytest.raises(ConfigurationError):
        env_int("CLIMORA_TIMEOUT", 10)


def test_blank_list_falls_back(monkeypatch):
    monkeypatch.setenv("CLIMORA_ORIGINS", "")

    assert env_list("CLIMORA_ORIGINS", "http://localhost:5173") == ["http://localhost:5173"]


def test_boolean_accepts_common_spellings(monkeypatch):
    monkeypatch.setenv("CLIMORA_FLAG", "TRUE")
    assert env_bool("CLIMORA_FLAG", False) is True

    monkeypatch.setenv("CLIMORA_FLAG", "no")
    assert env_bool("CLIMORA_FLAG", True) is False


def test_signing_keys_are_long_enough_for_hs256():
    assert len(BaseConfig.JWT_SECRET_KEY) >= 32
    assert len(BaseConfig.SECRET_KEY) >= 32


def test_placeholder_secrets_are_reported():
    assert "JWT_SECRET_KEY" in BaseConfig.insecure_defaults()


def test_production_refuses_to_start_with_placeholder_secrets(monkeypatch):
    monkeypatch.setattr(ProductionConfig, "REQUIRED_SETTINGS", ("SECRET_KEY", "JWT_SECRET_KEY"))
    monkeypatch.setattr(ProductionConfig, "JWT_SECRET_KEY", DEV_JWT_SECRET_KEY)

    with pytest.raises(ConfigurationError, match="placeholders"):
        ProductionConfig.validate()


def test_ai_base_url_defaults_to_openai():
    from app.config import BaseConfig

    assert BaseConfig.AI_BASE_URL == "https://api.openai.com/v1"


def test_ai_base_url_can_point_to_another_vendor(monkeypatch):
    """Switching to Groq or OpenRouter must be configuration, not code."""
    from app.config import env

    monkeypatch.setenv("AI_BASE_URL", "https://api.groq.com/openai/v1")

    assert env("AI_BASE_URL", "https://api.openai.com/v1") == "https://api.groq.com/openai/v1"
