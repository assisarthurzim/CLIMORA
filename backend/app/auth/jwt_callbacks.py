"""JWT identity resolution."""

from __future__ import annotations

from flask import Flask

from app.extensions import jwt


def register_jwt_callbacks(app: Flask) -> None:
    @jwt.user_identity_loader
    def serialize_identity(user_id) -> str:
        # The JWT "sub" claim must be a string.
        return str(user_id)

    @jwt.user_lookup_loader
    def load_user(_header: dict, payload: dict):
        from app.auth.service import AuthService

        identity = payload.get("sub")
        if identity is None or not str(identity).isdigit():
            return None
        return AuthService().get_active_user(int(identity))
