"""OpenWeatherMap fallback.

Only reached when Open-Meteo fails, and only when a key is configured. It
supplies the same normalized snapshot, minus the richer hourly series.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from flask import current_app

from app.utils.exceptions import ExternalServiceError
from app.utils.http import HttpClient
from app.weather.providers.base import (
    CurrentWeather,
    Location,
    WeatherProvider,
    WeatherSnapshot,
)
from app.weather.weather_codes import describe_wind_direction

OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5"

# OpenWeather uses its own condition ids; this maps their groups onto the WMO
# codes the rest of the application already understands.
_GROUP_TO_WMO = {2: 95, 3: 51, 5: 61, 6: 71, 7: 45, 8: 3}
_CLEAR_CODE = 0


def _to_wmo(owm_id: int | None) -> int:
    if owm_id is None:
        return _CLEAR_CODE
    if owm_id == 800:
        return _CLEAR_CODE
    return _GROUP_TO_WMO.get(owm_id // 100, _CLEAR_CODE)


class OpenWeatherProvider(WeatherProvider):
    name = "openweathermap"

    @property
    def is_available(self) -> bool:
        return bool(current_app.config.get("OPENWEATHER_KEY"))

    def get_snapshot(self, location: Location) -> WeatherSnapshot:
        from app.weather.weather_codes import describe

        api_key = current_app.config.get("OPENWEATHER_KEY")
        if not api_key:
            raise ExternalServiceError("OpenWeatherMap nao esta configurado.")

        payload = self._request(location, api_key)
        main = payload.get("main", {})
        wind = payload.get("wind", {})
        weather_entry = (payload.get("weather") or [{}])[0]
        system = payload.get("sys", {})

        condition = describe(_to_wmo(weather_entry.get("id")))
        current = CurrentWeather(
            observed_at=datetime.now(timezone.utc),
            temperature=main.get("temp"),
            feels_like=main.get("feels_like"),
            temperature_min=main.get("temp_min"),
            temperature_max=main.get("temp_max"),
            humidity=main.get("humidity"),
            pressure=main.get("pressure"),
            wind_speed=wind.get("speed"),
            wind_direction=wind.get("deg"),
            wind_direction_label=describe_wind_direction(wind.get("deg")),
            uv_index=None,
            visibility=payload.get("visibility"),
            precipitation_probability=None,
            precipitation=(payload.get("rain") or {}).get("1h"),
            cloud_cover=(payload.get("clouds") or {}).get("all"),
            is_day=True,
            weather_code=condition.code,
            condition=condition.label,
            icon=condition.icon,
            sunrise=_from_unix(system.get("sunrise")),
            sunset=_from_unix(system.get("sunset")),
        )

        return WeatherSnapshot(location=location, current=current, provider=self.name)

    def _request(self, location: Location, api_key: str) -> dict[str, Any]:
        client = HttpClient(self.name, OPEN_WEATHER_URL)
        return client.get_json(
            "/weather",
            params={
                "lat": location.latitude,
                "lon": location.longitude,
                "appid": api_key,
                "units": "metric",
                "lang": "pt_br",
            },
        )


def _from_unix(value: int | None) -> datetime | None:
    return datetime.fromtimestamp(value, tz=timezone.utc) if value else None
