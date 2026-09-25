"""Request and response contracts for authentication."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

HAS_LETTER = re.compile(r"[A-Za-z]")
HAS_DIGIT = re.compile(r"\d")


class RegisterSchema(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    password_confirmation: str

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Informe seu nome completo.")
        return cleaned

    @field_validator("password")
    @classmethod
    def enforce_password_policy(cls, value: str) -> str:
        if not HAS_LETTER.search(value) or not HAS_DIGIT.search(value):
            raise ValueError("A senha deve conter ao menos uma letra e um numero.")
        return value

    @model_validator(mode="after")
    def passwords_must_match(self) -> "RegisterSchema":
        if self.password != self.password_confirmation:
            raise ValueError("As senhas nao coincidem.")
        return self


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=PASSWORD_MAX_LENGTH)
    remember_me: bool = False


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    avatar_url: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None


def serialize_user(user) -> dict:
    return UserPublicSchema.model_validate(user).model_dump(mode="json")
