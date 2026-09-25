"""Weather endpoints."""

from __future__ import annotations

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.extensions import limiter
from app.utils.responses import success_response
from app.utils.validation import parse_query
from app.weather.schemas import CitySearchSchema, CoordinatesSchema
from app.weather.service import WeatherService

weather_bp = Blueprint("weather", __name__)

SEARCH_RATE_LIMIT = "60 per minute"
SNAPSHOT_RATE_LIMIT = "60 per minute"


@weather_bp.get("/search")
@jwt_required()
@limiter.limit(SEARCH_RATE_LIMIT)
def search_cities():
    """Autocomplete for the city search box."""
    query = parse_query(CitySearchSchema)
    results = WeatherService().search_cities(query.q, query.limit)
    return success_response([location.to_dict() for location in results])


@weather_bp.get("/reverse")
@jwt_required()
@limiter.limit(SEARCH_RATE_LIMIT)
def reverse_lookup():
    """Resolve the browser's coordinates into a named place."""
    coordinates = parse_query(CoordinatesSchema)
    location = WeatherService().reverse_lookup(coordinates.lat, coordinates.lon)
    return success_response(location.to_dict())


@weather_bp.get("/snapshot")
@jwt_required()
@limiter.limit(SNAPSHOT_RATE_LIMIT)
def snapshot():
    """Everything the dashboard needs for one location, in one call."""
    coordinates = parse_query(CoordinatesSchema)
    result = WeatherService().get_snapshot(coordinates.lat, coordinates.lon)
    return success_response(result.to_dict())


@weather_bp.get("/air-quality")
@jwt_required()
@limiter.limit(SNAPSHOT_RATE_LIMIT)
def air_quality():
    coordinates = parse_query(CoordinatesSchema)
    result = WeatherService().get_air_quality(coordinates.lat, coordinates.lon)
    return success_response(result.to_dict())
