"""Fallback orchestration across providers."""

from __future__ import annotations

from flask import current_app

from app.utils.exceptions import ExternalServiceError
from app.weather.providers.base import (
    GeocodingProvider,
    Location,
    WeatherProvider,
    WeatherSnapshot,
)


class WeatherProviderChain(WeatherProvider):
    """Tries each provider in order and degrades on failure."""

    name = "chain"

    def __init__(self, providers: list[WeatherProvider]) -> None:
        if not providers:
            raise ValueError("A provider chain needs at least one provider.")
        self._providers = providers

    def get_snapshot(self, location: Location) -> WeatherSnapshot:
        last_error: ExternalServiceError | None = None

        for provider in self._providers:
            if not getattr(provider, "is_available", True):
                continue
            try:
                return provider.get_snapshot(location)
            except ExternalServiceError as error:
                last_error = error
                current_app.logger.warning(
                    "Provider %s failed, trying the next one: %s", provider.name, error.message
                )

        raise last_error or ExternalServiceError()


class GeocodingChain(GeocodingProvider):
    name = "geocoding-chain"

    def __init__(self, providers: list[GeocodingProvider]) -> None:
        if not providers:
            raise ValueError("A geocoding chain needs at least one provider.")
        self._providers = providers

    def search(self, query: str, limit: int = 5) -> list[Location]:
        last_error: ExternalServiceError | None = None

        for provider in self._providers:
            try:
                results = provider.search(query, limit)
            except ExternalServiceError as error:
                last_error = error
                current_app.logger.warning("Geocoder %s failed: %s", provider.name, error.message)
                continue
            # An empty result is a valid answer from a healthy provider, but the
            # next one may still know the place.
            if results:
                return results

        if last_error:
            raise last_error
        return []

    def reverse(self, latitude: float, longitude: float) -> Location | None:
        for provider in self._providers:
            try:
                location = provider.reverse(latitude, longitude)
            except ExternalServiceError as error:
                current_app.logger.warning("Geocoder %s failed: %s", provider.name, error.message)
                continue
            if location:
                return location
        return None
