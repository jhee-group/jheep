from typing import Tuple

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jheep import models as m
from jheep import repositories as r

from tests.data import TestData, filestore_id, mlmodel_id


@pytest.mark.asyncio
async def test_filestore(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    store1 = data_mapping["filestore"]["local"]

    filestore_repo = r.get_repository(r.FileStoreRepository, session)
    statement = select(m.FileStore).where(m.FileStore.id == filestore_id)
    store2 = await filestore_repo.get_one_or_none(statement)

    assert store2 is not None
    assert store1.url == store2.url
    assert await store2.validate()


@pytest.mark.asyncio
async def test_mlmodel(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    model1 = data_mapping["mlmodel"]["basic-model"]

    model_repo = r.get_repository(r.MLModelRepository, session)
    statement = select(m.MLModel).where(m.MLModel.id == mlmodel_id)
    model2 = await model_repo.get_one_or_none(statement)

    assert model2 is not None
    assert model1.path == model2.path
    assert await model2.validate()

    contents = await model2.get_contents()
    assert contents == b"1234567890"
