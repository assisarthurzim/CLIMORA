"""Request and response contracts for the assistant."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import MessageRole

MESSAGE_MAX_LENGTH = 1000
TITLE_MAX_LENGTH = 160


class ChatRequestSchema(BaseModel):
    message: str = Field(min_length=1, max_length=MESSAGE_MAX_LENGTH)
    conversation_id: int | None = None
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)

    @field_validator("message")
    @classmethod
    def collapse_whitespace(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Escreva uma pergunta.")
        return cleaned


class MessagePublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: MessageRole
    content: str
    created_at: datetime


class ConversationPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    is_archived: bool
    last_message_at: datetime | None
    created_at: datetime


def serialize_message(message) -> dict:
    return MessagePublicSchema.model_validate(message).model_dump(mode="json")


def serialize_conversation(conversation) -> dict:
    return ConversationPublicSchema.model_validate(conversation).model_dump(mode="json")
