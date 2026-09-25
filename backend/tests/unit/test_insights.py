"""Insight rules and ranking."""

from datetime import date, datetime

from app.insights.base import InsightSeverity
from app.insights.engine import InsightRuleEngine
from app.insights.rules.weather_rules import (
    AirQualityRule,
    ColdRule,
    HeatRule,
    RainRule,
    UvRule,
    WalkWindowRule,
)
from app.weather.providers.base import (
    AirQuality,
    CurrentWeather,
    DailyPoint,
    HourlyPoint,
    Location,
    WeatherSnapshot,
)

SABARA = Location(name="Sabará", latitude=-19.8889, longitude=-43.8058)


def build_current(**overrides) -> CurrentWeather:
    defaults = dict(
        observed_at=datetime(2026, 7, 28, 9, 0),
        temperature=22.0,
        feels_like=22.0,
        temperature_min=18.0,
        temperature_max=28.0,
        humidity=60,
        pressure=1014.0,
        wind_speed=10.0,
        wind_direction=90,
        wind_direction_label="E",
        uv_index=3.0,
        visibility=20000.0,
        precipitation_probability=10,
        precipitation=0.0,
        cloud_cover=20,
        is_day=True,
        weather_code=0,
        condition="Céu limpo",
        icon="sun",
    )
    return CurrentWeather(**{**defaults, **overrides})


def build_day(**overrides) -> DailyPoint:
    defaults = dict(
        date=date(2026, 7, 28),
        temperature_min=18.0,
        temperature_max=28.0,
        precipitation_sum=0.0,
        precipitation_probability_max=10,
        wind_speed_max=15.0,
        uv_index_max=4.0,
        sunrise=datetime(2026, 7, 28, 6, 30),
        sunset=datetime(2026, 7, 28, 17, 40),
        weather_code=0,
        condition="Céu limpo",
        icon="sun",
    )
    return DailyPoint(**{**defaults, **overrides})


def build_hour(hour: int, **overrides) -> HourlyPoint:
    defaults = dict(
        time=datetime(2026, 7, 28, hour, 0),
        temperature=22.0,
        feels_like=22.0,
        precipitation_probability=5,
        precipitation=0.0,
        humidity=60,
        pressure=1014.0,
        wind_speed=10.0,
        uv_index=3.0,
        visibility=20000.0,
        weather_code=0,
        condition="Céu limpo",
        icon="sun",
    )
    return HourlyPoint(**{**defaults, **overrides})


def build_snapshot(current=None, daily=None, hourly=None, air_quality=None) -> WeatherSnapshot:
    return WeatherSnapshot(
        location=SABARA,
        current=current or build_current(),
        hourly=hourly or [],
        daily=daily or [build_day()],
        air_quality=air_quality,
    )


def test_rain_rule_fires_above_the_threshold():
    snapshot = build_snapshot(daily=[build_day(precipitation_probability_max=70)])

    insight = RainRule().evaluate(snapshot)

    assert insight is not None
    assert "70%" in insight.description
    assert insight.severity is InsightSeverity.WARNING


def test_rain_rule_stays_silent_on_a_dry_day():
    assert RainRule().evaluate(build_snapshot()) is None


def test_uv_rule_escalates_when_extreme():
    high = UvRule().evaluate(build_snapshot(daily=[build_day(uv_index_max=7.0)]))
    extreme = UvRule().evaluate(build_snapshot(daily=[build_day(uv_index_max=11.0)]))

    assert high.title == "Índice UV elevado"
    assert extreme.title == "Índice UV extremo"
    assert extreme.priority > high.priority


def test_cold_and_heat_rules_are_mutually_exclusive():
    cold_day = build_snapshot(daily=[build_day(temperature_min=8.0, temperature_max=18.0)])
    hot_day = build_snapshot(daily=[build_day(temperature_min=22.0, temperature_max=35.0)])

    assert ColdRule().evaluate(cold_day) is not None
    assert HeatRule().evaluate(cold_day) is None
    assert HeatRule().evaluate(hot_day) is not None
    assert ColdRule().evaluate(hot_day) is None


def test_air_quality_rule_reports_both_ends():
    good = AirQualityRule().evaluate(build_snapshot(air_quality=AirQuality(index=12, category="Boa")))
    poor = AirQualityRule().evaluate(build_snapshot(air_quality=AirQuality(index=80, category="Ruim")))
    middling = AirQualityRule().evaluate(
        build_snapshot(air_quality=AirQuality(index=40, category="Razoável"))
    )

    assert good.severity is InsightSeverity.POSITIVE
    assert poor.severity is InsightSeverity.WARNING
    assert middling is None


def test_walk_window_finds_a_comfortable_stretch():
    hourly = [
        build_hour(8, temperature=14.0),
        build_hour(9, temperature=19.0),
        build_hour(10, temperature=21.0),
        build_hour(11, temperature=23.0),
        build_hour(12, temperature=30.0),
    ]

    insight = WalkWindowRule().evaluate(build_snapshot(hourly=hourly))

    assert insight is not None
    assert "09h" in insight.description
    assert "11h" in insight.description


def test_walk_window_ignores_night_hours():
    """UV is zero after dark, so every other condition passes by accident."""
    hourly = [build_hour(hour, temperature=20.0, uv_index=0.0) for hour in (21, 22, 23)]

    assert WalkWindowRule().evaluate(build_snapshot(hourly=hourly)) is None


def test_walk_window_stays_silent_without_sun_times():
    from app.weather.providers.base import WeatherSnapshot

    snapshot = WeatherSnapshot(
        location=SABARA,
        current=build_current(),
        hourly=[build_hour(10), build_hour(11)],
        daily=[build_day(sunrise=None, sunset=None)],
    )

    assert WalkWindowRule().evaluate(snapshot) is None


def test_walk_window_stays_silent_when_it_rains_all_day():
    hourly = [build_hour(hour, precipitation_probability=90) for hour in range(8, 16)]

    assert WalkWindowRule().evaluate(build_snapshot(hourly=hourly)) is None


def test_engine_ranks_by_priority_and_respects_the_limit(app):
    snapshot = build_snapshot(
        daily=[build_day(precipitation_probability_max=80, uv_index_max=11.0, temperature_max=36.0)],
        air_quality=AirQuality(index=10, category="Boa"),
    )

    insights = InsightRuleEngine().evaluate(snapshot, limit=2)

    assert len(insights) == 2
    assert insights[0].priority >= insights[1].priority


def test_a_broken_rule_does_not_silence_the_others(app):
    class ExplodingRule:
        id = "exploding"

        def evaluate(self, snapshot):
            raise RuntimeError("boom")

    engine = InsightRuleEngine(rules=[ExplodingRule(), RainRule()])
    insights = engine.evaluate(build_snapshot(daily=[build_day(precipitation_probability_max=90)]))

    assert len(insights) == 1
    assert insights[0].id == "rain"
