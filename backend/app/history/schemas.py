"""Request and response contracts for the search history."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import SearchSource

MAX_PER_PAGE = 50
QUERY_MAX_LENGTH = 200


class HistoryCreateSchema(BaseModel):
    query: str = Field(min_length=1, max_length=QUERY_MAX_LENGTH)
    city_name: str = Field(min_length=1, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    state: str | None = Field(default=None, max_length=160)
    country: str | None = Field(default=None, max_length=160)
    country_code: str | None = Field(default=None, max_length=2)
    source: SearchSource = SearchSource.MANUAL

    @field_validator("query", "city_name")
    @classmethod
    def collapse_whitespace(cls, value: str) -> str:
        return " ".join(value.split())


class HistoryQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=MAX_PER_PAGE)
    q: str | None = Field(default=None, max_length=QUERY_MAX_LENGTH)


class HistoryPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    query: str
    city_name: str
    state: str | None
    country: str | None
    country_code: str | None
    latitude: float
    longitude: float
    location_key: str
    source: SearchSource
    created_at: datetime


def serialize_history(entry) -> dict:
    return HistoryPublicSchema.model_validate(entry).model_dump(mode="json")
