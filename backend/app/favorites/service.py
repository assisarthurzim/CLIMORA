"""Business rules for favourite cities."""

from __future__ import annotations

from flask import current_app

from app.favorites.repository import FavoriteCityRepository
from app.favorites.schemas import FavoriteCreateSchema, FavoriteUpdateSchema
from app.models.favorite_city import FavoriteCity
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.geo import build_location_key, normalize_coordinate

MAX_FAVORITES_PER_USER = 50
NOT_FOUND_MESSAGE = "Cidade favorita não encontrada."


class FavoriteService:
    def __init__(self, repository: FavoriteCityRepository | None = None) -> None:
        self.repository = repository or FavoriteCityRepository()

    def list_favorites(self, user_id: int, search: str | None = None) -> list[FavoriteCity]:
        return self.repository.list_for_user(user_id, search)

    def add_favorite(self, user_id: int, payload: FavoriteCreateSchema) -> FavoriteCity:
        location_key = build_location_key(payload.latitude, payload.longitude)

        if self.repository.find_by_location(user_id, location_key):
            raise ConflictError("Esta cidade já está nos seus favoritos.")

        if self.repository.count_for_user(user_id) >= MAX_FAVORITES_PER_USER:
            raise ValidationError(
                f"Você atingiu o limite de {MAX_FAVORITES_PER_USER} cidades favoritas."
            )

        favorite = FavoriteCity(
            user_id=user_id,
            name=payload.name,
            state=payload.state,
            country=payload.country,
            country_code=payload.country_code,
            latitude=normalize_coordinate(payload.latitude),
            longitude=normalize_coordinate(payload.longitude),
            location_key=location_key,
            timezone=payload.timezone,
            label=payload.label,
            position=self.repository.next_position(user_id),
        )

        self.repository.add(favorite)
        current_app.logger.info("Favorite added user_id=%s location=%s", user_id, location_key)
        return favorite

    def update_favorite(
        self, user_id: int, favorite_id: int, payload: FavoriteUpdateSchema
    ) -> FavoriteCity:
        favorite = self._require(user_id, favorite_id)

        # Only the fields the caller actually sent are touched, so a partial
        # update never clears the others.
        changes = payload.model_dump(exclude_unset=True, exclude_none=True)
        if not changes:
            raise ValidationError("Informe ao menos um campo para atualizar.")

        return self.repository.update(favorite, **changes)

    def remove_favorite(self, user_id: int, favorite_id: int) -> None:
        favorite = self._require(user_id, favorite_id)
        self.repository.delete(favorite)
        current_app.logger.info("Favorite removed user_id=%s id=%s", user_id, favorite_id)

    def is_favorite(self, user_id: int, latitude: float, longitude: float) -> FavoriteCity | None:
        return self.repository.find_by_location(user_id, build_location_key(latitude, longitude))

    def _require(self, user_id: int, favorite_id: int) -> FavoriteCity:
        """Scoping the lookup by user makes another account's id a 404, not a 403."""
        favorite = self.repository.get_for_user(user_id, favorite_id)
        if favorite is None:
            raise NotFoundError(NOT_FOUND_MESSAGE)
        return favorite
