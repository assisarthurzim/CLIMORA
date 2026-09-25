"""Caching and degradation rules in the weather service."""

from unittest.mock import patch

from app.utils.cache import get_cache
from app.weather.providers.base import Location
from app.weather.service import WeatherService

SABARA = Location(name="Sabará", latitude=-19.8889, longitude=-43.8058)


def test_repeated_searches_hit_the_cache_once(app):
    get_cache().clear()
    service = WeatherService()

    with patch.object(service.geocoder, "search", return_value=[SABARA]) as geocoder:
        service.search_cities("Sabara")
        service.search_cities("Sabara")

    assert geocoder.call_count == 1


def test_reverse_lookup_falls_back_to_a_placeholder_location(app):
    get_cache().clear()
    service = WeatherService()

    with patch.object(service.geocoder, "reverse", return_value=None):
        location = service.reverse_lookup(-19.8889, -43.8058)

    assert location.name == "Local selecionado"
    assert location.location_key == "-19.8889,-43.8058"


def test_air_quality_failure_does_not_break_the_forecast(app):
    get_cache().clear()
    service = WeatherService()

    with patch.object(
        service.air_quality_provider, "get_air_quality", side_effect=RuntimeError("boom")
    ):
        assert service._safe_air_quality(-19.8889, -43.8058) is None
