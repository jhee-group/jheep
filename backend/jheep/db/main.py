import contextlib
from typing import AsyncGenerator, AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from .engine import create_async_session_maker, create_async_engine
from ..config import settings


engine = create_async_engine(settings.get_database_connection_parameters())
session_maker = create_async_session_maker(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


def get_session_manager() -> AsyncContextManager[AsyncGenerator[AsyncSession, None]]:

    @contextlib.asynccontextmanager
    async def _get_session_manager(*args, **kwargs):
        yield get_session()

    return _get_session_manager


__all__ = [
    "session_maker",
    "get_session",
]
