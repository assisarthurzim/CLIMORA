"""User account."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.favorite_city import FavoriteCity
    from app.models.search_history import SearchHistory
    from app.models.user_settings import UserSettings

EMAIL_MAX_LENGTH = 255
NAME_MAX_LENGTH = 120


class User(BaseModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=False, unique=True, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False, passive_deletes=True
    )
    favorite_cities: Mapped[list["FavoriteCity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    search_history: Mapped[list["SearchHistory"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    @staticmethod
    def normalize_email(email: str) -> str:
        """Emails are matched case-insensitively; store them folded."""
        return email.strip().lower()
