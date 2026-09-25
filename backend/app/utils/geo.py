"""Geographic helpers shared across domains."""

from __future__ import annotations

# Four decimals is roughly 11 metres: precise enough to identify a city,
# tolerant enough that two lookups of the same place collapse into one key.
COORDINATE_PRECISION = 4


def normalize_coordinate(value: float) -> float:
    return round(float(value), COORDINATE_PRECISION)


def build_location_key(latitude: float, longitude: float) -> str:
    """Stable identifier for a place, used for uniqueness and cache keys."""
    return f"{normalize_coordinate(latitude):.4f},{normalize_coordinate(longitude):.4f}"
