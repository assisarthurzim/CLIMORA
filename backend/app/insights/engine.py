"""Runs every rule against a snapshot and ranks what came back."""

from __future__ import annotations

from flask import current_app

from app.insights.base import Insight, InsightRule
from app.insights.rules.weather_rules import (
    AirQualityRule,
    ColdRule,
    DryAirRule,
    HeatRule,
    PleasantNightRule,
    RainRule,
    UvRule,
    WalkWindowRule,
    WindRule,
)
from app.weather.providers.base import WeatherSnapshot

DEFAULT_LIMIT = 4

DEFAULT_RULES: tuple[type[InsightRule], ...] = (
    RainRule,
    UvRule,
    HeatRule,
    AirQualityRule,
    ColdRule,
    WindRule,
    DryAirRule,
    WalkWindowRule,
    PleasantNightRule,
)


class InsightRuleEngine:
    def __init__(self, rules: list[InsightRule] | None = None) -> None:
        self.rules = rules if rules is not None else [rule() for rule in DEFAULT_RULES]

    def evaluate(self, snapshot: WeatherSnapshot, limit: int = DEFAULT_LIMIT) -> list[Insight]:
        insights: list[Insight] = []

        for rule in self.rules:
            try:
                insight = rule.evaluate(snapshot)
            except Exception:  # noqa: BLE001 - one broken rule must not silence the rest
                current_app.logger.exception("Insight rule %s failed", rule.id)
                continue
            if insight is not None:
                insights.append(insight)

        insights.sort(key=lambda item: item.priority, reverse=True)
        return insights[:limit]
