"""Persistence for favourite cities."""

from __future__ import annotations

from sqlalchemy import func, or_, select

from app.models.favorite_city import FavoriteCity
from app.repositories.base import BaseRepository


class FavoriteCityRepository(BaseRepository[FavoriteCity]):
    model = FavoriteCity

    def list_for_user(self, user_id: int, search: str | None = None) -> list[FavoriteCity]:
        statement = select(FavoriteCity).where(FavoriteCity.user_id == user_id)

        if search:
            pattern = f"%{search.lower()}%"
            statement = statement.where(
                or_(
                    func.lower(FavoriteCity.name).like(pattern),
                    func.lower(FavoriteCity.label).like(pattern),
                    func.lower(FavoriteCity.state).like(pattern),
                    func.lower(FavoriteCity.country).like(pattern),
                )
            )

        statement = statement.order_by(FavoriteCity.position, FavoriteCity.created_at)
        return list(self.session.scalars(statement))

    def get_for_user(self, user_id: int, favorite_id: int) -> FavoriteCity | None:
        return self.find_one_by(id=favorite_id, user_id=user_id)

    def find_by_location(self, user_id: int, location_key: str) -> FavoriteCity | None:
        return self.find_one_by(user_id=user_id, location_key=location_key)

    def count_for_user(self, user_id: int) -> int:
        statement = select(func.count()).select_from(FavoriteCity).where(
            FavoriteCity.user_id == user_id
        )
        return self.session.scalar(statement) or 0

    def next_position(self, user_id: int) -> int:
        statement = select(func.max(FavoriteCity.position)).where(FavoriteCity.user_id == user_id)
        highest = self.session.scalar(statement)
        return (highest + 1) if highest is not None else 0
