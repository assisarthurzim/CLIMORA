"""Second containment layer: give the model the facts so it never guesses them.

The snapshot is rendered as compact text rather than raw JSON. Prose costs
fewer tokens and models follow it more reliably.
"""

from __future__ import annotations

from datetime import datetime

from app.insights.engine import InsightRuleEngine
from app.weather.providers.base import WeatherSnapshot

HOURS_IN_CONTEXT = 24
DAYS_IN_CONTEXT = 7

WEEKDAYS = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)
UNAVAILABLE = "sem dado"


def _value(number: float | int | None, unit: str = "") -> str:
    return UNAVAILABLE if number is None else f"{round(number)}{unit}"


def _clock(moment: datetime | None) -> str:
    return UNAVAILABLE if moment is None else moment.strftime("%H:%M")


class WeatherContextBuilder:
    def __init__(self, engine: InsightRuleEngine | None = None) -> None:
        self.engine = engine or InsightRuleEngine()

    def build(self, snapshot: WeatherSnapshot, now: datetime | None = None) -> str:
        sections = [
            self._location(snapshot, now),
            self._current(snapshot),
            self._yesterday(snapshot),
            self._hourly(snapshot),
            self._daily(snapshot),
            self._air_quality(snapshot),
            self._insights(snapshot),
        ]
        return "\n\n".join(section for section in sections if section)

    def _location(self, snapshot: WeatherSnapshot, now: datetime | None) -> str:
        location = snapshot.location
        place = ", ".join(part for part in (location.name, location.state, location.country) if part)
        moment = (now or datetime.now()).strftime("%d/%m/%Y às %H:%M")
        return f"LOCAL: {place}\nMOMENTO DA CONSULTA: {moment}"

    def _current(self, snapshot: WeatherSnapshot) -> str:
        current = snapshot.current
        return (
            "AGORA:\n"
            f"- Condição: {current.condition}\n"
            f"- Temperatura: {_value(current.temperature, '°C')} "
            f"(sensação {_value(current.feels_like, '°C')})\n"
            f"- Máxima hoje: {_value(current.temperature_max, '°C')} / "
            f"Mínima: {_value(current.temperature_min, '°C')}\n"
            f"- Umidade: {_value(current.humidity, '%')}\n"
            f"- Vento: {_value(current.wind_speed, ' km/h')} "
            f"{current.wind_direction_label or ''}".rstrip()
            + f"\n- Índice UV: {_value(current.uv_index)}\n"
            f"- Chance de chuva: {_value(current.precipitation_probability, '%')}\n"
            f"- Nascer do Sol: {_clock(current.sunrise)} / "
            f"Pôr do Sol: {_clock(current.sunset)}"
        )

    def _yesterday(self, snapshot: WeatherSnapshot) -> str:
        """Lets the assistant answer comparisons instead of declining them."""
        day = snapshot.previous_day
        if day is None or day.date is None:
            return ""

        return (
            f"ONTEM ({day.date:%d/%m}): {_value(day.temperature_min, '°')} a "
            f"{_value(day.temperature_max, '°')}, "
            f"chuva acumulada {_value(day.precipitation_sum, ' mm')}, "
            f"{day.condition}"
        )

    def _hourly(self, snapshot: WeatherSnapshot) -> str:
        points = snapshot.hourly[:HOURS_IN_CONTEXT]
        if not points:
            return ""

        lines = [
            f"- {_clock(point.time)}: {_value(point.temperature, '°C')}, "
            f"chuva {_value(point.precipitation_probability, '%')}, "
            f"UV {_value(point.uv_index)}, {point.condition}"
            for point in points
        ]
        return "PRÓXIMAS HORAS:\n" + "\n".join(lines)

    def _daily(self, snapshot: WeatherSnapshot) -> str:
        days = snapshot.daily[:DAYS_IN_CONTEXT]
        if not days:
            return ""

        lines = [
            f"- {WEEKDAYS[day.date.weekday()]} {day.date:%d/%m}: "
            f"{_value(day.temperature_min, '°')} a "
            f"{_value(day.temperature_max, '°')}, "
            f"chuva {_value(day.precipitation_probability_max, '%')}, "
            f"vento até {_value(day.wind_speed_max, ' km/h')}, "
            f"UV máx {_value(day.uv_index_max)}, {day.condition}"
            for day in days
            if day.date is not None
        ]
        return "PRÓXIMOS DIAS:\n" + "\n".join(lines)

    def _air_quality(self, snapshot: WeatherSnapshot) -> str:
        air_quality = snapshot.air_quality
        if air_quality is None:
            return ""
        return (
            f"QUALIDADE DO AR: {air_quality.category} "
            f"(índice {_value(air_quality.index)})"
        )

    def _insights(self, snapshot: WeatherSnapshot) -> str:
        insights = self.engine.evaluate(snapshot)
        if not insights:
            return ""
        lines = [f"- {insight.title}: {insight.description}" for insight in insights]
        return "OBSERVAÇÕES JÁ CALCULADAS:\n" + "\n".join(lines)
