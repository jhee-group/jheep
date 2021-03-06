import os
import asyncio
import contextlib
from typing import AsyncGenerator, Tuple
import uuid
import aiofiles
from pathlib import Path

os.environ["ENVIRONMENT"] = "test"


import pytest
from sqlalchemy_utils import create_database, drop_database
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession
from sqlmodel import SQLModel

from jheep.db.types import DatabaseConnectionParameters, DatabaseType, get_driver
from jheep.db.engine import create_async_engine
from jheep.config import settings

from tests.data import TestData, data_mapping
from tests.types import GetTestDatabase, GetSessionManager


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def get_test_database() -> GetTestDatabase:

    @contextlib.asynccontextmanager
    async def _get_test_database() -> AsyncGenerator[Tuple[DatabaseConnectionParameters, DatabaseType], None]:
        url, connect_args = settings.get_database_connection_parameters(False)
        create_database(url)
        yield (url, connect_args, settings.database_type)
        drop_database(url)

    return _get_test_database


@pytest.fixture(scope="session")
async def test_database(
    get_test_database: GetTestDatabase,
) -> AsyncGenerator[Tuple[DatabaseConnectionParameters, DatabaseType], None]:
    async with get_test_database() as (url, connect_args, database_type):
        url = url.set(drivername=get_driver(database_type, asyncio=True))
        yield (url, connect_args), database_type


@pytest.fixture(scope="session")
async def test_engine(
    test_database: Tuple[DatabaseConnectionParameters, DatabaseType],
) -> AsyncGenerator[AsyncEngine, None]:
    database_connection_parameters, _ = test_database
    engine = create_async_engine(database_connection_parameters)
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
    await test_connection.run_sync(SQLModel.metadata.create_all)


@pytest.fixture(scope="session")
async def test_session(
    test_connection: AsyncConnection, create_test_db
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=test_connection, expire_on_commit=False) as session:
        await session.begin_nested()
        yield session
        await session.rollback()


@pytest.fixture(scope="session")
def test_session_manager(test_session: AsyncSession):

    @contextlib.asynccontextmanager
    async def _test_session_manager(*args, **kwargs):
        yield test_session

    return _test_session_manager


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def test_file():
    filepath = data_mapping["model"]["basic-model"].path
    async with aiofiles.tempfile.TemporaryDirectory() as tmpd:
        path = Path(tmpd, filepath)
        path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        async with aiofiles.open(path, 'wb') as tmpf:
            await tmpf.write(b"1234567890")
        data_mapping["modelstore"]["local"].url = f"file://{tmpd}"
        yield


@pytest.fixture(scope="session")
@pytest.mark.asyncio
async def test_env(
    test_session_manager: GetSessionManager,
    test_file,
) -> Tuple[AsyncSession, TestData]:
    async with test_session_manager() as session:
        for model in data_mapping.values():
            for obj in model.values():
                session.add(obj)
        await session.commit()
        yield session, data_mapping


@pytest.fixture
def not_existing_uuid() -> uuid.UUID:
    return uuid.uuid4()
