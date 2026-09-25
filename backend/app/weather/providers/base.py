"""Provider contracts and the normalized shapes every provider must produce.

Upstream APIs disagree on field names, units and structure. These DTOs are the
only vocabulary the rest of the application knows, so swapping a provider never
reaches the services above.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any

from app.utils.geo import build_location_key


@dataclass(frozen=True, slots=True)
class Location:
    name: str
    latitude: float
    longitude: float
    state: str | None = None
    country: str | None = None
    country_code: str | None = None
    timezone: str | None = None
    population: int | None = None

    @property
    def location_key(self) -> str:
        return build_location_key(self.latitude, self.longitude)

    @property
    def display_name(self) -> str:
        parts = [self.name, self.state, self.country]
        return ", ".join(part for part in parts if part)

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "location_key": self.location_key, "display_name": self.display_name}


@dataclass(frozen=True, slots=True)
class CurrentWeather:
    observed_at: datetime
    temperature: float | None
    feels_like: float | None
    temperature_min: float | None
    temperature_max: float | None
    humidity: int | None
    pressure: float | None
    wind_speed: float | None
    wind_direction: int | None
    wind_direction_label: str | None
    uv_index: float | None
    visibility: float | None
    precipitation_probability: int | None
    precipitation: float | None
    cloud_cover: int | None
    is_day: bool
    weather_code: int
    condition: str
    icon: str
    sunrise: datetime | None = None
    sunset: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class HourlyPoint:
    time: datetime
    temperature: float | None
    feels_like: float | None
    precipitation_probability: int | None
    precipitation: float | None
    humidity: int | None
    pressure: float | None
    wind_speed: float | None
    uv_index: float | None
    visibility: float | None
    weather_code: int
    condition: str
    icon: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class DailyPoint:
    date: date
    temperature_min: float | None
    temperature_max: float | None
    precipitation_sum: float | None
    precipitation_probability_max: int | None
    wind_speed_max: float | None
    uv_index_max: float | None
    sunrise: datetime | None
    sunset: datetime | None
    weather_code: int
    condition: str
    icon: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class AirQuality:
    index: int | None
    category: str
    pm2_5: float | None = None
    pm10: float | None = None
    ozone: float | None = None
    nitrogen_dioxide: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return _serialize(asdict(self))


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    """Everything one location lookup produces, from a single provider call."""

    location: Location
    current: CurrentWeather
    hourly: list[HourlyPoint] = field(default_factory=list)
    daily: list[DailyPoint] = field(default_factory=list)
    air_quality: AirQuality | None = None
    previous_day: DailyPoint | None = None
    provider: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location.to_dict(),
            "current": self.current.to_dict(),
            "hourly": [point.to_dict() for point in self.hourly],
            "daily": [point.to_dict() for point in self.daily],
            "air_quality": self.air_quality.to_dict() if self.air_quality else None,
            "previous_day": self.previous_day.to_dict() if self.previous_day else None,
            "provider": self.provider,
        }


def _serialize(payload: dict[str, Any]) -> dict[str, Any]:
    """Render dates and times as ISO strings for JSON transport."""
    return {
        key: value.isoformat() if isinstance(value, (datetime, date)) else value
        for key, value in payload.items()
    }


class WeatherProvider(ABC):
    """Source of forecast data for a coordinate pair."""

    name: str

    @abstractmethod
    def get_snapshot(self, location: Location) -> WeatherSnapshot: ...


class GeocodingProvider(ABC):
    """Source of place lookups by name or by coordinate."""

    name: str

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[Location]: ...

    @abstractmethod
    def reverse(self, latitude: float, longitude: float) -> Location | None: ...


class AirQualityProvider(ABC):
    name: str

    @abstractmethod
    def get_air_quality(self, latitude: float, longitude: float) -> AirQuality | None: ...
