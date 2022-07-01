from typing import AsyncContextManager, Callable, Tuple

import httpx
from fastapi import FastAPI

from jheep.db.types import DatabaseConnectionParameters, DatabaseType


TestClientGeneratorType = Callable[[FastAPI], AsyncContextManager[httpx.AsyncClient]]

GetTestDatabase = Callable[
    ..., AsyncContextManager[Tuple[DatabaseConnectionParameters, DatabaseType]]
]
