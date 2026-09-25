"""Global error handling.

Every failure leaves the application through here, so routes stay free of
try/except blocks and responses share one shape.
"""

from __future__ import annotations

from flask import Flask
from werkzeug.exceptions import HTTPException

from app.extensions import jwt
from app.utils.exceptions import ClimoraError
from app.utils.responses import error_response

HTTP_ERROR_CODES: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "AUTHENTICATION_ERROR",
    403: "AUTHORIZATION_ERROR",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
}

HTTP_ERROR_MESSAGES: dict[int, str] = {
    400: "Requisicao invalida.",
    401: "Sessao expirada ou inexistente. Entre novamente.",
    403: "Voce nao tem permissao para acessar este recurso.",
    404: "Recurso nao encontrado.",
    405: "Metodo nao permitido para este endereco.",
    409: "Este recurso ja existe.",
    422: "Os dados enviados sao invalidos.",
    429: "Muitas requisicoes. Aguarde alguns instantes.",
}

GENERIC_ERROR_MESSAGE = "Algo deu errado. Tente novamente em instantes."


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ClimoraError)
    def handle_domain_error(error: ClimoraError):
        app.logger.warning("%s: %s", error.error_code, error.message)
        return error_response(
            code=error.error_code,
            message=error.message,
            details=error.details,
            status_code=error.status_code,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        status = error.code or 500
        return error_response(
            code=HTTP_ERROR_CODES.get(status, "HTTP_ERROR"),
            message=HTTP_ERROR_MESSAGES.get(status, GENERIC_ERROR_MESSAGE),
            status_code=status,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        # The stack trace belongs in the log, never in the response body.
        app.logger.exception("Unhandled exception: %s", error)
        return error_response(
            code="INTERNAL_ERROR",
            message=GENERIC_ERROR_MESSAGE,
            status_code=500,
        )


def register_jwt_handlers(app: Flask) -> None:
    """Keep authentication failures inside the standard envelope."""

    @jwt.unauthorized_loader
    def handle_missing_token(_reason: str):
        return error_response(
            code="AUTHENTICATION_ERROR",
            message="Faca login para continuar.",
            status_code=401,
        )

    @jwt.invalid_token_loader
    def handle_invalid_token(_reason: str):
        return error_response(
            code="AUTHENTICATION_ERROR",
            message="Sessao invalida. Entre novamente.",
            status_code=401,
        )

    @jwt.expired_token_loader
    def handle_expired_token(_header: dict, _payload: dict):
        return error_response(
            code="TOKEN_EXPIRED",
            message="Sua sessao expirou. Entre novamente.",
            status_code=401,
        )

    @jwt.user_lookup_error_loader
    def handle_missing_user(_header: dict, _payload: dict):
        # The token is valid but the account no longer exists or was disabled.
        return error_response(
            code="AUTHENTICATION_ERROR",
            message="Conta indisponivel. Entre novamente.",
            status_code=401,
        )
