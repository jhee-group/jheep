from typing import Tuple
import pytest

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from jheep.models import (
    FileStore,
    ModelFile,
)
from jheep.repositories import (
    FileStoreRepository,
    ModelFileRepository,
    get_repository,
)

from tests.data import TestData, filestore_id, modelfile_id


@pytest.mark.asyncio
async def test_file_store(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    store1 = data_mapping["filestore"]["local"]

    filestore_repo = get_repository(FileStoreRepository, session)
    statement = select(FileStore).where(FileStore.id == filestore_id)
    store2 = await filestore_repo.get_one_or_none(statement)

    assert store2 is not None
    assert store1.id == store2.id
    assert await store2.validate()


@pytest.mark.asyncio
async def test_model(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    model1 = data_mapping["model"]["basic-model"]

    model_repo = get_repository(ModelFileRepository, session)
    statement = select(ModelFile).where(ModelFile.id == modelfile_id)
    model2 = await model_repo.get_one_or_none(statement)

    assert model2 is not None
    assert model1.path == model2.path

    contents = await model2.get_contents()
    assert contents == b"1234567890"
