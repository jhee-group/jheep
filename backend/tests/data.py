import uuid
from datetime import datetime, timezone
from typing import Mapping, TypedDict

from jheep.models import (
    M,
    Model,
)
from jheep.settings import settings


ModelMapping = Mapping[str, M]

now = datetime.now(timezone.utc)


class TestData(TypedDict):
    __test__ = False

    models: ModelMapping[Model]


models: ModelMapping[Model] = {
    "basic": Model(
        id=uuid.uuid4(),
        name="basic",
        url="/tmp/basic",
    ),
}

data_mapping: TestData = {
    "models": models,
}

__all__ = [
    "data_mapping",
    "TestData",
]
