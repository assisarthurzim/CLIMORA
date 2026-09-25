"""Profile and account endpoints."""

from __future__ import annotations

from flask import Blueprint
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from app.auth.schemas import serialize_user
from app.auth.service import AuthService
from app.extensions import limiter
from app.profile.schemas import (
    ChangePasswordSchema,
    DeleteAccountSchema,
    UpdateProfileSchema,
    UpdateSettingsSchema,
    serialize_settings,
)
from app.profile.service import ProfileService
from app.utils.responses import success_response
from app.utils.validation import parse_body

profile_bp = Blueprint("profile", __name__)

SENSITIVE_RATE_LIMIT = "10 per hour"


@profile_bp.get("")
@jwt_required()
def get_profile():
    return success_response(serialize_user(current_user))


@profile_bp.patch("")
@jwt_required()
def update_profile():
    payload = parse_body(UpdateProfileSchema)
    user = ProfileService().update_profile(current_user, payload)
    return success_response(serialize_user(user))


@profile_bp.put("/password")
@jwt_required()
@limiter.limit(SENSITIVE_RATE_LIMIT)
def change_password():
    payload = parse_body(ChangePasswordSchema)
    user = ProfileService().change_password(current_user, payload)

    # Fresh tokens after a password change, so the new secret takes effect on
    # this session too instead of forcing an immediate re-login.
    response, code = success_response({"message": "Senha alterada com sucesso."})
    set_access_cookies(response, create_access_token(identity=user.id))
    set_refresh_cookies(
        response,
        create_refresh_token(identity=user.id, expires_delta=AuthService.refresh_token_lifetime(False)),
    )
    return response, code


@profile_bp.delete("")
@jwt_required()
@limiter.limit(SENSITIVE_RATE_LIMIT)
def delete_account():
    payload = parse_body(DeleteAccountSchema)
    ProfileService().delete_account(current_user, payload)

    response, code = success_response({"message": "Conta excluída."})
    unset_jwt_cookies(response)
    return response, code


@profile_bp.get("/settings")
@jwt_required()
def get_settings():
    return success_response(serialize_settings(ProfileService().get_settings(current_user)))


@profile_bp.put("/settings")
@jwt_required()
def update_settings():
    payload = parse_body(UpdateSettingsSchema)
    settings = ProfileService().update_settings(current_user, payload)
    return success_response(serialize_settings(settings))
