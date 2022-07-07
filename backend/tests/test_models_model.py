import pytest
from sqlmodel import select

from jheep.models import ModelStore, Model

from tests.data import TestData
from tests.types import GetSessionManager


@pytest.mark.asyncio
async def test_model_store(
    test_data: TestData,
):
    store = test_data["modelstore"]["local"]
    assert store.name == "local"


@pytest.mark.asyncio
async def test_fields(
    test_data: TestData,
    test_session_manager: GetSessionManager,
):
    model = test_data["model"]["basic-model"]
    assert model.name == "basic-model"
    assert model.path == "basic-model/modelfile"

    async with test_session_manager() as session:
        contents = await model.get_contents(session)
    assert contents == b"1234567890"
