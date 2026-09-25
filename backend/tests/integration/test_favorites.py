"""Favourite city endpoints."""

ACCOUNT = {
    "name": "Arthur Assis",
    "email": "arthur@example.com",
    "password": "climora2026",
    "password_confirmation": "climora2026",
}
OTHER_ACCOUNT = {**ACCOUNT, "name": "Outra Pessoa", "email": "outra@example.com"}

SABARA = {
    "name": "Sabará",
    "latitude": -19.8889,
    "longitude": -43.8058,
    "state": "Minas Gerais",
    "country": "Brasil",
    "country_code": "BR",
}


def authenticate(client, account=ACCOUNT):
    client.post("/api/v1/auth/register", json=account)


def add_favorite(client, **overrides):
    return client.post("/api/v1/favorites", json={**SABARA, **overrides})


def test_favorites_require_authentication(client):
    assert client.get("/api/v1/favorites").status_code == 401


def test_adding_a_favorite_returns_it(client):
    authenticate(client)

    response = add_favorite(client)

    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["name"] == "Sabará"
    assert data["location_key"] == "-19.8889,-43.8058"
    assert data["position"] == 0


def test_the_same_place_cannot_be_added_twice(client):
    authenticate(client)
    add_favorite(client)

    response = add_favorite(client, name="Sabara")

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "CONFLICT"


def test_nearly_identical_coordinates_count_as_the_same_place(client):
    authenticate(client)
    add_favorite(client)

    response = add_favorite(client, latitude=-19.88891, longitude=-43.80581)

    assert response.status_code == 409


def test_favorites_are_listed_in_position_order(client):
    authenticate(client)
    add_favorite(client)
    add_favorite(client, name="Belo Horizonte", latitude=-19.9167, longitude=-43.9345)

    response = client.get("/api/v1/favorites")

    names = [item["name"] for item in response.get_json()["data"]]
    assert names == ["Sabará", "Belo Horizonte"]


def test_favorites_can_be_filtered_by_name(client):
    authenticate(client)
    add_favorite(client)
    add_favorite(client, name="Belo Horizonte", latitude=-19.9167, longitude=-43.9345)

    response = client.get("/api/v1/favorites?q=belo")

    data = response.get_json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Belo Horizonte"


def test_a_custom_label_replaces_the_display_name(client):
    authenticate(client)
    favorite_id = add_favorite(client).get_json()["data"]["id"]

    response = client.patch(f"/api/v1/favorites/{favorite_id}", json={"label": "Casa"})

    assert response.status_code == 200
    assert response.get_json()["data"]["display_name"] == "Casa"


def test_updating_with_an_empty_payload_is_rejected(client):
    authenticate(client)
    favorite_id = add_favorite(client).get_json()["data"]["id"]

    response = client.patch(f"/api/v1/favorites/{favorite_id}", json={})

    assert response.status_code == 422


def test_a_favorite_can_be_removed(client):
    authenticate(client)
    favorite_id = add_favorite(client).get_json()["data"]["id"]

    assert client.delete(f"/api/v1/favorites/{favorite_id}").status_code == 200
    assert client.get("/api/v1/favorites").get_json()["data"] == []


def test_another_users_favorite_is_invisible(client):
    """Scoping by user turns someone else's id into a 404, not a 403."""
    authenticate(client)
    favorite_id = add_favorite(client).get_json()["data"]["id"]
    client.post("/api/v1/auth/logout")

    authenticate(client, OTHER_ACCOUNT)
    response = client.delete(f"/api/v1/favorites/{favorite_id}")

    assert response.status_code == 404


def test_invalid_coordinates_are_rejected(client):
    authenticate(client)

    response = add_favorite(client, latitude=200)

    assert response.status_code == 422
