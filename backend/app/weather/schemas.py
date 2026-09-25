"""Query contracts for the weather endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 120
MAX_SEARCH_RESULTS = 10


class CitySearchSchema(BaseModel):
    q: str = Field(min_length=MIN_QUERY_LENGTH, max_length=MAX_QUERY_LENGTH)
    limit: int = Field(default=5, ge=1, le=MAX_SEARCH_RESULTS)

    @field_validator("q")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < MIN_QUERY_LENGTH:
            raise ValueError("Informe ao menos dois caracteres.")
        return cleaned


class CoordinatesSchema(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
