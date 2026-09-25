"""Assistant orchestration: scope, context, model, persistence."""

from __future__ import annotations

from flask import current_app

from app.ai.context_builder import WeatherContextBuilder
from app.ai.prompts import OUT_OF_SCOPE_REPLY, build_system_prompt
from app.ai.providers.base import AIProvider, ChatTurn
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.repository import ConversationMessageRepository, ConversationRepository
from app.ai.schemas import ChatRequestSchema
from app.ai.scope_validator import is_weather_related
from app.extensions import db
from app.models.base import utcnow
from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage
from app.models.enums import MessageRole
from app.utils.exceptions import NotFoundError
from app.weather.service import WeatherService

HISTORY_TURNS = 8
TITLE_MAX_LENGTH = 60
NOT_FOUND_MESSAGE = "Conversa não encontrada."


class AIService:
    def __init__(
        self,
        provider: AIProvider | None = None,
        weather_service: WeatherService | None = None,
        context_builder: WeatherContextBuilder | None = None,
    ) -> None:
        self.provider = provider or OpenAIProvider()
        self.weather_service = weather_service or WeatherService()
        self.context_builder = context_builder or WeatherContextBuilder()
        self.conversations = ConversationRepository()
        self.messages = ConversationMessageRepository()

    def chat(self, user_id: int, payload: ChatRequestSchema) -> dict:
        conversation = self._resolve_conversation(user_id, payload)
        # Captured before storing the question, so the current turn does not
        # count as its own history.
        has_history = bool(self.messages.recent_turns(conversation.id, 1))
        user_message = self._store(conversation, MessageRole.USER, payload.message)

        # Layer one: obvious off-topic questions never reach the model.
        if not is_weather_related(payload.message, has_history=has_history):
            current_app.logger.info("Out-of-scope question from user_id=%s", user_id)
            answer = self._store(conversation, MessageRole.ASSISTANT, OUT_OF_SCOPE_REPLY)
            return self._result(conversation, user_message, answer)

        # Layer two: real data goes into the prompt so nothing is invented.
        snapshot = self.weather_service.get_snapshot(payload.lat, payload.lon)
        context = self.context_builder.build(snapshot)

        # Layer three: instructions the model must not step outside.
        completion = self.provider.complete(
            build_system_prompt(context, snapshot.location.name), self._history(conversation)
        )

        answer = self._store(
            conversation,
            MessageRole.ASSISTANT,
            completion.content,
            weather_context=snapshot.to_dict()["current"],
            token_count=completion.tokens_used,
        )
        return self._result(conversation, user_message, answer)

    def list_conversations(self, user_id: int) -> list[Conversation]:
        return self.conversations.list_for_user(user_id)

    def list_messages(self, user_id: int, conversation_id: int) -> list[ConversationMessage]:
        conversation = self._require(user_id, conversation_id)
        return self.messages.list_for_conversation(conversation.id)

    def delete_conversation(self, user_id: int, conversation_id: int) -> None:
        self.conversations.delete(self._require(user_id, conversation_id))

    def _resolve_conversation(self, user_id: int, payload: ChatRequestSchema) -> Conversation:
        if payload.conversation_id is not None:
            return self._require(user_id, payload.conversation_id)

        # The first question becomes the title, so the list is readable without
        # opening every thread.
        title = payload.message[:TITLE_MAX_LENGTH]
        return self.conversations.add(Conversation(user_id=user_id, title=title))

    def _require(self, user_id: int, conversation_id: int) -> Conversation:
        conversation = self.conversations.get_for_user(user_id, conversation_id)
        if conversation is None:
            raise NotFoundError(NOT_FOUND_MESSAGE)
        return conversation

    def _history(self, conversation: Conversation) -> list[ChatTurn]:
        turns = self.messages.recent_turns(conversation.id, HISTORY_TURNS)
        return [ChatTurn(role=str(turn.role), content=turn.content) for turn in turns]

    def _store(
        self,
        conversation: Conversation,
        role: MessageRole,
        content: str,
        weather_context: dict | None = None,
        token_count: int | None = None,
    ) -> ConversationMessage:
        message = ConversationMessage(
            conversation_id=conversation.id,
            role=role,
            content=content,
            weather_context=weather_context,
            token_count=token_count,
        )
        db.session.add(message)
        conversation.last_message_at = utcnow()
        db.session.commit()
        return message

    @staticmethod
    def _result(
        conversation: Conversation,
        question: ConversationMessage,
        answer: ConversationMessage,
    ) -> dict:
        return {"conversation": conversation, "question": question, "answer": answer}
