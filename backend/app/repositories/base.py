"""Generic persistence operations shared by every repository.

Domain repositories subclass this and add only the queries their aggregate
needs, so no module rewrites basic CRUD.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.extensions import db
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, model: type[ModelType] | None = None) -> None:
        if model is not None:
            self.model = model

    @property
    def session(self) -> Session:
        return db.session

    def get_by_id(self, entity_id: int) -> ModelType | None:
        return self.session.get(self.model, entity_id)

    def list_all(self, limit: int | None = None, offset: int = 0) -> list[ModelType]:
        statement = select(self.model).offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.scalars(statement))

    def find_one_by(self, **filters: Any) -> ModelType | None:
        return self.session.scalars(select(self.model).filter_by(**filters).limit(1)).first()

    def find_all_by(self, **filters: Any) -> list[ModelType]:
        return list(self.session.scalars(select(self.model).filter_by(**filters)))

    def exists(self, **filters: Any) -> bool:
        return self.find_one_by(**filters) is not None

    def add(self, entity: ModelType, *, commit: bool = True) -> ModelType:
        self.session.add(entity)
        self._persist(commit)
        return entity

    def update(self, entity: ModelType, *, commit: bool = True, **values: Any) -> ModelType:
        for field, value in values.items():
            setattr(entity, field, value)
        self._persist(commit)
        return entity

    def delete(self, entity: ModelType, *, commit: bool = True) -> None:
        self.session.delete(entity)
        self._persist(commit)

    def _persist(self, commit: bool) -> None:
        """Commit, or flush when the caller owns the transaction boundary."""
        if commit:
            self.session.commit()
        else:
            self.session.flush()
