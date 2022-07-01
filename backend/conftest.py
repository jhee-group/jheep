import asyncio
import contextlib
from typing import (
    Any,
    AsyncContextManager,
    AsyncGenerator,
    Callable,
    Dict,
    Optional,
    Tuple,
)

import pytest
from sqlalchemy_utils import create_database, drop_database

from jheep.db import AsyncConnection, AsyncEngine, AsyncSession
from jheep.db.types import DatabaseConnectionParameters, DatabaseType, get_driver
from jheep.db.engine import create_engine
from jheep.models import Base
from jheep.settings import settings

from tests.data import TestData, data_mapping


GetTestDatabase = Callable[
    ..., AsyncContextManager[Tuple[DatabaseConnectionParameters, DatabaseType]]
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def get_test_database() -> GetTestDatabase:

    @contextlib.asynccontextmanager
    async def _get_test_database(
        *, name: str = "jheep_test"
    ) -> AsyncGenerator[Tuple[DatabaseConnectionParameters, DatabaseType], None]:
        url, connect_args = settings.get_database_connection_parameters(False)
        url = url.set(database=name)
        assert url.database == name
        create_database(url)
        yield ((url, connect_args), settings.database_type)
        drop_database(url)

    return _get_test_database


@pytest.fixture(scope="session")
async def test_database(
    get_test_database: GetTestDatabase,
) -> AsyncGenerator[Tuple[DatabaseConnectionParameters, DatabaseType], None]:
    async with get_test_database() as (database_connection_parameters, database_type):
        url, connect_args = database_connection_parameters
        url = url.set(drivername=get_driver(database_type, asyncio=True))
        yield (url, connect_args), database_type


@pytest.fixture(scope="session")
async def test_engine(
    test_database: Tuple[DatabaseConnectionParameters, DatabaseType],
) -> AsyncGenerator[AsyncEngine, None]:
    database_connection_parameters, _ = test_database
    engine = create_engine(database_connection_parameters)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_connection(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection, None]:
    async with test_engine.connect() as connection:
        yield connection


@pytest.fixture(scope="session")
async def create_test_db(test_connection: AsyncConnection):
    await test_connection.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
async def test_session(
    test_connection: AsyncConnection, create_main_db
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=test_connection, expire_on_commit=False) as session:
        await session.begin_nested()
        yield session
        await session.rollback()


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def test_data(test_connection: AsyncConnection) -> TestData:
    async with AsyncSession(bind=test_connection, expire_on_commit=False) as session:
        for model in data_mapping.values():
            for object in model.values():
                session.add(object)
        await session.commit()
    await test_connection.commit()
    yield data_mapping
