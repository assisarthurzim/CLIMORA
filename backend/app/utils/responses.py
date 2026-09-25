"""Standard response envelope shared by every endpoint."""

from __future__ import annotations

from typing import Any

from flask import jsonify
from flask.wrappers import Response


def success_response(
    data: Any = None,
    meta: dict[str, Any] | None = None,
    status_code: int = 200,
) -> tuple[Response, int]:
    payload: dict[str, Any] = {"success": True, "data": data}
    if meta:
        payload["meta"] = meta
    return jsonify(payload), status_code


def error_response(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    status_code: int = 400,
) -> tuple[Response, int]:
    error: dict[str, Any] = {"code": code, "message": message}
    if details:
        error["details"] = details
    return jsonify({"success": False, "error": error}), status_code
