"""Cache abstraction.

An in-memory backend ships today; swapping in Redis later means registering a
different implementation here, with no change to any service.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from typing import Any


class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Any | None: ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int) -> None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...


class InMemoryTTLCache(CacheBackend):
    """Thread-safe dictionary cache with per-entry expiry."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


_cache: CacheBackend = InMemoryTTLCache()


def get_cache() -> CacheBackend:
    return _cache


def build_cache_key(namespace: str, *parts: Any) -> str:
    return ":".join([namespace, *(str(part) for part in parts)])
