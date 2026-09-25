"""Engine-level database configuration."""

from __future__ import annotations

from sqlalchemy import Engine, event


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    """SQLite ignores foreign keys unless the pragma is set per connection.

    Without this, every ON DELETE CASCADE declared in the models is silently a
    no-op and deleting an account leaves orphaned rows behind.
    """
    if type(dbapi_connection).__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
