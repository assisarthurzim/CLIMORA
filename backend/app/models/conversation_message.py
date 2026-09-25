"""Single turn inside an assistant conversation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import BaseModel
from app.models.enums import MessageRole

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class ConversationMessage(BaseModel):
    __tablename__ = "conversation_messages"

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, native_enum=False, length=20), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Snapshot of the weather data that grounded this answer. Stored so an
    # archived conversation can be audited against the facts it was given.
    weather_context: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
