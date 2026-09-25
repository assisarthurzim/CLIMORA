"""Insight contracts.

Insights are produced by deterministic rules, not by a language model: they
must be reproducible, testable and free to compute.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from app.weather.providers.base import WeatherSnapshot


class InsightSeverity(StrEnum):
    POSITIVE = "positive"
    INFO = "info"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class Insight:
    id: str
    title: str
    description: str
    icon: str
    severity: InsightSeverity
    priority: int

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "severity": str(self.severity)}


class InsightRule(ABC):
    """One observation about the forecast, evaluated in isolation."""

    id: str

    @abstractmethod
    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        """Return an insight when the condition applies, otherwise None."""
