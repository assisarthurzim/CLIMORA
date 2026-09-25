"""Shared HTTP client for outbound integrations.

Every external call goes through here so timeouts, retries, logging and error
translation are defined once instead of in each provider.
"""

from __future__ import annotations

import time
from typing import Any

import requests
from flask import current_app
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.utils.exceptions import ExternalServiceError

RETRYABLE_STATUS = (429, 500, 502, 503, 504)
MAX_RETRIES = 2
BACKOFF_FACTOR = 0.4


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=RETRYABLE_STATUS,
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


_session = _build_session()


class HttpClient:
    """Thin wrapper around a shared session, scoped to one upstream service."""

    def __init__(self, service_name: str, base_url: str, user_agent: str | None = None) -> None:
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {"Accept": "application/json"}
        if self.user_agent:
            headers["User-Agent"] = self.user_agent

        started_at = time.perf_counter()
        try:
            response = _session.get(
                url,
                params=params,
                headers=headers,
                timeout=current_app.config["EXTERNAL_API_TIMEOUT"],
            )
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            current_app.logger.info(
                "%s %s -> %s in %.0fms", self.service_name, path, response.status_code, elapsed_ms
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout as error:
            raise ExternalServiceError(
                f"O servico {self.service_name} demorou demais para responder."
            ) from error
        except requests.RequestException as error:
            current_app.logger.warning("%s request failed: %s", self.service_name, error)
            raise ExternalServiceError(
                f"Nao foi possivel consultar {self.service_name} no momento."
            ) from error
        except ValueError as error:
            raise ExternalServiceError(
                f"O servico {self.service_name} devolveu uma resposta invalida."
            ) from error
