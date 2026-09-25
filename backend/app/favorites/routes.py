"""Favourite city endpoints."""

from __future__ import annotations

from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required

from app.favorites.schemas import (
    FavoriteCreateSchema,
    FavoriteQuerySchema,
    FavoriteUpdateSchema,
    serialize_favorite,
)
from app.favorites.service import FavoriteService
from app.utils.responses import success_response
from app.utils.validation import parse_body, parse_query

favorites_bp = Blueprint("favorites", __name__)


@favorites_bp.get("")
@jwt_required()
def list_favorites():
    query = parse_query(FavoriteQuerySchema)
    favorites = FavoriteService().list_favorites(current_user.id, query.q)
    return success_response([serialize_favorite(favorite) for favorite in favorites])


@favorites_bp.post("")
@jwt_required()
def add_favorite():
    payload = parse_body(FavoriteCreateSchema)
    favorite = FavoriteService().add_favorite(current_user.id, payload)
    return success_response(serialize_favorite(favorite), status_code=201)


@favorites_bp.patch("/<int:favorite_id>")
@jwt_required()
def update_favorite(favorite_id: int):
    payload = parse_body(FavoriteUpdateSchema)
    favorite = FavoriteService().update_favorite(current_user.id, favorite_id, payload)
    return success_response(serialize_favorite(favorite))


@favorites_bp.delete("/<int:favorite_id>")
@jwt_required()
def remove_favorite(favorite_id: int):
    FavoriteService().remove_favorite(current_user.id, favorite_id)
    return success_response({"message": "Cidade removida dos favoritos."})
