"""Persistence for the search history."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, func, or_, select

from app.models.search_history import SearchHistory
from app.repositories.base import BaseRepository


class SearchHistoryRepository(BaseRepository[SearchHistory]):
    model = SearchHistory

    def paginate_for_user(
        self, user_id: int, page: int, per_page: int, search: str | None = None
    ) -> tuple[list[SearchHistory], int]:
        conditions = [SearchHistory.user_id == user_id]

        if search:
            pattern = f"%{search.lower()}%"
            conditions.append(
                or_(
                    func.lower(SearchHistory.query).like(pattern),
                    func.lower(SearchHistory.city_name).like(pattern),
                    func.lower(SearchHistory.country).like(pattern),
                )
            )

        total = self.session.scalar(
            select(func.count()).select_from(SearchHistory).where(*conditions)
        ) or 0

        statement = (
            select(SearchHistory)
            .where(*conditions)
            .order_by(SearchHistory.created_at.desc(), SearchHistory.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        return list(self.session.scalars(statement)), total

    def get_for_user(self, user_id: int, entry_id: int) -> SearchHistory | None:
        return self.find_one_by(id=entry_id, user_id=user_id)

    def most_recent(self, user_id: int) -> SearchHistory | None:
        statement = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc(), SearchHistory.id.desc())
            .limit(1)
        )
        return self.session.scalars(statement).first()

    def clear_for_user(self, user_id: int) -> int:
        result = self.session.execute(
            delete(SearchHistory).where(SearchHistory.user_id == user_id)
        )
        self.session.commit()
        return result.rowcount or 0

    def delete_older_than(self, user_id: int, cutoff: datetime) -> int:
        result = self.session.execute(
            delete(SearchHistory).where(
                SearchHistory.user_id == user_id, SearchHistory.created_at < cutoff
            )
        )
        self.session.commit()
        return result.rowcount or 0
