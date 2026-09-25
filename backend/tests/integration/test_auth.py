"""End-to-end behaviour of the authentication endpoints."""

VALID_ACCOUNT = {
    "name": "Arthur Assis",
    "email": "arthur@example.com",
    "password": "climora2026",
    "password_confirmation": "climora2026",
}


def register(client, **overrides):
    return client.post("/api/v1/auth/register", json={**VALID_ACCOUNT, **overrides})


def test_registration_returns_the_user_and_sets_cookies(client):
    response = register(client)

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["data"]["email"] == "arthur@example.com"
    assert "password" not in payload["data"]

    cookies = response.headers.getlist("Set-Cookie")
    assert any("access_token_cookie" in cookie for cookie in cookies)
    assert any("HttpOnly" in cookie for cookie in cookies)


def test_registration_rejects_mismatched_passwords(client):
    response = register(client, password_confirmation="outra-senha1")

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_registration_rejects_a_password_without_digits(client):
    response = register(client, password="somenteletras", password_confirmation="somenteletras")

    assert response.status_code == 422


def test_registration_rejects_a_duplicate_email(client):
    register(client)
    response = register(client, name="Outro")

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "CONFLICT"


def test_login_succeeds_with_valid_credentials(client):
    register(client)
    client.delete_cookie("access_token_cookie")

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "arthur@example.com", "password": "climora2026"},
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["last_login_at"] is not None


def test_login_does_not_reveal_whether_an_email_exists(client):
    register(client)

    unknown = client.post(
        "/api/v1/auth/login",
        json={"email": "ninguem@example.com", "password": "climora2026"},
    )
    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"email": "arthur@example.com", "password": "senhaerrada1"},
    )

    assert unknown.status_code == wrong_password.status_code == 401
    assert unknown.get_json()["error"]["message"] == wrong_password.get_json()["error"]["message"]


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTHENTICATION_ERROR"


def test_me_returns_the_session_owner(client):
    register(client)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.get_json()["data"]["name"] == "Arthur Assis"


def test_logout_clears_the_session(client):
    register(client)

    client.post("/api/v1/auth/logout")
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_refresh_issues_a_new_access_token(client):
    register(client)

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    assert response.get_json()["data"]["email"] == "arthur@example.com"
