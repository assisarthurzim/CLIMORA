"""Weather endpoints, with the provider layer mocked."""

from unittest.mock import patch

from app.weather.providers.base import AirQuality, CurrentWeather, Location, WeatherSnapshot
from datetime import datetime

ACCOUNT = {
    "name": "Arthur Assis",
    "email": "arthur@example.com",
    "password": "climora2026",
    "password_confirmation": "climora2026",
}

SABARA = Location(
    name="Sabará",
    latitude=-19.8889,
    longitude=-43.8058,
    state="Minas Gerais",
    country="Brasil",
    country_code="BR",
)

SNAPSHOT = WeatherSnapshot(
    location=SABARA,
    current=CurrentWeather(
        observed_at=datetime(2026, 7, 27, 18, 0),
        temperature=24.3,
        feels_like=25.1,
        temperature_min=16.2,
        temperature_max=27.4,
        humidity=62,
        pressure=1014.2,
        wind_speed=11.5,
        wind_direction=95,
        wind_direction_label="E",
        uv_index=3.2,
        visibility=24140.0,
        precipitation_probability=15,
        precipitation=0.0,
        cloud_cover=40,
        is_day=True,
        weather_code=2,
        condition="Parcialmente nublado",
        icon="cloud-sun",
    ),
    air_quality=AirQuality(index=18, category="Boa", pm2_5=6.1),
    provider="open-meteo",
)


def authenticate(client):
    client.post("/api/v1/auth/register", json=ACCOUNT)


def test_search_requires_authentication(client):
    response = client.get("/api/v1/weather/search?q=Sabara")

    assert response.status_code == 401


def test_search_returns_matching_places(client):
    authenticate(client)

    with patch("app.weather.service.WeatherService.search_cities", return_value=[SABARA]):
        response = client.get("/api/v1/weather/search?q=Sabara")

    assert response.status_code == 200
    results = response.get_json()["data"]
    assert results[0]["name"] == "Sabará"
    assert results[0]["display_name"] == "Sabará, Minas Gerais, Brasil"
    assert results[0]["location_key"] == "-19.8889,-43.8058"


def test_search_rejects_a_query_that_is_too_short(client):
    authenticate(client)

    response = client.get("/api/v1/weather/search?q=a")

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_search_rejects_a_limit_beyond_the_maximum(client):
    authenticate(client)

    response = client.get("/api/v1/weather/search?q=Sabara&limit=99")

    assert response.status_code == 422


def test_snapshot_returns_the_full_payload(client):
    authenticate(client)

    with patch("app.weather.service.WeatherService.get_snapshot", return_value=SNAPSHOT):
        response = client.get("/api/v1/weather/snapshot?lat=-19.8889&lon=-43.8058")

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["current"]["temperature"] == 24.3
    assert data["current"]["condition"] == "Parcialmente nublado"
    assert data["current"]["visibility"] == 24140.0
    assert data["air_quality"]["category"] == "Boa"
    assert data["provider"] == "open-meteo"


def test_snapshot_rejects_coordinates_out_of_range(client):
    authenticate(client)

    response = client.get("/api/v1/weather/snapshot?lat=120&lon=-43.8")

    assert response.status_code == 422
    assert "lat" in response.get_json()["error"]["details"]


def test_snapshot_rejects_missing_coordinates(client):
    authenticate(client)

    response = client.get("/api/v1/weather/snapshot")

    assert response.status_code == 422


def test_upstream_failure_becomes_a_gateway_error(client):
    from app.utils.exceptions import ExternalServiceError

    authenticate(client)

    with patch(
        "app.weather.service.WeatherService.get_snapshot",
        side_effect=ExternalServiceError(),
    ):
        response = client.get("/api/v1/weather/snapshot?lat=-19.8889&lon=-43.8058")

    assert response.status_code == 502
    assert response.get_json()["error"]["code"] == "EXTERNAL_SERVICE_ERROR"
