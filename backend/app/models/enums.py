"""Enumerations persisted as constrained strings."""

from __future__ import annotations

from enum import StrEnum


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class SearchSource(StrEnum):
    MANUAL = "manual"
    FAVORITE = "favorite"
    GEOLOCATION = "geolocation"


class TemperatureUnit(StrEnum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class WindSpeedUnit(StrEnum):
    KMH = "kmh"
    MS = "ms"
    MPH = "mph"


class ThemePreference(StrEnum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"
