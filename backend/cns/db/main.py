from typing import AsyncGenerator

from .engine import AsyncSession, create_async_session_maker, create_engine
from ..settings import settings


engine = create_engine(settings.get_database_connection_parameters())
session_maker = create_async_session_maker(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


__all__ = [
    "session_maker",
    "get_session",
]
