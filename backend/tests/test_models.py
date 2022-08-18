from typing import Tuple

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from jheep import models as m
from jheep import repositories as r

from tests.data import TestData, filestore_id, dataset_id, mlmodel_id


@pytest.mark.asyncio
async def test_filestore(test_env: Tuple[TestData, AsyncSession, AsyncClient]):
    data_mapping, session, client = test_env

    data_dict = data_mapping["filestores"]["local"]
    store1 = data_dict["model"]

    filestore_repo = r.get_repository(r.FileStoreRepository, session)
    statement = select(m.FileStore).where(m.FileStore.id == filestore_id)
    store2 = await filestore_repo.get_one_or_none(statement)

    assert store2 is not None
    assert store1.url == store2.url
    assert await store2.validate()


@pytest.mark.asyncio
async def test_dataset(test_env: Tuple[TestData, AsyncSession, AsyncClient]):
    data_mapping, session, _ = test_env

    data_dict = data_mapping["datasets"]["qm9"]
    dataset1 = data_dict["model"]

    dataset_repo = r.get_repository(r.DatasetRepository, session)
    statement = select(m.Dataset).where(m.Dataset.id == dataset_id)
    dataset2 = await dataset_repo.get_one_or_none(statement)

    assert dataset2 is not None
    assert dataset1.path == dataset2.path
    assert await dataset2.validate()

    contents = await dataset2.get_contents()
    assert contents == data_dict["contents"]


@pytest.mark.asyncio
async def test_mlmodel(test_env: Tuple[TestData, AsyncSession, AsyncClient]):
    data_mapping, session, _ = test_env

    data_dict = data_mapping["mlmodels"]["basic-model"]
    model1 = data_dict["model"]

    model_repo = r.get_repository(r.MLModelRepository, session)
    statement = select(m.MLModel).where(m.MLModel.id == mlmodel_id)
    model2 = await model_repo.get_one_or_none(statement)

    assert model2 is not None
    assert model1.path == model2.path
    assert await model2.validate()

    contents = await model2.get_contents()
    assert contents == data_dict["contents"]
