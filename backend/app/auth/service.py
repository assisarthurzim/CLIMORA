"""Authentication business rules."""

from __future__ import annotations

from datetime import timedelta

from flask import current_app

from app.auth.repository import UserRepository
from app.auth.schemas import LoginSchema, RegisterSchema
from app.extensions import db
from app.models.base import utcnow
from app.models.user import User
from app.models.user_settings import UserSettings
from app.utils.exceptions import AuthenticationError, ConflictError
from app.utils.security import hash_password, verify_password

# One message for both "unknown email" and "wrong password" keeps the endpoint
# from confirming which addresses have accounts.
INVALID_CREDENTIALS_MESSAGE = "E-mail ou senha incorretos."
INACTIVE_ACCOUNT_MESSAGE = "Esta conta foi desativada."


class AuthService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def register(self, payload: RegisterSchema) -> User:
        email = User.normalize_email(payload.email)

        if self.repository.email_exists(email):
            raise ConflictError("Este e-mail ja esta cadastrado.")

        user = User(
            name=payload.name,
            email=email,
            password_hash=hash_password(payload.password),
        )
        # Preferences are created with the account so no screen has to handle
        # their absence.
        user.settings = UserSettings()

        self.repository.add(user)
        current_app.logger.info("Account created for user_id=%s", user.id)
        return user

    def authenticate(self, payload: LoginSchema) -> User:
        user = self.repository.get_by_email(payload.email)

        if user is None or not verify_password(payload.password, user.password_hash):
            current_app.logger.warning("Failed login attempt for %s", payload.email)
            raise AuthenticationError(INVALID_CREDENTIALS_MESSAGE)

        if not user.is_active:
            raise AuthenticationError(INACTIVE_ACCOUNT_MESSAGE)

        user.last_login_at = utcnow()
        db.session.commit()

        current_app.logger.info("Login succeeded for user_id=%s", user.id)
        return user

    def get_active_user(self, user_id: int) -> User | None:
        user = self.repository.get_by_id(user_id)
        return user if user is not None and user.is_active else None

    @staticmethod
    def refresh_token_lifetime(remember_me: bool) -> timedelta:
        key = "JWT_REFRESH_TOKEN_EXPIRES_REMEMBER" if remember_me else "JWT_REFRESH_TOKEN_EXPIRES"
        return current_app.config[key]
