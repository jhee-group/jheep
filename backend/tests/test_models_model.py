import pytest

from tests.data import TestData


@pytest.mark.asyncio
async def test_fields(test_data: TestData):
    model = test_data["model"]["basic"]
    print(model)
    assert model.name == "basic"
    assert model.url == "file:///tmp/basic"
