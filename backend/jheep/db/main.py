import contextlib
from typing import AsyncGenerator, AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from .engine import create_async_session_maker, create_async_engine
from ..config import settings


async_engine = create_async_engine(settings.get_database_connection_parameters())
async_session_maker = create_async_session_maker(async_engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


__all__ = [
    "async_session_maker",
    "get_async_session",
]
