"""Model-level guarantees the rest of the application relies on."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Conversation, ConversationMessage, FavoriteCity, MessageRole, User
from app.utils.geo import build_location_key


def create_user(email: str = "ana@example.com") -> User:
    user = User(name="Ana", email=email, password_hash="hashed")
    db.session.add(user)
    db.session.commit()
    return user


def test_timestamps_are_populated_on_insert(app):
    user = create_user()

    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_email_must_be_unique(app):
    create_user()

    db.session.add(User(name="Outra", email="ana@example.com", password_hash="hashed"))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_same_place_cannot_be_favourited_twice(app):
    user = create_user()
    location_key = build_location_key(-19.8889, -43.8058)

    for name in ("Sabará", "Sabara"):
        db.session.add(
            FavoriteCity(
                user_id=user.id,
                name=name,
                latitude=-19.8889,
                longitude=-43.8058,
                location_key=location_key,
            )
        )

    with pytest.raises(IntegrityError):
        db.session.commit()


def test_deleting_a_user_removes_dependent_records(app):
    user = create_user()
    conversation = Conversation(user_id=user.id, title="Vai chover?")
    db.session.add(conversation)
    db.session.commit()

    db.session.add(
        ConversationMessage(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content="Vai chover hoje?",
        )
    )
    db.session.commit()

    db.session.delete(user)
    db.session.commit()

    assert db.session.query(Conversation).count() == 0
    assert db.session.query(ConversationMessage).count() == 0


def test_email_normalization_folds_case_and_whitespace():
    assert User.normalize_email("  Ana@Example.COM ") == "ana@example.com"


def test_naive_timestamps_from_sqlite_are_treated_as_utc(app):
    """SQLite drops the timezone, so reads must restore it before comparing."""
    from datetime import datetime, timezone

    from app.models.base import ensure_utc, utcnow

    naive = datetime(2026, 7, 27, 12, 0)
    restored = ensure_utc(naive)

    assert restored.tzinfo is timezone.utc
    assert isinstance(utcnow() - restored, type(utcnow() - utcnow()))


def test_ensure_utc_leaves_aware_values_untouched():
    from datetime import datetime, timedelta, timezone

    from app.models.base import ensure_utc

    aware = datetime(2026, 7, 27, 12, 0, tzinfo=timezone(timedelta(hours=-3)))

    assert ensure_utc(aware) is aware
    assert ensure_utc(None) is None
