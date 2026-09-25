"""Language model provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChatTurn:
    role: str
    content: str


@dataclass(frozen=True, slots=True)
class ChatCompletion:
    content: str
    tokens_used: int | None = None


class AIProvider(ABC):
    """Any model behind the assistant. Swapping vendors stops here."""

    name: str

    @property
    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def complete(self, system_prompt: str, history: list[ChatTurn]) -> ChatCompletion: ...
