"""Insight endpoints."""

from __future__ import annotations

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.insights.service import InsightService
from app.utils.responses import success_response
from app.utils.validation import parse_query
from app.weather.schemas import CoordinatesSchema

insights_bp = Blueprint("insights", __name__)


@insights_bp.get("")
@jwt_required()
def list_insights():
    """Insights do Dia for one location."""
    coordinates = parse_query(CoordinatesSchema)
    insights = InsightService().for_location(coordinates.lat, coordinates.lon)
    return success_response([insight.to_dict() for insight in insights])
