"""Parsing and fallback behaviour, with every network call mocked."""

from unittest.mock import patch

import pytest

from app.utils.exceptions import ExternalServiceError
from app.weather.providers.base import Location
from app.weather.providers.chain import GeocodingChain, WeatherProviderChain
from app.weather.providers.open_meteo import (
    OpenMeteoAirQuality,
    OpenMeteoGeocoder,
    OpenMeteoProvider,
    classify_air_quality,
)

SABARA = Location(name="Sabará", latitude=-19.8889, longitude=-43.8058, timezone="America/Sao_Paulo")

FORECAST_PAYLOAD = {
    "current": {
        "time": "2026-07-27T18:00",
        "temperature_2m": 24.3,
        "apparent_temperature": 25.1,
        "relative_humidity_2m": 62,
        "surface_pressure": 1014.2,
        "wind_speed_10m": 11.5,
        "wind_direction_10m": 95,
        "precipitation": 0.0,
        "cloud_cover": 40,
        "is_day": 1,
        "weather_code": 2,
    },
    "hourly": {
        "time": ["2026-07-27T18:00", "2026-07-27T19:00"],
        "temperature_2m": [24.3, 22.8],
        "apparent_temperature": [25.1, 23.4],
        "precipitation_probability": [15, 20],
        "precipitation": [0.0, 0.1],
        "relative_humidity_2m": [62, 68],
        "surface_pressure": [1014.2, 1014.8],
        "wind_speed_10m": [11.5, 9.9],
        "uv_index": [3.2, 0.4],
        "visibility": [24140.0, 24140.0],
        "weather_code": [2, 3],
    },
    "daily": {
        "time": ["2026-07-27", "2026-07-28"],
        "temperature_2m_min": [16.2, 15.8],
        "temperature_2m_max": [27.4, 26.1],
        "precipitation_sum": [0.0, 2.4],
        "precipitation_probability_max": [20, 65],
        "wind_speed_10m_max": [18.0, 21.3],
        "uv_index_max": [7.8, 6.5],
        "sunrise": ["2026-07-27T06:42", "2026-07-28T06:41"],
        "sunset": ["2026-07-27T17:55", "2026-07-28T17:56"],
        "weather_code": [2, 61],
    },
}


def test_snapshot_is_normalized_from_the_raw_payload(app):
    with patch("app.utils.http.HttpClient.get_json", return_value=FORECAST_PAYLOAD):
        snapshot = OpenMeteoProvider().get_snapshot(SABARA)

    assert snapshot.provider == "open-meteo"
    assert snapshot.current.temperature == 24.3
    assert snapshot.current.condition == "Parcialmente nublado"
    assert snapshot.current.wind_direction_label == "E"
    assert snapshot.current.is_day is True
    assert len(snapshot.hourly) == 2
    assert len(snapshot.daily) == 2


def test_current_borrows_fields_the_upstream_block_omits(app):
    """UV, rain chance and the day's range are not in the current block."""
    with patch("app.utils.http.HttpClient.get_json", return_value=FORECAST_PAYLOAD):
        current = OpenMeteoProvider().get_snapshot(SABARA).current

    assert current.uv_index == 3.2
    assert current.precipitation_probability == 15
    assert current.visibility == 24140.0
    assert current.temperature_min == 16.2
    assert current.temperature_max == 27.4
    assert current.sunrise is not None


def test_parsing_survives_missing_series(app):
    """A partial payload must degrade to nulls, not raise."""
    with patch("app.utils.http.HttpClient.get_json", return_value={"current": {"weather_code": 0}}):
        snapshot = OpenMeteoProvider().get_snapshot(SABARA)

    assert snapshot.current.temperature is None
    assert snapshot.current.condition == "Céu limpo"
    assert snapshot.hourly == []


def test_snapshot_serializes_dates_as_iso_strings(app):
    with patch("app.utils.http.HttpClient.get_json", return_value=FORECAST_PAYLOAD):
        payload = OpenMeteoProvider().get_snapshot(SABARA).to_dict()

    assert isinstance(payload["current"]["observed_at"], str)
    assert payload["daily"][0]["date"] == "2026-07-27"
    assert payload["location"]["display_name"].startswith("Sabará")


def test_geocoder_maps_results_to_locations(app):
    payload = {
        "results": [
            {
                "name": "Sabará",
                "latitude": -19.8889,
                "longitude": -43.8058,
                "admin1": "Minas Gerais",
                "country": "Brasil",
                "country_code": "BR",
                "timezone": "America/Sao_Paulo",
            }
        ]
    }
    with patch("app.utils.http.HttpClient.get_json", return_value=payload):
        results = OpenMeteoGeocoder().search("Sabará")

    assert len(results) == 1
    assert results[0].state == "Minas Gerais"
    assert results[0].location_key == "-19.8889,-43.8058"


@pytest.mark.parametrize(
    ("index", "expected"),
    [(None, "Indisponível"), (12, "Boa"), (35, "Razoável"), (55, "Moderada"), (140, "Extremamente ruim")],
)
def test_air_quality_categories(index, expected):
    assert classify_air_quality(index) == expected


