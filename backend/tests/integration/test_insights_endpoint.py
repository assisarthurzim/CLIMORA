"""Insights do Dia endpoint."""

from unittest.mock import patch

ACCOUNT = {
    "name": "Arthur Assis",
    "email": "arthur@example.com",
    "password": "climora2026",
    "password_confirmation": "climora2026",
}


def authenticate(client):
    client.post("/api/v1/auth/register", json=ACCOUNT)


def test_insights_require_authentication(client):
    assert client.get("/api/v1/insights?lat=-19.9&lon=-43.9").status_code == 401


def test_insights_are_returned_for_a_location(client):
    from tests.unit.test_insights import build_day, build_snapshot

    authenticate(client)
    snapshot = build_snapshot(daily=[build_day(precipitation_probability_max=80)])

    with patch("app.weather.service.WeatherService.get_snapshot", return_value=snapshot):
        response = client.get("/api/v1/insights?lat=-19.8889&lon=-43.8058")

    assert response.status_code == 200
    titles = [item["title"] for item in response.get_json()["data"]]
    assert "Leve guarda-chuva" in titles


def test_insights_reject_invalid_coordinates(client):
    authenticate(client)

    assert client.get("/api/v1/insights?lat=999&lon=0").status_code == 422
