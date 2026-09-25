"""Model registry.

Importing this package registers every mapper, which Alembic autogenerate and
SQLAlchemy relationship resolution both depend on.
"""

from app.models.base import BaseModel, TimestampMixin, utcnow
from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage
from app.models.enums import (
    MessageRole,
    SearchSource,
    TemperatureUnit,
    ThemePreference,
    WindSpeedUnit,
)
from app.models.favorite_city import FavoriteCity
from app.models.search_history import SearchHistory
from app.models.user import User
from app.models.user_settings import UserSettings

__all__ = [
    "BaseModel",
    "Conversation",
    "ConversationMessage",
    "FavoriteCity",
    "MessageRole",
    "SearchHistory",
    "SearchSource",
    "TemperatureUnit",
    "ThemePreference",
    "TimestampMixin",
    "User",
    "UserSettings",
    "WindSpeedUnit",
    "utcnow",
]
