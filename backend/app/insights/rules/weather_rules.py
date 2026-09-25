"""The rule set behind Insights do Dia.

Adding an observation means adding a class here and listing it in the engine.
No existing rule changes.
"""

from __future__ import annotations

from datetime import datetime

from app.insights.base import Insight, InsightRule, InsightSeverity
from app.weather.providers.base import HourlyPoint, WeatherSnapshot

RAIN_LIKELY_THRESHOLD = 50
UV_HIGH_THRESHOLD = 6
UV_EXTREME_THRESHOLD = 10
STRONG_WIND_THRESHOLD = 40
COLD_THRESHOLD = 12
HEAT_THRESHOLD = 32
DRY_AIR_THRESHOLD = 30
GOOD_AIR_THRESHOLD = 20
POOR_AIR_THRESHOLD = 60
PLEASANT_NIGHT_RANGE = (15, 24)

WALK_TEMPERATURE_RANGE = (16, 27)
WALK_MAX_RAIN_CHANCE = 25
WALK_MAX_UV = 6
SUN_PEAK_HOURS = (12, 15)


def _today(snapshot: WeatherSnapshot):
    return snapshot.daily[0] if snapshot.daily else None


class RainRule(InsightRule):
    id = "rain"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        today = _today(snapshot)
        chance = today.precipitation_probability_max if today else None
        if chance is None or chance < RAIN_LIKELY_THRESHOLD:
            return None

        return Insight(
            id=self.id,
            title="Leve guarda-chuva",
            description=f"A chance de chuva chega a {round(chance)}% hoje.",
            icon="umbrella",
            severity=InsightSeverity.WARNING,
            priority=90,
        )


class UvRule(InsightRule):
    id = "uv"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        today = _today(snapshot)
        uv = today.uv_index_max if today else None
        if uv is None or uv < UV_HIGH_THRESHOLD:
            return None

        is_extreme = uv >= UV_EXTREME_THRESHOLD
        start, end = SUN_PEAK_HOURS
        return Insight(
            id=self.id,
            title="Índice UV elevado" if not is_extreme else "Índice UV extremo",
            description=(
                f"O UV chega a {round(uv)} hoje. Evite exposição ao Sol entre {start}h e {end}h "
                "e use protetor solar."
            ),
            icon="sun",
            severity=InsightSeverity.WARNING,
            priority=95 if is_extreme else 80,
        )


class WalkWindowRule(InsightRule):
    """Finds the next stretch of daylight hours comfortable for being outside."""

    id = "walk_window"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        window = self._find_window(snapshot.hourly, self._daylight_ranges(snapshot))
        if window is None:
            return None

        start, end = window
        return Insight(
            id=self.id,
            title="Bom horário para caminhar",
            description=(
                f"Entre {start:%H}h e {end:%H}h a temperatura fica agradável, "
                "com pouca chance de chuva."
            ),
            icon="person-walking",
            severity=InsightSeverity.POSITIVE,
            priority=60,
        )

    @staticmethod
    def _daylight_ranges(snapshot: WeatherSnapshot) -> list[tuple[datetime, datetime]]:
        return [
            (day.sunrise, day.sunset)
            for day in snapshot.daily
            if day.sunrise is not None and day.sunset is not None
        ]

    def _find_window(
        self, hourly: list[HourlyPoint], daylight: list[tuple[datetime, datetime]]
    ) -> tuple[datetime, datetime] | None:
        comfortable: list[HourlyPoint] = []

        for point in hourly[:24]:
            if self._is_comfortable(point, daylight):
                comfortable.append(point)
                continue
            if len(comfortable) >= 2:
                break
            comfortable = []

        if len(comfortable) < 2:
            return None
        return comfortable[0].time, comfortable[-1].time

    def _is_comfortable(
        self, point: HourlyPoint, daylight: list[tuple[datetime, datetime]]
    ) -> bool:
        if point.temperature is None or point.time is None:
            return False

        # Without this the rule recommends 21h to 00h: UV is zero at night, so
        # every other condition happens to pass.
        if not self._is_daylight(point.time, daylight):
            return False

        low, high = WALK_TEMPERATURE_RANGE
        rain = point.precipitation_probability or 0
        uv = point.uv_index or 0
        return low <= point.temperature <= high and rain <= WALK_MAX_RAIN_CHANCE and uv <= WALK_MAX_UV

    @staticmethod
    def _is_daylight(moment: datetime, daylight: list[tuple[datetime, datetime]]) -> bool:
        if not daylight:
            return False
        return any(sunrise <= moment <= sunset for sunrise, sunset in daylight)


