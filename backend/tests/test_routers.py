from typing import Tuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from jheep.main import app

from tests.data import TestData, filestore_id, mlmodel_id


client = TestClient(app)


@pytest.mark.asyncio
async def test_filestore(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    response = client.get("/v1/artifact/filestores")
    assert response.status_code == 200
    assert response.json()[0]['id'] == filestore_id
