"""Record of every city lookup performed by a user."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import SearchSource

if TYPE_CHECKING:
    from app.models.user import User


class SearchHistory(BaseModel):
    __tablename__ = "search_history"
    __table_args__ = (
        # The history screen always reads the newest entries of one user.
        Index("ix_search_history_user_recent", "user_id", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    query: Mapped[str] = mapped_column(String(200), nullable=False)
    city_name: Mapped[str] = mapped_column(String(160), nullable=False)
    state: Mapped[str | None] = mapped_column(String(160), nullable=True)
    country: Mapped[str | None] = mapped_column(String(160), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_key: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    source: Mapped[SearchSource] = mapped_column(
        Enum(SearchSource, native_enum=False, length=20),
        default=SearchSource.MANUAL,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="search_history")
