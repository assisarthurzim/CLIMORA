"""Authentication endpoints."""

from __future__ import annotations

from flask import Blueprint, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_current_user,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from app.auth.schemas import LoginSchema, RegisterSchema, serialize_user
from app.auth.service import AuthService
from app.extensions import limiter
from app.utils.responses import success_response
from app.utils.validation import parse_body

auth_bp = Blueprint("auth", __name__)

REGISTER_RATE_LIMIT = "5 per hour"
LOGIN_RATE_LIMIT = "5 per minute"


def _authenticated_response(user, remember_me: bool = False, status_code: int = 200):
    """Issue both tokens as httpOnly cookies alongside the user payload."""
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(
        identity=user.id, expires_delta=AuthService.refresh_token_lifetime(remember_me)
    )

    response, code = success_response(serialize_user(user), status_code=status_code)
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, code


@auth_bp.post("/register")
@limiter.limit(REGISTER_RATE_LIMIT)
def register():
    payload = parse_body(RegisterSchema)
    user = AuthService().register(payload)
    return _authenticated_response(user, status_code=201)


@auth_bp.post("/login")
@limiter.limit(LOGIN_RATE_LIMIT)
def login():
    payload = parse_body(LoginSchema)
    user = AuthService().authenticate(payload)
    return _authenticated_response(user, remember_me=payload.remember_me)


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Rotate the access token without asking for credentials again."""
    access_token = create_access_token(identity=current_user.id)
    response, code = success_response(serialize_user(current_user))
    set_access_cookies(response, access_token)
    return response, code


@auth_bp.post("/logout")
@jwt_required(verify_type=False, optional=True)
def logout():
    # current_user is a proxy and is never itself None, so the underlying
    # value has to be read before checking for an anonymous caller.
    user = get_current_user()

    response, code = success_response({"message": "Sessao encerrada."})
    unset_jwt_cookies(response)

    if user is not None:
        current_app.logger.info("Logout for user_id=%s", user.id)
    return response, code


@auth_bp.get("/me")
@jwt_required()
def me():
    """Used by the frontend to restore a session on page load."""
    return success_response(serialize_user(current_user))
