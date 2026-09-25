"""Cities saved by a user."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class FavoriteCity(BaseModel):
    __tablename__ = "favorite_cities"
    __table_args__ = (
        # Coordinates identify a place, not its name: two spellings of the same
        # city must not become two favourites.
        UniqueConstraint("user_id", "location_key", name="uq_favorite_user_location"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    state: Mapped[str | None] = mapped_column(String(160), nullable=True)
    country: Mapped[str | None] = mapped_column(String(160), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_key: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorite_cities")

    @property
    def display_name(self) -> str:
        return self.label or self.name
