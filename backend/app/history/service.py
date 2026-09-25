"""Business rules for the search history."""

from __future__ import annotations

from datetime import timedelta

from app.history.repository import SearchHistoryRepository
from app.history.schemas import HistoryCreateSchema
from app.models.base import ensure_utc, utcnow
from app.models.search_history import SearchHistory
from app.utils.exceptions import NotFoundError
from app.utils.geo import build_location_key, normalize_coordinate

# Reopening the same city minutes apart is one visit, not two entries.
DEDUPLICATION_WINDOW = timedelta(minutes=10)
NOT_FOUND_MESSAGE = "Registro de histórico não encontrado."


class HistoryService:
    def __init__(self, repository: SearchHistoryRepository | None = None) -> None:
        self.repository = repository or SearchHistoryRepository()

    def record(self, user_id: int, payload: HistoryCreateSchema) -> SearchHistory:
        location_key = build_location_key(payload.latitude, payload.longitude)

        recent = self.repository.most_recent(user_id)
        if self._is_duplicate(recent, location_key):
            return recent

        entry = SearchHistory(
            user_id=user_id,
            query=payload.query,
            city_name=payload.city_name,
            state=payload.state,
            country=payload.country,
            country_code=payload.country_code,
            latitude=normalize_coordinate(payload.latitude),
            longitude=normalize_coordinate(payload.longitude),
            location_key=location_key,
            source=payload.source,
        )
        return self.repository.add(entry)

    def list_history(
        self, user_id: int, page: int, per_page: int, search: str | None = None
    ) -> tuple[list[SearchHistory], dict[str, int]]:
        entries, total = self.repository.paginate_for_user(user_id, page, per_page, search)
        meta = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        }
        return entries, meta

    def delete_entry(self, user_id: int, entry_id: int) -> None:
        entry = self.repository.get_for_user(user_id, entry_id)
        if entry is None:
            raise NotFoundError(NOT_FOUND_MESSAGE)
        self.repository.delete(entry)

    def clear_history(self, user_id: int) -> int:
        return self.repository.clear_for_user(user_id)

    @staticmethod
    def _is_duplicate(recent: SearchHistory | None, location_key: str) -> bool:
        if recent is None or recent.location_key != location_key:
            return False
        return (utcnow() - ensure_utc(recent.created_at)) < DEDUPLICATION_WINDOW
