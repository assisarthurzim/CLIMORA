"""Persistence for user accounts."""

from __future__ import annotations

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.find_one_by(email=User.normalize_email(email))

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None
