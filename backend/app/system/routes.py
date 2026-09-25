"""Operational endpoints used by monitoring and by the frontend bootstrap."""

from __future__ import annotations

from flask import Blueprint, current_app
from sqlalchemy import inspect

from app.extensions import db
from app.utils.responses import success_response

system_bp = Blueprint("system", __name__)

API_VERSION = "1.0.0"

# A health check that only runs SELECT 1 reports success against an empty
# database, so it has to assert the schema is actually there.
EXPECTED_TABLES = frozenset(
    {
        "users",
        "user_settings",
        "favorite_cities",
        "search_history",
        "conversations",
        "conversation_messages",
    }
)


def _inspect_database() -> tuple[str, list[str]]:
    """Return the database status and any expected tables that are missing."""
    try:
        existing = set(inspect(db.engine).get_table_names())
    except Exception:  # noqa: BLE001 - the reason is logged, the caller sees a status
        current_app.logger.exception("Database health check failed")
        return "down", []

    missing = sorted(EXPECTED_TABLES - existing)
    return ("up" if not missing else "schema_incomplete"), missing


@system_bp.get("/health")
def health_check():
    """Report application and database availability."""
    database_status, missing_tables = _inspect_database()

    payload = {
        "application": "Climora",
        "version": API_VERSION,
        "environment": current_app.config["ENV_NAME"],
        "database": database_status,
    }
    if missing_tables:
        payload["missing_tables"] = missing_tables
        current_app.logger.error(
            "Schema incomplete, run 'flask db upgrade'. Missing: %s", ", ".join(missing_tables)
        )

    status_code = 200 if database_status == "up" else 503
    return success_response(payload, status_code=status_code)
