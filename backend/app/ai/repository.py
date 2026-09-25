"""Persistence for assistant conversations."""

from __future__ import annotations

from sqlalchemy import select

from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    def list_for_user(self, user_id: int, include_archived: bool = False) -> list[Conversation]:
        statement = select(Conversation).where(Conversation.user_id == user_id)
        if not include_archived:
            statement = statement.where(Conversation.is_archived.is_(False))

        statement = statement.order_by(
            Conversation.last_message_at.desc().nullslast(), Conversation.created_at.desc()
        )
        return list(self.session.scalars(statement))

    def get_for_user(self, user_id: int, conversation_id: int) -> Conversation | None:
        return self.find_one_by(id=conversation_id, user_id=user_id)


class ConversationMessageRepository(BaseRepository[ConversationMessage]):
    model = ConversationMessage

    def list_for_conversation(self, conversation_id: int) -> list[ConversationMessage]:
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at, ConversationMessage.id)
        )
        return list(self.session.scalars(statement))

    def recent_turns(self, conversation_id: int, limit: int) -> list[ConversationMessage]:
        """The tail of the conversation, oldest first, for prompt history."""
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.desc(), ConversationMessage.id.desc())
            .limit(limit)
        )
        return list(reversed(list(self.session.scalars(statement))))
