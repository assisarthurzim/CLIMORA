"""Open-Meteo: forecast, geocoding and air quality.

Free, keyless and without a practical rate limit, which makes it the primary
source for every weather lookup.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.utils.http import HttpClient
from app.weather.providers.base import (
    AirQuality,
    AirQualityProvider,
    CurrentWeather,
    DailyPoint,
    GeocodingProvider,
    HourlyPoint,
    Location,
    WeatherProvider,
    WeatherSnapshot,
)
from app.weather.weather_codes import describe, describe_wind_direction

FORECAST_URL = "https://api.open-meteo.com/v1"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1"

CURRENT_FIELDS = (
    "temperature_2m,apparent_temperature,relative_humidity_2m,surface_pressure,"
    "wind_speed_10m,wind_direction_10m,precipitation,cloud_cover,is_day,weather_code"
)
HOURLY_FIELDS = (
    "temperature_2m,apparent_temperature,precipitation_probability,precipitation,"
    "relative_humidity_2m,surface_pressure,wind_speed_10m,uv_index,visibility,weather_code"
)
DAILY_FIELDS = (
    "temperature_2m_min,temperature_2m_max,precipitation_sum,precipitation_probability_max,"
    "wind_speed_10m_max,uv_index_max,sunrise,sunset,weather_code"
)

FORECAST_DAYS = 7
HOURLY_POINTS = 48
# One past day lets the assistant answer "está mais frio que ontem?" from
# data rather than inference.
PAST_DAYS = 1

# European AQI bands, in ascending order of concern.
AQI_CATEGORIES = (
    (20, "Boa"),
    (40, "Razoável"),
    (60, "Moderada"),
    (80, "Ruim"),
    (100, "Muito ruim"),
)
AQI_WORST_CATEGORY = "Extremamente ruim"
AQI_UNKNOWN_CATEGORY = "Indisponível"

# GeoNames feature codes for populated places all start with PPL. Filtering on
# them keeps countries, regions and rivers out of a city search.
POPULATED_PLACE_PREFIX = "PPL"


def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def split_past_days(days: list[Any], reference: datetime | None) -> tuple[Any, list[Any]]:
    """Separate yesterday from the forecast that starts today."""
    if not days:
        return None, []

    today = (reference or datetime.now()).date()
    upcoming = [day for day in days if day.date is not None and day.date >= today]
    past = [day for day in days if day.date is not None and day.date < today]

    return (past[-1] if past else None), (upcoming or days)


def find_current_hour_index(points: list[Any], reference: datetime | None) -> int:
    """Index of the first hourly point at or after the current hour.

    Open-Meteo returns the hourly series from midnight, not from now. Without
    this the forecast would open in the past and the derived current values
    would be read off the wrong hour.
    """
    if reference is None or not points:
        return 0

    current_hour = reference.replace(minute=0, second=0, microsecond=0)
    for index, point in enumerate(points):
        if point.time is not None and point.time >= current_hour:
            return index
    return 0


def _at(series: list[Any] | None, index: int) -> Any:
    """Open-Meteo returns parallel arrays that may be short or absent."""
    if not series or index >= len(series):
        return None
    return series[index]


class OpenMeteoProvider(WeatherProvider):
    name = "open-meteo"

    def __init__(self) -> None:
        self._client = HttpClient(self.name, FORECAST_URL)

    def get_snapshot(self, location: Location) -> WeatherSnapshot:
        payload = self._client.get_json(
            "/forecast",
            params={
                "latitude": location.latitude,
                "longitude": location.longitude,
                "current": CURRENT_FIELDS,
                "hourly": HOURLY_FIELDS,
                "daily": DAILY_FIELDS,
                "forecast_days": FORECAST_DAYS,
                "past_days": PAST_DAYS,
                "timezone": location.timezone or "auto",
            },
        )

        raw_current = payload.get("current", {})

        # With past_days the daily series starts yesterday, so it is split
        # before anything downstream reads daily[0] as today.
        all_daily = self._parse_daily(payload.get("daily", {}))
        current_time = _parse_datetime(raw_current.get("time"))
        previous_day, daily = split_past_days(all_daily, current_time)

        # The series is trimmed to start at the current hour so both the chart
        # and the derived current values look forward, not back.
        full_hourly = self._parse_hourly(payload.get("hourly", {}))
        start = find_current_hour_index(full_hourly, current_time)
        hourly = full_hourly[start : start + HOURLY_POINTS]

        current = self._parse_current(raw_current, hourly, daily)

        return WeatherSnapshot(
            location=location,
            current=current,
            hourly=hourly,
            daily=daily,
            previous_day=previous_day,
            provider=self.name,
        )

    def _parse_current(
        self, raw: dict[str, Any], hourly: list[HourlyPoint], daily: list[DailyPoint]
    ) -> CurrentWeather:
        condition = describe(raw.get("weather_code"))
        today = daily[0] if daily else None
        # The current block carries no UV, visibility or rain chance, so the
        # nearest hourly point supplies them.
        reference_hour = hourly[0] if hourly else None

        return CurrentWeather(
            observed_at=_parse_datetime(raw.get("time")) or datetime.now(),
            temperature=raw.get("temperature_2m"),
            feels_like=raw.get("apparent_temperature"),
            temperature_min=today.temperature_min if today else None,
            temperature_max=today.temperature_max if today else None,
            humidity=raw.get("relative_humidity_2m"),
            pressure=raw.get("surface_pressure"),
            wind_speed=raw.get("wind_speed_10m"),
            wind_direction=raw.get("wind_direction_10m"),
            wind_direction_label=describe_wind_direction(raw.get("wind_direction_10m")),
            uv_index=reference_hour.uv_index if reference_hour else None,
            visibility=reference_hour.visibility if reference_hour else None,
            precipitation_probability=(
                reference_hour.precipitation_probability if reference_hour else None
            ),
            precipitation=raw.get("precipitation"),
            cloud_cover=raw.get("cloud_cover"),
            is_day=bool(raw.get("is_day", 1)),
            weather_code=condition.code,
            condition=condition.label,
            icon=condition.icon,
            sunrise=today.sunrise if today else None,
            sunset=today.sunset if today else None,
        )

    def _parse_hourly(self, raw: dict[str, Any]) -> list[HourlyPoint]:
        times = raw.get("time") or []
        points: list[HourlyPoint] = []

        for index in range(len(times)):
            condition = describe(_at(raw.get("weather_code"), index))
            points.append(
                HourlyPoint(
                    time=_parse_datetime(times[index]),
                    temperature=_at(raw.get("temperature_2m"), index),
                    feels_like=_at(raw.get("apparent_temperature"), index),
                    precipitation_probability=_at(raw.get("precipitation_probability"), index),
                    precipitation=_at(raw.get("precipitation"), index),
                    humidity=_at(raw.get("relative_humidity_2m"), index),
                    pressure=_at(raw.get("surface_pressure"), index),
                    wind_speed=_at(raw.get("wind_speed_10m"), index),
                    uv_index=_at(raw.get("uv_index"), index),
                    visibility=_at(raw.get("visibility"), index),
                    weather_code=condition.code,
                    condition=condition.label,
                    icon=condition.icon,
                )
            )
        return points

    def _parse_daily(self, raw: dict[str, Any]) -> list[DailyPoint]:
        dates = raw.get("time") or []
        points: list[DailyPoint] = []

        for index in range(len(dates)):
            condition = describe(_at(raw.get("weather_code"), index))
            points.append(
                DailyPoint(
                    date=_parse_date(dates[index]),
                    temperature_min=_at(raw.get("temperature_2m_min"), index),
                    temperature_max=_at(raw.get("temperature_2m_max"), index),
                    precipitation_sum=_at(raw.get("precipitation_sum"), index),
                    precipitation_probability_max=_at(
                        raw.get("precipitation_probability_max"), index
                    ),
                    wind_speed_max=_at(raw.get("wind_speed_10m_max"), index),
                    uv_index_max=_at(raw.get("uv_index_max"), index),
                    sunrise=_parse_datetime(_at(raw.get("sunrise"), index)),
                    sunset=_parse_datetime(_at(raw.get("sunset"), index)),
                    weather_code=condition.code,
                    condition=condition.label,
                    icon=condition.icon,
                )
            )
        return points


class OpenMeteoGeocoder(GeocodingProvider):
    name = "open-meteo-geocoding"

    def __init__(self) -> None:
        self._client = HttpClient(self.name, GEOCODING_URL)

    def search(self, query: str, limit: int = 5) -> list[Location]:
        # Over-fetch so filtering out non-cities still leaves a full page.
        payload = self._client.get_json(
            "/search",
            params={"name": query, "count": limit * 3, "language": "pt", "format": "json"},
        )
        results = payload.get("results") or []
        return [self._to_location(item) for item in prefer_cities(results)[:limit]]

    def reverse(self, latitude: float, longitude: float) -> Location | None:
        # Open-Meteo offers no reverse lookup; Nominatim covers this case.
        return None

    @staticmethod
    def _to_location(item: dict[str, Any]) -> Location:
        return Location(
            name=item.get("name", ""),
            latitude=item["latitude"],
            longitude=item["longitude"],
            state=item.get("admin1"),
            country=item.get("country"),
            country_code=item.get("country_code"),
            timezone=item.get("timezone"),
            population=item.get("population"),
        )


class OpenMeteoAirQuality(AirQualityProvider):
    name = "open-meteo-air-quality"

    def __init__(self) -> None:
        self._client = HttpClient(self.name, AIR_QUALITY_URL)

    def get_air_quality(self, latitude: float, longitude: float) -> AirQuality | None:
        payload = self._client.get_json(
            "/air-quality",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "european_aqi,pm2_5,pm10,ozone,nitrogen_dioxide",
            },
        )
        current = payload.get("current")
        if not current:
            return None

        index = current.get("european_aqi")
        return AirQuality(
            index=index,
            category=classify_air_quality(index),
            pm2_5=current.get("pm2_5"),
            pm10=current.get("pm10"),
            ozone=current.get("ozone"),
            nitrogen_dioxide=current.get("nitrogen_dioxide"),
        )


def prefer_cities(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep only populated places, unless that would leave nothing.

    A weather app searching "Bósnia" wants Sarajevo, not the country. But an
    obscure query that only matches a region should still return it.
    """
    cities = [
        item
        for item in results
        if str(item.get("feature_code", "")).startswith(POPULATED_PLACE_PREFIX)
    ]
    return cities or results


def classify_air_quality(index: int | float | None) -> str:
    if index is None:
        return AQI_UNKNOWN_CATEGORY
    for threshold, label in AQI_CATEGORIES:
        if index <= threshold:
            return label
    return AQI_WORST_CATEGORY
