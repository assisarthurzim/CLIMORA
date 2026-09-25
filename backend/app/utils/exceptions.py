"""Domain exception hierarchy.

Services raise these; routes never catch them. The global error handlers
translate each exception into an HTTP response.
"""

from __future__ import annotations

from typing import Any


class ClimoraError(Exception):
    """Base class for every expected failure in the application."""

    status_code = 500
    error_code = "INTERNAL_ERROR"
    default_message = "Algo deu errado. Tente novamente em instantes."

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ClimoraError):
    status_code = 422
    error_code = "VALIDATION_ERROR"
    default_message = "Os dados enviados sao invalidos."


class AuthenticationError(ClimoraError):
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    default_message = "Credenciais invalidas."


class AuthorizationError(ClimoraError):
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    default_message = "Voce nao tem permissao para acessar este recurso."


class NotFoundError(ClimoraError):
    status_code = 404
    error_code = "NOT_FOUND"
    default_message = "Recurso nao encontrado."


class ConflictError(ClimoraError):
    status_code = 409
    error_code = "CONFLICT"
    default_message = "Este recurso ja existe."


class RateLimitError(ClimoraError):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    default_message = "Muitas requisicoes. Aguarde alguns instantes."


class ExternalServiceError(ClimoraError):
    status_code = 502
    error_code = "EXTERNAL_SERVICE_ERROR"
    default_message = "Servico externo indisponivel no momento."


class OutOfScopeError(ClimoraError):
    """Raised when the assistant receives a request unrelated to weather."""

    status_code = 400
    error_code = "OUT_OF_SCOPE"
    default_message = "O assistente do Climora responde apenas sobre clima e tempo."