def test_air_quality_returns_none_without_a_current_block(app):
    with patch("app.utils.http.HttpClient.get_json", return_value={}):
        assert OpenMeteoAirQuality().get_air_quality(-19.8, -43.8) is None


class _FailingProvider:
    name = "failing"

    def get_snapshot(self, location):
        raise ExternalServiceError("indisponivel")


class _WorkingProvider:
    name = "working"

    def get_snapshot(self, location):
        return "snapshot"


def test_chain_falls_back_to_the_next_provider(app):
    chain = WeatherProviderChain([_FailingProvider(), _WorkingProvider()])

    assert chain.get_snapshot(SABARA) == "snapshot"


def test_chain_raises_when_every_provider_fails(app):
    chain = WeatherProviderChain([_FailingProvider(), _FailingProvider()])

    with pytest.raises(ExternalServiceError):
        chain.get_snapshot(SABARA)


def test_chain_rejects_an_empty_provider_list():
    with pytest.raises(ValueError):
        WeatherProviderChain([])


class _EmptyGeocoder:
    name = "empty"

    def search(self, query, limit=5):
        return []

    def reverse(self, latitude, longitude):
        return None


class _FoundGeocoder:
    name = "found"

    def search(self, query, limit=5):
        return [SABARA]

    def reverse(self, latitude, longitude):
        return SABARA


def test_geocoding_chain_moves_on_when_a_provider_finds_nothing(app):
    chain = GeocodingChain([_EmptyGeocoder(), _FoundGeocoder()])

    assert chain.search("Sabará") == [SABARA]
    assert chain.reverse(-19.8, -43.8) == SABARA


def test_geocoding_chain_returns_empty_when_nobody_knows_the_place(app):
    chain = GeocodingChain([_EmptyGeocoder(), _EmptyGeocoder()])

    assert chain.search("Lugar inexistente") == []


def test_city_search_filters_out_countries_and_regions(app):
    from app.weather.providers.open_meteo import prefer_cities

    results = [
        {"name": "Bósnia e Herzegovina", "feature_code": "PCLI"},
        {"name": "Sarajevo", "feature_code": "PPLC"},
        {"name": "Rio Bósnia", "feature_code": "STM"},
        {"name": "Banja Luka", "feature_code": "PPLA"},
    ]

    assert [item["name"] for item in prefer_cities(results)] == ["Sarajevo", "Banja Luka"]


def test_city_search_keeps_everything_when_no_city_matches(app):
    from app.weather.providers.open_meteo import prefer_cities

    results = [{"name": "Minas Gerais", "feature_code": "ADM1"}]

    assert prefer_cities(results) == results


def test_geocoder_applies_the_city_filter_end_to_end(app):
    payload = {
        "results": [
            {"name": "Bósnia e Herzegovina", "latitude": 44.0, "longitude": 18.0, "feature_code": "PCLI"},
            {"name": "Sarajevo", "latitude": 43.85, "longitude": 18.38, "feature_code": "PPLC"},
        ]
    }
    with patch("app.utils.http.HttpClient.get_json", return_value=payload):
        results = OpenMeteoGeocoder().search("Bosnia")

    assert [location.name for location in results] == ["Sarajevo"]


def test_hourly_series_starts_at_the_current_hour(app):
    """Open-Meteo returns the day from midnight; the forecast must start now."""
    payload = {
        "current": {"time": "2026-07-27T19:00", "weather_code": 0},
        "hourly": {
            "time": [
                "2026-07-27T17:00",
                "2026-07-27T18:00",
                "2026-07-27T19:00",
                "2026-07-27T20:00",
            ],
            "temperature_2m": [24.0, 22.0, 20.0, 19.0],
            "uv_index": [4.0, 1.0, 0.0, 0.0],
            "visibility": [10000.0, 12000.0, 24000.0, 25000.0],
            "weather_code": [0, 0, 0, 0],
        },
    }
    with patch("app.utils.http.HttpClient.get_json", return_value=payload):
        snapshot = OpenMeteoProvider().get_snapshot(SABARA)

    assert snapshot.hourly[0].time.hour == 19
    assert len(snapshot.hourly) == 2
    # The derived current values must come from the current hour, not midnight.
    assert snapshot.current.visibility == 24000.0
    assert snapshot.current.uv_index == 0.0


def test_hourly_series_falls_back_to_the_start_when_the_hour_is_absent(app):
    from app.weather.providers.open_meteo import find_current_hour_index

    assert find_current_hour_index([], None) == 0


def test_yesterday_is_separated_from_the_forecast(app):
    """past_days puts yesterday first; nothing downstream may read it as today."""
    from datetime import date, datetime

    from app.weather.providers.open_meteo import split_past_days

    class Day:
        def __init__(self, offset):
            self.date = date(2026, 7, 28 + offset)

    days = [Day(-1), Day(0), Day(1)]
    previous, upcoming = split_past_days(days, datetime(2026, 7, 28, 10, 0))

    assert previous.date.day == 27
    assert [day.date.day for day in upcoming] == [28, 29]


def test_split_falls_back_when_every_day_is_in_the_past(app):
    from app.weather.providers.open_meteo import split_past_days

    assert split_past_days([], None) == (None, [])
