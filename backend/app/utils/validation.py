"""Bridge between pydantic schemas and the domain error envelope."""

from __future__ import annotations

from typing import TypeVar

from flask import request
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from app.utils.exceptions import ValidationError

SchemaType = TypeVar("SchemaType", bound=BaseModel)


def parse_body(schema: type[SchemaType]) -> SchemaType:
    """Validate the JSON body against a schema or raise a 422."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError("Envie um corpo JSON valido.")

    try:
        return schema.model_validate(payload)
    except PydanticValidationError as error:
        raise ValidationError(details=_format_errors(error)) from error


def parse_query(schema: type[SchemaType]) -> SchemaType:
    """Validate the query string against a schema or raise a 422."""
    try:
        return schema.model_validate(request.args.to_dict())
    except PydanticValidationError as error:
        raise ValidationError(details=_format_errors(error)) from error


def _format_errors(error: PydanticValidationError) -> dict[str, str]:
    """Flatten pydantic errors into one message per field."""
    details: dict[str, str] = {}
    for item in error.errors():
        field = ".".join(str(part) for part in item["loc"]) or "body"
        details.setdefault(field, item["msg"])
    return details
