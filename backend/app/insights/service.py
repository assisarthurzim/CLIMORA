"""Insight generation on top of the weather service."""

from __future__ import annotations

from app.insights.base import Insight
from app.insights.engine import DEFAULT_LIMIT, InsightRuleEngine
from app.weather.service import WeatherService


class InsightService:
    def __init__(
        self,
        weather_service: WeatherService | None = None,
        engine: InsightRuleEngine | None = None,
    ) -> None:
        self.weather_service = weather_service or WeatherService()
        self.engine = engine or InsightRuleEngine()

    def for_location(
        self, latitude: float, longitude: float, limit: int = DEFAULT_LIMIT
    ) -> list[Insight]:
        snapshot = self.weather_service.get_snapshot(latitude, longitude)
        return self.engine.evaluate(snapshot, limit)
