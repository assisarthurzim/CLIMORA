"""WMO weather code interpretation.

Open-Meteo returns numeric codes; the UI needs a label and an icon. Keeping the
translation here means providers stay free of presentation concerns.
"""

from __future__ import annotations

from typing import NamedTuple


class WeatherCondition(NamedTuple):
    code: int
    label: str
    icon: str


UNKNOWN_CONDITION = WeatherCondition(-1, "Condição desconhecida", "cloud-question")

_CONDITIONS: dict[int, tuple[str, str]] = {
    0: ("Céu limpo", "sun"),
    1: ("Predominantemente limpo", "sun-cloud"),
    2: ("Parcialmente nublado", "cloud-sun"),
    3: ("Nublado", "cloud"),
    45: ("Nevoeiro", "fog"),
    48: ("Nevoeiro com geada", "fog"),
    51: ("Garoa leve", "drizzle"),
    53: ("Garoa moderada", "drizzle"),
    55: ("Garoa intensa", "drizzle"),
    56: ("Garoa congelante leve", "sleet"),
    57: ("Garoa congelante intensa", "sleet"),
    61: ("Chuva fraca", "rain"),
    63: ("Chuva moderada", "rain"),
    65: ("Chuva forte", "rain-heavy"),
    66: ("Chuva congelante fraca", "sleet"),
    67: ("Chuva congelante forte", "sleet"),
    71: ("Neve fraca", "snow"),
    73: ("Neve moderada", "snow"),
    75: ("Neve forte", "snow-heavy"),
    77: ("Granizo fino", "snow"),
    80: ("Pancadas de chuva fracas", "rain-showers"),
    81: ("Pancadas de chuva moderadas", "rain-showers"),
    82: ("Pancadas de chuva fortes", "rain-heavy"),
    85: ("Pancadas de neve fracas", "snow"),
    86: ("Pancadas de neve fortes", "snow-heavy"),
    95: ("Tempestade", "thunderstorm"),
    96: ("Tempestade com granizo", "thunderstorm"),
    99: ("Tempestade com granizo forte", "thunderstorm"),
}


def describe(code: int | None) -> WeatherCondition:
    if code is None or code not in _CONDITIONS:
        return UNKNOWN_CONDITION
    label, icon = _CONDITIONS[code]
    return WeatherCondition(code, label, icon)


_CARDINAL_POINTS = (
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO",
)


def describe_wind_direction(degrees: float | None) -> str | None:
    """Convert a bearing into a cardinal label."""
    if degrees is None:
        return None
    index = int((degrees % 360) / 22.5 + 0.5) % 16
    return _CARDINAL_POINTS[index]
