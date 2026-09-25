"""Chat completions over any OpenAI-compatible endpoint.

The /chat/completions contract is a de facto standard: OpenAI, Groq,
OpenRouter and a local Ollama all speak it. Keeping the base URL in
configuration means switching vendors is an environment change, not a code
change. Calling it over plain HTTP instead of a vendor SDK is what makes that
possible.
"""

from __future__ import annotations

from flask import current_app

from app.ai.providers.base import AIProvider, ChatCompletion, ChatTurn
from app.utils.exceptions import ExternalServiceError
from app.utils.http import HttpClient

DEFAULT_MODEL = "gpt-4o-mini"
MAX_TOKENS = 600
# Low temperature: the assistant interprets data, it does not invent prose.
TEMPERATURE = 0.3


class OpenAIProvider(AIProvider):
    name = "openai"

    @property
    def is_available(self) -> bool:
        return bool(current_app.config.get("OPENAI_KEY"))

    def complete(self, system_prompt: str, history: list[ChatTurn]) -> ChatCompletion:
        api_key = current_app.config.get("OPENAI_KEY")
        if not api_key:
            raise ExternalServiceError(
                "O assistente não está configurado. Defina OPENAI_KEY no ambiente."
            )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend({"role": turn.role, "content": turn.content} for turn in history)

        payload = self._post(api_key, messages)
        choices = payload.get("choices") or []
        if not choices:
            raise ExternalServiceError("O assistente não retornou resposta.")

        usage = payload.get("usage") or {}
        return ChatCompletion(
            content=choices[0].get("message", {}).get("content", "").strip(),
            tokens_used=usage.get("total_tokens"),
        )

    def _post(self, api_key: str, messages: list[dict[str, str]]) -> dict:
        import requests

        base_url = current_app.config["AI_BASE_URL"].rstrip("/")
        url = f"{base_url}/chat/completions"
        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": current_app.config.get("OPENAI_MODEL", DEFAULT_MODEL),
                    "messages": messages,
                    "max_tokens": MAX_TOKENS,
                    "temperature": TEMPERATURE,
                },
                timeout=current_app.config["AI_TIMEOUT"],
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout as error:
            raise ExternalServiceError("O assistente demorou demais para responder.") from error
        except requests.RequestException as error:
            current_app.logger.warning("OpenAI request failed: %s", error)
            raise ExternalServiceError("Não foi possível falar com o assistente agora.") from error


# Referenced so the shared client stays the single place documenting outbound
# conventions, even though this provider posts directly.
__all__ = ["OpenAIProvider", "HttpClient"]
