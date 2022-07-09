from typing import Tuple
import pytest

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from jheep.models import ModelStore, Model
from jheep.repositories.base import get_repository
from jheep.repositories.model import (
    ModelStoreRepository,
    ModelRepository,
)

from tests.data import TestData


@pytest.mark.asyncio
async def test_model_store(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    store1 = data_mapping["modelstore"]["local"]
    assert store1.name == "local"

    modelstore_repo = get_repository(ModelStoreRepository, session)
    statement = select(ModelStore).where(ModelStore.name == store1.name)
    store2 = await modelstore_repo.get_one_or_none(statement)
    assert store2 is not None
    assert await modelstore_repo.validate(store2)


@pytest.mark.asyncio
async def test_model(test_env: Tuple[AsyncSession, TestData]):
    session, data_mapping = test_env

    model1 = data_mapping["model"]["basic-model"]
    assert model1.name == "basic-model"
    assert model1.path == "basic-model/modelfile"

    model_repo = get_repository(ModelRepository, session)
    statement = select(Model).where(Model.name == model1.name)
    model2 = await model_repo.get_one_or_none(statement)
    assert model2 is not None
    contents = await model_repo.get_contents(model2)
    assert contents == b"1234567890"
