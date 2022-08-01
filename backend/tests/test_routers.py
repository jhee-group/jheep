from typing import Tuple

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from jheep.config import settings

from tests.data import TestData, filestore_id, mlmodel_id


@pytest.mark.asyncio
async def test_filestore(
    test_env: Tuple[AsyncSession, TestData],
    test_client: AsyncClient,
):
    session, data_mapping = test_env
    client = test_client

    response = await client.get("/v1/artifact/filestores")

    assert response.status_code == 200
    assert response.json()[0]['id'] == filestore_id
