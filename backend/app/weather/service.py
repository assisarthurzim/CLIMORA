"""Weather business rules.

Providers are wired here and results are cached, so no route or other domain
ever touches an upstream API directly.
"""

from __future__ import annotations

from flask import current_app

from app.utils.cache import build_cache_key, get_cache
from app.utils.exceptions import NotFoundError
from app.utils.geo import build_location_key, normalize_coordinate
from app.weather.providers.base import AirQuality, Location, WeatherSnapshot
from app.weather.providers.chain import GeocodingChain, WeatherProviderChain
from app.weather.providers.nominatim import NominatimGeocoder
from app.weather.providers.open_meteo import (
    OpenMeteoAirQuality,
    OpenMeteoGeocoder,
    OpenMeteoProvider,
)
from app.weather.providers.open_weather import OpenWeatherProvider

CACHE_NAMESPACE_SEARCH = "geocode:search"
CACHE_NAMESPACE_REVERSE = "geocode:reverse"
CACHE_NAMESPACE_SNAPSHOT = "weather:snapshot"
CACHE_NAMESPACE_AIR = "weather:air"

UNKNOWN_LOCATION_NAME = "Local selecionado"


class WeatherService:
    def __init__(
        self,
        weather_provider: WeatherProviderChain | None = None,
        geocoder: GeocodingChain | None = None,
        air_quality_provider: OpenMeteoAirQuality | None = None,
    ) -> None:
        self.weather_provider = weather_provider or WeatherProviderChain(
            [OpenMeteoProvider(), OpenWeatherProvider()]
        )
        self.geocoder = geocoder or GeocodingChain([OpenMeteoGeocoder(), NominatimGeocoder()])
        self.air_quality_provider = air_quality_provider or OpenMeteoAirQuality()
        self.cache = get_cache()

    def search_cities(self, query: str, limit: int = 5) -> list[Location]:
        cache_key = build_cache_key(CACHE_NAMESPACE_SEARCH, query.lower(), limit)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        results = self.geocoder.search(query, limit)
        self.cache.set(cache_key, results, current_app.config["CACHE_TTL_GEOCODING"])
        return results

    def reverse_lookup(self, latitude: float, longitude: float) -> Location:
        """Resolve a coordinate to a place, never failing the caller."""
        cache_key = build_cache_key(
            CACHE_NAMESPACE_REVERSE, build_location_key(latitude, longitude)
        )
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        location = self.geocoder.reverse(latitude, longitude) or Location(
            name=UNKNOWN_LOCATION_NAME,
            latitude=normalize_coordinate(latitude),
            longitude=normalize_coordinate(longitude),
        )
        self.cache.set(cache_key, location, current_app.config["CACHE_TTL_GEOCODING"])
        return location

    def get_snapshot(self, latitude: float, longitude: float) -> WeatherSnapshot:
        """Full picture for one place: conditions, forecast and air quality."""
        location_key = build_location_key(latitude, longitude)
        cache_key = build_cache_key(CACHE_NAMESPACE_SNAPSHOT, location_key)

        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        location = self.reverse_lookup(latitude, longitude)
        snapshot = self.weather_provider.get_snapshot(location)

        # Air quality comes from a separate endpoint and is optional: a failure
        # there must not cost the user their forecast.
        snapshot = WeatherSnapshot(
            location=snapshot.location,
            current=snapshot.current,
            hourly=snapshot.hourly,
            daily=snapshot.daily,
            air_quality=self._safe_air_quality(latitude, longitude),
            previous_day=snapshot.previous_day,
            provider=snapshot.provider,
        )

        self.cache.set(cache_key, snapshot, current_app.config["CACHE_TTL_CURRENT_WEATHER"])
        return snapshot

    def get_air_quality(self, latitude: float, longitude: float) -> AirQuality:
        air_quality = self._safe_air_quality(latitude, longitude)
        if air_quality is None:
            raise NotFoundError("Nao ha dados de qualidade do ar para esta localizacao.")
        return air_quality

    def _safe_air_quality(self, latitude: float, longitude: float) -> AirQuality | None:
        cache_key = build_cache_key(CACHE_NAMESPACE_AIR, build_location_key(latitude, longitude))
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            air_quality = self.air_quality_provider.get_air_quality(latitude, longitude)
        except Exception:  # noqa: BLE001 - optional data, logged and skipped
            current_app.logger.warning("Air quality lookup failed", exc_info=True)
            return None

        if air_quality is not None:
            self.cache.set(cache_key, air_quality, current_app.config["CACHE_TTL_AIR_QUALITY"])
        return air_quality
