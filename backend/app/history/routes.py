"""Search history endpoints."""

from __future__ import annotations

from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required

from app.history.schemas import HistoryCreateSchema, HistoryQuerySchema, serialize_history
from app.history.service import HistoryService
from app.utils.responses import success_response
from app.utils.validation import parse_body, parse_query

history_bp = Blueprint("history", __name__)


@history_bp.get("")
@jwt_required()
def list_history():
    query = parse_query(HistoryQuerySchema)
    entries, meta = HistoryService().list_history(
        current_user.id, query.page, query.per_page, query.q
    )
    return success_response([serialize_history(entry) for entry in entries], meta=meta)


@history_bp.post("")
@jwt_required()
def record_search():
    """Called when the user deliberately opens a city, not on every refresh."""
    payload = parse_body(HistoryCreateSchema)
    entry = HistoryService().record(current_user.id, payload)
    return success_response(serialize_history(entry), status_code=201)


@history_bp.delete("/<int:entry_id>")
@jwt_required()
def delete_entry(entry_id: int):
    HistoryService().delete_entry(current_user.id, entry_id)
    return success_response({"message": "Registro removido."})


@history_bp.delete("")
@jwt_required()
def clear_history():
    removed = HistoryService().clear_history(current_user.id)
    return success_response({"message": "Histórico limpo.", "removed": removed})
