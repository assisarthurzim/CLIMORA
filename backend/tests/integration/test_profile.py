"""Profile, password and account deletion endpoints."""

ACCOUNT = {
    "name": "Arthur Assis",
    "email": "arthur@example.com",
    "password": "climora2026",
    "password_confirmation": "climora2026",
}

NEW_PASSWORD = {
    "current_password": "climora2026",
    "new_password": "novaSenha2027",
    "new_password_confirmation": "novaSenha2027",
}


def authenticate(client):
    client.post("/api/v1/auth/register", json=ACCOUNT)


def test_profile_requires_authentication(client):
    assert client.get("/api/v1/profile").status_code == 401


def test_profile_returns_the_session_owner(client):
    authenticate(client)

    data = client.get("/api/v1/profile").get_json()["data"]

    assert data["email"] == "arthur@example.com"
    assert "password_hash" not in data


def test_the_name_can_be_updated(client):
    authenticate(client)

    response = client.patch("/api/v1/profile", json={"name": "  Arthur   Assis Silva "})

    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == "Arthur Assis Silva"


def test_an_empty_update_is_rejected(client):
    authenticate(client)

    assert client.patch("/api/v1/profile", json={}).status_code == 422


def test_a_one_letter_name_is_rejected(client):
    authenticate(client)

    assert client.patch("/api/v1/profile", json={"name": "A"}).status_code == 422


def test_the_password_can_be_changed(client):
    authenticate(client)

    response = client.put("/api/v1/profile/password", json=NEW_PASSWORD)

    assert response.status_code == 200
    client.post("/api/v1/auth/logout")
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "arthur@example.com", "password": "novaSenha2027"},
    )
    assert login.status_code == 200


def test_changing_the_password_requires_the_current_one(client):
    authenticate(client)

    response = client.put(
        "/api/v1/profile/password", json={**NEW_PASSWORD, "current_password": "errada123"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"]["message"] == "Senha atual incorreta."


def test_the_new_password_must_differ_from_the_current_one(client):
    authenticate(client)

    response = client.put(
        "/api/v1/profile/password",
        json={
            "current_password": "climora2026",
            "new_password": "climora2026",
            "new_password_confirmation": "climora2026",
        },
    )

    assert response.status_code == 422


def test_the_session_survives_a_password_change(client):
    """New cookies are issued, so the user is not logged out mid-flow."""
    authenticate(client)

    client.put("/api/v1/profile/password", json=NEW_PASSWORD)

    assert client.get("/api/v1/profile").status_code == 200


def test_settings_are_created_with_the_account(client):
    authenticate(client)

    data = client.get("/api/v1/profile/settings").get_json()["data"]

    assert data["temperature_unit"] == "celsius"
    assert data["language"] == "pt-BR"


def test_settings_can_be_updated(client):
    authenticate(client)

    response = client.put(
        "/api/v1/profile/settings", json={"temperature_unit": "fahrenheit", "theme": "dark"}
    )

    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["temperature_unit"] == "fahrenheit"
    assert data["theme"] == "dark"
    # Untouched preferences must survive a partial update.
    assert data["wind_speed_unit"] == "kmh"


def test_an_unknown_unit_is_rejected(client):
    authenticate(client)

    response = client.put("/api/v1/profile/settings", json={"temperature_unit": "kelvin"})

    assert response.status_code == 422


def test_deleting_the_account_requires_the_password(client):
    authenticate(client)

    response = client.delete("/api/v1/profile", json={"password": "errada123"})

    assert response.status_code == 401


def test_deleting_the_account_removes_every_dependent_record(client):
    """The cascade declared in the models is what makes this safe."""
    from app.extensions import db
    from app.models import Conversation, FavoriteCity, SearchHistory, User, UserSettings

    authenticate(client)
    client.post(
        "/api/v1/favorites",
        json={"name": "Sabará", "latitude": -19.8889, "longitude": -43.8058},
    )
    client.post(
        "/api/v1/history",
        json={
            "query": "Sabara",
            "city_name": "Sabará",
            "latitude": -19.8889,
            "longitude": -43.8058,
        },
    )

    response = client.delete("/api/v1/profile", json={"password": "climora2026"})

    assert response.status_code == 200
    assert db.session.query(User).count() == 0
    assert db.session.query(FavoriteCity).count() == 0
    assert db.session.query(SearchHistory).count() == 0
    assert db.session.query(Conversation).count() == 0
    assert db.session.query(UserSettings).count() == 0


def test_the_session_ends_after_deletion(client):
    authenticate(client)

    client.delete("/api/v1/profile", json={"password": "climora2026"})

    assert client.get("/api/v1/profile").status_code == 401
