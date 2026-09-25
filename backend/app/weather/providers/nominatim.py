"""Nominatim geocoding.

Used for reverse lookups and as a fallback when Open-Meteo finds nothing. Its
usage policy caps requests at one per second and requires an identifying
User-Agent, so calls are throttled here rather than trusted to callers.
"""

from __future__ import annotations

import threading
import time
from typing import Any

from flask import current_app

from app.utils.http import HttpClient
from app.weather.providers.base import GeocodingProvider, Location

NOMINATIM_URL = "https://nominatim.openstreetmap.org"
MIN_INTERVAL_SECONDS = 1.0

# Nominatim reports the settlement under one of several keys depending on the
# place type, from most to least specific.
PLACE_KEYS = ("city", "town", "village", "municipality", "county")


class _RateGate:
    """Serializes calls so the one-per-second policy is never breached."""

    def __init__(self, min_interval: float) -> None:
        self._min_interval = min_interval
        self._last_call = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            elapsed = time.monotonic() - self._last_call
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_call = time.monotonic()


class NominatimGeocoder(GeocodingProvider):
    name = "nominatim"

    def __init__(self) -> None:
        self._gate = _RateGate(MIN_INTERVAL_SECONDS)

    @property
    def _client(self) -> HttpClient:
        return HttpClient(
            self.name, NOMINATIM_URL, user_agent=current_app.config["NOMINATIM_USER_AGENT"]
        )

    def search(self, query: str, limit: int = 5) -> list[Location]:
        self._gate.wait()
        payload = self._client.get_json(
            "/search",
            params={
                "q": query,
                "format": "jsonv2",
                "limit": limit,
                "addressdetails": 1,
                "accept-language": "pt-BR",
            },
        )
        results = payload if isinstance(payload, list) else payload.get("results", [])
        return [self._to_location(item) for item in results]

    def reverse(self, latitude: float, longitude: float) -> Location | None:
        self._gate.wait()
        payload = self._client.get_json(
            "/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "addressdetails": 1,
                "accept-language": "pt-BR",
            },
        )
        if not payload or "error" in payload:
            return None
        return self._to_location(payload)

    @staticmethod
    def _to_location(item: dict[str, Any]) -> Location:
        address = item.get("address") or {}
        name = next(
            (address[key] for key in PLACE_KEYS if address.get(key)),
            item.get("name") or item.get("display_name", "").split(",")[0],
        )
        country_code = address.get("country_code")

        return Location(
            name=name,
            latitude=float(item["lat"]),
            longitude=float(item["lon"]),
            state=address.get("state"),
            country=address.get("country"),
            country_code=country_code.upper() if country_code else None,
        )
