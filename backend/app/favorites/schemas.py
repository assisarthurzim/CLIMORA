"""Request and response contracts for favourite cities."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

NAME_MAX_LENGTH = 160
LABEL_MAX_LENGTH = 80


class FavoriteCreateSchema(BaseModel):
    name: str = Field(min_length=1, max_length=NAME_MAX_LENGTH)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    state: str | None = Field(default=None, max_length=NAME_MAX_LENGTH)
    country: str | None = Field(default=None, max_length=NAME_MAX_LENGTH)
    country_code: str | None = Field(default=None, max_length=2)
    timezone: str | None = Field(default=None, max_length=64)
    label: str | None = Field(default=None, max_length=LABEL_MAX_LENGTH)

    @field_validator("name", "label")
    @classmethod
    def collapse_whitespace(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value else value


class FavoriteUpdateSchema(BaseModel):
    label: str | None = Field(default=None, max_length=LABEL_MAX_LENGTH)
    position: int | None = Field(default=None, ge=0)

    @field_validator("label")
    @classmethod
    def collapse_whitespace(cls, value: str | None) -> str | None:
        return " ".join(value.split()) if value else value


class FavoriteQuerySchema(BaseModel):
    q: str | None = Field(default=None, max_length=NAME_MAX_LENGTH)


class FavoritePublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    label: str | None
    display_name: str
    state: str | None
    country: str | None
    country_code: str | None
    latitude: float
    longitude: float
    location_key: str
    timezone: str | None
    position: int
    created_at: datetime


def serialize_favorite(favorite) -> dict:
    return FavoritePublicSchema.model_validate(favorite).model_dump(mode="json")
