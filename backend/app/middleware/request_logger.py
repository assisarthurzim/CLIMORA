"""Request lifecycle logging with a correlation id."""

from __future__ import annotations

import time
import uuid

from flask import Flask, Response, g, request

from app.utils.logger import get_client_ip

SKIPPED_PATHS = frozenset({"/api/v1/system/health"})


def register_request_logging(app: Flask) -> None:
    @app.before_request
    def start_timer() -> None:
        g.request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])
        g.started_at = time.perf_counter()

    @app.after_request
    def log_request(response: Response) -> Response:
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-")

        if request.path in SKIPPED_PATHS:
            return response

        elapsed_ms = (time.perf_counter() - getattr(g, "started_at", time.perf_counter())) * 1000
        app.logger.info(
            "%s %s -> %s in %.1fms from %s",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
            get_client_ip(),
        )
        return response
