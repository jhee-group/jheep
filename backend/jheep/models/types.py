from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP
from sqlalchemy.types import TypeDecorator


class TIMESTAMPAware(TypeDecorator):
    """
    MySQL and SQLite will always return naive-Python datetimes.

    We store everything as UTC, but we want to have
    only offset-aware Python datetimes, even with MySQL and SQLite.
    """

    impl = TIMESTAMP
    cache_ok = True

    def process_result_value(self, value: datetime | None, dialect):
        if value is not None and dialect.name != "postgresql":
            return value.replace(tzinfo=timezone.utc)
        return value
