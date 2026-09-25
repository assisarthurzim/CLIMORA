"""Search history endpoints."""

ACCOUNT = {
    "name": "Arthur Assis",
    "email": "arthur@example.com",
    "password": "climora2026",
    "password_confirmation": "climora2026",
}

ENTRY = {
    "query": "Sabara",
    "city_name": "Sabará",
    "latitude": -19.8889,
    "longitude": -43.8058,
    "state": "Minas Gerais",
    "country": "Brasil",
    "country_code": "BR",
}


def authenticate(client):
    client.post("/api/v1/auth/register", json=ACCOUNT)


def record(client, **overrides):
    return client.post("/api/v1/history", json={**ENTRY, **overrides})


def test_history_requires_authentication(client):
    assert client.get("/api/v1/history").status_code == 401


def test_recording_a_search_stores_it(client):
    authenticate(client)

    response = record(client)

    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["city_name"] == "Sabará"
    assert data["source"] == "manual"


def test_reopening_the_same_city_does_not_duplicate_the_entry(client):
    authenticate(client)
    first = record(client).get_json()["data"]["id"]

    second = record(client).get_json()["data"]["id"]

    assert first == second
    assert len(client.get("/api/v1/history").get_json()["data"]) == 1


def test_a_different_city_creates_a_new_entry(client):
    authenticate(client)
    record(client)

    record(client, city_name="Belo Horizonte", latitude=-19.9167, longitude=-43.9345)

    assert len(client.get("/api/v1/history").get_json()["data"]) == 2


def test_history_is_returned_newest_first(client):
    authenticate(client)
    record(client)
    record(client, city_name="Belo Horizonte", latitude=-19.9167, longitude=-43.9345)

    names = [item["city_name"] for item in client.get("/api/v1/history").get_json()["data"]]

    assert names[0] == "Belo Horizonte"


def test_history_reports_pagination_metadata(client):
    authenticate(client)
    record(client)

    payload = client.get("/api/v1/history?page=1&per_page=10").get_json()

    assert payload["meta"]["total"] == 1
    assert payload["meta"]["pages"] == 1


def test_history_can_be_filtered(client):
    authenticate(client)
    record(client)
    record(client, city_name="Belo Horizonte", latitude=-19.9167, longitude=-43.9345)

    data = client.get("/api/v1/history?q=belo").get_json()["data"]

    assert len(data) == 1


def test_per_page_beyond_the_maximum_is_rejected(client):
    authenticate(client)

    assert client.get("/api/v1/history?per_page=500").status_code == 422


def test_an_entry_can_be_removed(client):
    authenticate(client)
    entry_id = record(client).get_json()["data"]["id"]

    assert client.delete(f"/api/v1/history/{entry_id}").status_code == 200
    assert client.get("/api/v1/history").get_json()["data"] == []


def test_the_whole_history_can_be_cleared(client):
    authenticate(client)
    record(client)
    record(client, city_name="Belo Horizonte", latitude=-19.9167, longitude=-43.9345)

    response = client.delete("/api/v1/history")

    assert response.get_json()["data"]["removed"] == 2
    assert client.get("/api/v1/history").get_json()["data"] == []


def test_deduplication_survives_a_timestamp_read_back_from_the_database(client):
    """Regression: SQLite returns naive datetimes, which broke the comparison."""
    authenticate(client)
    record(client)

    response = record(client)

    assert response.status_code == 201
    assert "data" in response.get_json()
