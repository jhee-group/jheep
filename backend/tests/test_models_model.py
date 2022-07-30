from typing import Tuple
import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jheep.models import (
    FileStore,
    MLModel,
)
from jheep.repositories import (
    FileStoreRepository,
    MLModelRepository,
    get_repository,
)

from tests.data import TestData, filestore_id, mlmodel_id


@pytest.mark.asyncio
async def test_filestore(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    store1 = data_mapping["filestore"]["local"]

    filestore_repo = get_repository(FileStoreRepository, session)
    statement = select(FileStore).where(FileStore.id == filestore_id)
    store2 = await filestore_repo.get_one_or_none(statement)

    assert store2 is not None
    assert store1.url == store2.url
    assert await store2.validate()


@pytest.mark.asyncio
async def test_mlmodel(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    model1 = data_mapping["mlmodel"]["basic-model"]

    model_repo = get_repository(MLModelRepository, session)
    statement = select(MLModel).where(MLModel.id == mlmodel_id)
    model2 = await model_repo.get_one_or_none(statement)

    assert model2 is not None
    assert model1.path == model2.path
    assert await model2.validate()

    contents = await model2.get_contents()
    assert contents == b"1234567890"
