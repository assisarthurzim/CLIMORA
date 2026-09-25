"""Per-user preferences."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import TemperatureUnit, ThemePreference, WindSpeedUnit

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(BaseModel):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    temperature_unit: Mapped[TemperatureUnit] = mapped_column(
        Enum(TemperatureUnit, native_enum=False, length=20),
        default=TemperatureUnit.CELSIUS,
        nullable=False,
    )
    wind_speed_unit: Mapped[WindSpeedUnit] = mapped_column(
        Enum(WindSpeedUnit, native_enum=False, length=20),
        default=WindSpeedUnit.KMH,
        nullable=False,
    )
    theme: Mapped[ThemePreference] = mapped_column(
        Enum(ThemePreference, native_enum=False, length=20),
        default=ThemePreference.SYSTEM,
        nullable=False,
    )
    language: Mapped[str] = mapped_column(String(10), default="pt-BR", nullable=False)

    user: Mapped["User"] = relationship(back_populates="settings")
