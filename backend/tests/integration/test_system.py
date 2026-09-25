"""Smoke tests for the operational endpoints."""


def test_health_check_reports_application_state(client):
    response = client.get("/api/v1/system/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["data"]["database"] == "up"
    assert payload["data"]["environment"] == "testing"
    assert "missing_tables" not in payload["data"]


def test_health_check_reports_an_incomplete_schema(client, app):
    from app.extensions import db

    db.drop_all()
    response = client.get("/api/v1/system/health")

    assert response.status_code == 503
    payload = response.get_json()["data"]
    assert payload["database"] == "schema_incomplete"
    assert "users" in payload["missing_tables"]


def test_unknown_route_uses_the_standard_error_envelope(client):
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "NOT_FOUND"


def test_an_unsupported_method_uses_the_standard_envelope(client):
    response = client.post("/api/v1/system/health")

    assert response.status_code == 405
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_a_malformed_body_is_rejected_with_a_readable_message(client):
    response = client.post(
        "/api/v1/auth/login", data="isto nao e json", content_type="application/json"
    )

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_error_responses_never_leak_internals(client):
    """Stack traces belong in the log, never in the body."""
    response = client.get("/api/v1/does-not-exist")
    body = response.get_data(as_text=True)

    assert "Traceback" not in body
    assert "File \"" not in body


def test_security_headers_are_present_on_every_response(client):
    response = client.get("/api/v1/system/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-Request-ID" in response.headers
