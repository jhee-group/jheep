from typing import Tuple

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from jheep.main import app

from tests.data import TestData, filestore_id, mlmodel_id


@pytest.mark.anyio
async def test_filestore(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/v1/artifact/filestores")
    assert response.status_code == 200
    assert response.json()[0]['id'] == filestore_id
