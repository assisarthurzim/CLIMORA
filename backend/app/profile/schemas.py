"""Request contracts for account management."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.auth.schemas import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, HAS_DIGIT, HAS_LETTER
from app.models.enums import TemperatureUnit, ThemePreference, WindSpeedUnit

NAME_MAX_LENGTH = 120
AVATAR_URL_MAX_LENGTH = 512


class UpdateProfileSchema(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=NAME_MAX_LENGTH)
    avatar_url: str | None = Field(default=None, max_length=AVATAR_URL_MAX_LENGTH)

    @field_validator("name")
    @classmethod
    def collapse_whitespace(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Informe seu nome completo.")
        return cleaned


class ChangePasswordSchema(BaseModel):
    current_password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    new_password_confirmation: str

    @field_validator("new_password")
    @classmethod
    def enforce_password_policy(cls, value: str) -> str:
        if not HAS_LETTER.search(value) or not HAS_DIGIT.search(value):
            raise ValueError("A senha deve conter ao menos uma letra e um número.")
        return value

    @model_validator(mode="after")
    def validate_change(self) -> "ChangePasswordSchema":
        if self.new_password != self.new_password_confirmation:
            raise ValueError("As senhas não coincidem.")
        if self.new_password == self.current_password:
            raise ValueError("A nova senha deve ser diferente da atual.")
        return self


class DeleteAccountSchema(BaseModel):
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)


class UpdateSettingsSchema(BaseModel):
    temperature_unit: TemperatureUnit | None = None
    wind_speed_unit: WindSpeedUnit | None = None
    theme: ThemePreference | None = None
    language: str | None = Field(default=None, max_length=10)


class SettingsPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    temperature_unit: TemperatureUnit
    wind_speed_unit: WindSpeedUnit
    theme: ThemePreference
    language: str


def serialize_settings(settings) -> dict:
    return SettingsPublicSchema.model_validate(settings).model_dump(mode="json")
