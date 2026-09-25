"""Account management rules."""

from __future__ import annotations

from flask import current_app

from app.auth.repository import UserRepository
from app.extensions import db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.profile.schemas import (
    ChangePasswordSchema,
    DeleteAccountSchema,
    UpdateProfileSchema,
    UpdateSettingsSchema,
)
from app.utils.exceptions import AuthenticationError, ValidationError
from app.utils.security import hash_password, verify_password

WRONG_PASSWORD_MESSAGE = "Senha atual incorreta."


class ProfileService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def update_profile(self, user: User, payload: UpdateProfileSchema) -> User:
        changes = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not changes:
            raise ValidationError("Informe ao menos um campo para atualizar.")

        self.repository.update(user, **changes)
        current_app.logger.info("Profile updated for user_id=%s", user.id)
        return user

    def change_password(self, user: User, payload: ChangePasswordSchema) -> User:
        # Knowing the current password is what separates changing your own
        # password from an attacker using a stolen session.
        if not verify_password(payload.current_password, user.password_hash):
            current_app.logger.warning("Failed password change for user_id=%s", user.id)
            raise AuthenticationError(WRONG_PASSWORD_MESSAGE)

        self.repository.update(user, password_hash=hash_password(payload.new_password))
        current_app.logger.info("Password changed for user_id=%s", user.id)
        return user

    def delete_account(self, user: User, payload: DeleteAccountSchema) -> None:
        if not verify_password(payload.password, user.password_hash):
            raise AuthenticationError(WRONG_PASSWORD_MESSAGE)

        user_id = user.id
        # A hard delete: favourites, history, conversations and settings go
        # with it through the cascades declared on the model.
        self.repository.delete(user)
        current_app.logger.info("Account deleted for user_id=%s", user_id)

    def get_settings(self, user: User) -> UserSettings:
        if user.settings is None:
            user.settings = UserSettings()
            db.session.commit()
        return user.settings

    def update_settings(self, user: User, payload: UpdateSettingsSchema) -> UserSettings:
        changes = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not changes:
            raise ValidationError("Informe ao menos uma preferência para atualizar.")

        settings = self.get_settings(user)
        for field, value in changes.items():
            setattr(settings, field, value)
        db.session.commit()
        return settings
