from typing import AsyncContextManager, AsyncGenerator, Callable, Tuple

import httpx
from fastapi import FastAPI

from jheep.db import AsyncSession
from jheep.db.types import DatabaseConnectionParameters, DatabaseType


TestClientGeneratorType = Callable[[FastAPI], AsyncContextManager[httpx.AsyncClient]]

GetTestDatabase = Callable[
    ..., AsyncContextManager[Tuple[DatabaseConnectionParameters, DatabaseType]]
]

GetSessionManager = Callable[
    ..., AsyncContextManager[AsyncGenerator[AsyncSession, None]]
]
