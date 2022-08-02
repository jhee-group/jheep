import os
import asyncio
import contextlib
from typing import AsyncGenerator, Tuple
import uuid
import aiofiles
from pathlib import Path

os.environ["ENVIRONMENT"] = "test"


import pytest
from fastapi import FastAPI
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy_utils import create_database, drop_database
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

from jheep.main import app
from jheep.models import Base
from jheep.db.main import get_async_session
from jheep.db.types import DatabaseConnectionParameters, DatabaseType, get_driver
from jheep.db.engine import create_async_engine
from jheep.config import settings

from tests.data import TestData, data_mapping
from tests.types import GetTestDatabase, GetSessionManager, TestClientGeneratorType


fixture_scope = "session"


@pytest.fixture(scope=fixture_scope)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope=fixture_scope)
def get_test_database() -> GetTestDatabase:

    @contextlib.asynccontextmanager
    async def _get_test_database() -> AsyncGenerator[Tuple[DatabaseConnectionParameters, DatabaseType], None]:
        url, connect_args = settings.get_database_connection_parameters(False)
        create_database(url)
        yield (url, connect_args, settings.database_type)
        drop_database(url)

    return _get_test_database


@pytest.fixture(scope=fixture_scope)
async def test_database(
    get_test_database: GetTestDatabase,
) -> AsyncGenerator[Tuple[DatabaseConnectionParameters, DatabaseType], None]:
    async with get_test_database() as (url, connect_args, database_type):
        url = url.set(drivername=get_driver(database_type, asyncio=True))
        yield (url, connect_args), database_type


@pytest.fixture(scope=fixture_scope)
async def test_engine(
    test_database: Tuple[DatabaseConnectionParameters, DatabaseType],
) -> AsyncGenerator[AsyncEngine, None]:
    database_connection_parameters, _ = test_database
    engine = create_async_engine(database_connection_parameters)
    yield engine
    await engine.dispose()


@pytest.fixture(scope=fixture_scope)
async def test_connection(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncConnection, None]:
    async with test_engine.connect() as connection:
        yield connection


@pytest.fixture(scope=fixture_scope)
async def create_test_db(test_connection: AsyncConnection):
    await test_connection.run_sync(Base.metadata.create_all)


@pytest.fixture(scope=fixture_scope)
async def test_session(
    test_connection: AsyncConnection,
    create_test_db,
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=test_connection, expire_on_commit=False) as session:
        await session.begin_nested()
        yield session
        await session.rollback()


@pytest.fixture(scope=fixture_scope)
def test_session_manager(test_session: AsyncSession):

    @contextlib.asynccontextmanager
    async def _test_session_manager(*args, **kwargs):
        yield test_session

    return _test_session_manager


@pytest.fixture(scope=fixture_scope)
async def test_file():
    filepath = data_mapping["mlmodel"]["basic-model"].path
    async with aiofiles.tempfile.TemporaryDirectory() as tmpd:
        path = Path(tmpd, filepath)
        path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        async with aiofiles.open(path, 'wb') as tmpf:
            await tmpf.write(b"1234567890")
        data_mapping["filestore"]["local"].url = f"file://{tmpd}"
        yield


@pytest.fixture(scope=fixture_scope)
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
"""
@pytest.fixture(scope=fixture_scope)
async def test_env(
    test_file,
    test_session: AsyncSession,
) -> Tuple[AsyncSession, TestData]:
    for model in data_mapping.values():
        for obj in model.values():
            test_session.add(obj)
    await test_session.commit()
    for model in data_mapping.values():
        for obj in model.values():
            await test_session.refresh(obj)
    yield test_session, data_mapping
"""


@pytest.fixture(scope=fixture_scope)
def test_client_generator(
    test_session: AsyncSession,
):

    @contextlib.asynccontextmanager
    async def _test_client_generator(app: FastAPI):
        app.dependency_overrides = {}
        app.dependency_overrides[get_async_session] = test_session

        async with LifespanManager(app):
            async with AsyncClient(
                app=app,
                base_url="http://server:8801",
            ) as test_client:
                yield test_client

    return _test_client_generator


@pytest.fixture(scope=fixture_scope)
async def test_client(
    test_client_generator: TestClientGeneratorType,
) -> AsyncGenerator[AsyncClient, None]:
    async with test_client_generator(app) as client:
        yield client


@pytest.fixture
def not_existing_uuid() -> uuid.UUID:
    return uuid.uuid4()
