"""Assistant endpoints."""

from __future__ import annotations

from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required

from app.ai.schemas import (
    ChatRequestSchema,
    serialize_conversation,
    serialize_message,
)
from app.ai.service import AIService
from app.extensions import limiter
from app.utils.responses import success_response
from app.utils.validation import parse_body

ai_bp = Blueprint("ai", __name__)

CHAT_RATE_LIMIT = "20 per minute"


@ai_bp.post("/chat")
@jwt_required()
@limiter.limit(CHAT_RATE_LIMIT)
def chat():
    """Ask the assistant, continuing a conversation or starting one."""
    payload = parse_body(ChatRequestSchema)
    result = AIService().chat(current_user.id, payload)

    return success_response(
        {
            "conversation": serialize_conversation(result["conversation"]),
            "question": serialize_message(result["question"]),
            "answer": serialize_message(result["answer"]),
        },
        status_code=201,
    )


@ai_bp.get("/conversations")
@jwt_required()
def list_conversations():
    conversations = AIService().list_conversations(current_user.id)
    return success_response([serialize_conversation(item) for item in conversations])


@ai_bp.get("/conversations/<int:conversation_id>/messages")
@jwt_required()
def list_messages(conversation_id: int):
    messages = AIService().list_messages(current_user.id, conversation_id)
    return success_response([serialize_message(message) for message in messages])


@ai_bp.delete("/conversations/<int:conversation_id>")
@jwt_required()
def delete_conversation(conversation_id: int):
    AIService().delete_conversation(current_user.id, conversation_id)
    return success_response({"message": "Conversa removida."})
