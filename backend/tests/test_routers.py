from typing import Tuple

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from jheep.config import settings

from tests.data import TestData


"""
@pytest.mark.asyncio
async def test_filestore(
    test_env: Tuple[TestData, AsyncSession, AsyncClient],
):
    session, data_mapping, client = test_env

    response = await client.get("/v1/artifact/filestores")

    assert response.status_code == 200
    assert response.json()[0]['id'] == filestore_id
"""
