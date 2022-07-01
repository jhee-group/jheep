import pytest

from tests.data import TestData


@pytest.mark.asyncio
async def test_fields(test_data: TestData):
    model = test_data["models"]["basic"]
    assert model.fields == {
        "name": "basic",
        "url": "/tmp/basic",
    }
