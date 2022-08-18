from typing import AsyncContextManager, AsyncGenerator, Callable, Tuple

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from jheep.db.types import DatabaseConnectionParameters, DatabaseType


GetTestDatabase = Callable[
    ..., AsyncContextManager[Tuple[DatabaseConnectionParameters, DatabaseType]]
]

GetSessionManager = Callable[
    ..., AsyncContextManager[AsyncGenerator[AsyncSession, None]]
]

GetClientGenerator = Callable[
    [FastAPI], AsyncContextManager[AsyncGenerator[AsyncClient, None]]
]