class PleasantNightRule(InsightRule):
    id = "pleasant_night"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        today = _today(snapshot)
        minimum = today.temperature_min if today else None
        low, high = PLEASANT_NIGHT_RANGE
        if minimum is None or not low <= minimum <= high:
            return None

        return Insight(
            id=self.id,
            title="Noite agradável",
            description=f"A mínima fica em torno de {round(minimum)}°, boa para sair.",
            icon="moon",
            severity=InsightSeverity.POSITIVE,
            priority=40,
        )


class ColdRule(InsightRule):
    id = "cold"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        today = _today(snapshot)
        minimum = today.temperature_min if today else None
        if minimum is None or minimum > COLD_THRESHOLD:
            return None

        return Insight(
            id=self.id,
            title="Vai fazer frio",
            description=f"A mínima prevista é de {round(minimum)}°. Leve um casaco.",
            icon="temperature-low",
            severity=InsightSeverity.INFO,
            priority=75,
        )


class HeatRule(InsightRule):
    id = "heat"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        today = _today(snapshot)
        maximum = today.temperature_max if today else None
        if maximum is None or maximum < HEAT_THRESHOLD:
            return None

        return Insight(
            id=self.id,
            title="Calor intenso",
            description=f"A máxima chega a {round(maximum)}°. Beba água com frequência.",
            icon="temperature-high",
            severity=InsightSeverity.WARNING,
            priority=85,
        )


class WindRule(InsightRule):
    id = "wind"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        today = _today(snapshot)
        wind = today.wind_speed_max if today else None
        if wind is None or wind < STRONG_WIND_THRESHOLD:
            return None

        return Insight(
            id=self.id,
            title="Vento forte",
            description=f"Rajadas de até {round(wind)} km/h ao longo do dia.",
            icon="wind",
            severity=InsightSeverity.WARNING,
            priority=70,
        )


class DryAirRule(InsightRule):
    id = "dry_air"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        humidity = snapshot.current.humidity
        if humidity is None or humidity > DRY_AIR_THRESHOLD:
            return None

        return Insight(
            id=self.id,
            title="Ar seco",
            description=f"A umidade está em {round(humidity)}%. Hidrate-se mais que o habitual.",
            icon="droplet",
            severity=InsightSeverity.INFO,
            priority=65,
        )


class AirQualityRule(InsightRule):
    id = "air_quality"

    def evaluate(self, snapshot: WeatherSnapshot) -> Insight | None:
        air_quality = snapshot.air_quality
        index = air_quality.index if air_quality else None
        if index is None:
            return None

        if index <= GOOD_AIR_THRESHOLD:
            return Insight(
                id=self.id,
                title="Boa qualidade do ar",
                description="Condições favoráveis para atividades ao ar livre.",
                icon="leaf",
                severity=InsightSeverity.POSITIVE,
                priority=30,
            )

        if index >= POOR_AIR_THRESHOLD:
            return Insight(
                id=self.id,
                title="Qualidade do ar ruim",
                description=(
                    "Evite exercícios intensos ao ar livre, especialmente se tiver "
                    "problemas respiratórios."
                ),
                icon="lungs",
                severity=InsightSeverity.WARNING,
                priority=88,
            )

        return None
