from typing import AsyncContextManager, AsyncGenerator, Callable, Tuple

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from jheep.db.types import DatabaseConnectionParameters, DatabaseType


TestClientGeneratorType = Callable[[FastAPI], AsyncContextManager[httpx.AsyncClient]]

GetTestDatabase = Callable[
    ..., AsyncContextManager[Tuple[DatabaseConnectionParameters, DatabaseType]]
]

GetSessionManager = Callable[
    ..., AsyncContextManager[AsyncGenerator[AsyncSession, None]]
]
