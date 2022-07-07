import uuid
from datetime import datetime, timezone
from typing import Mapping, TypedDict

from jheep.models import (
    M,
    ModelStore,
    ModelStoreCreate,
    Model,
    ModelCreate,
)
from jheep.config import settings


ModelMapping = Mapping[str, M]

now = datetime.now(timezone.utc)


class TestData(TypedDict):
    __test__ = False

    modelstore: ModelMapping[ModelStore]
    model: ModelMapping[Model]


store_id = uuid.uuid4()
model_id = uuid.uuid4()

modelstore: ModelMapping[ModelStore] = {
    "local": ModelStore(
        id=store_id,
        name="local",
        url=None,
    ),
}

model: ModelMapping[Model] = {
    "basic-model": Model(
        id=model_id,
        name="basic-model",
        path="basic-model/modelfile",
        modelstore_id=store_id,
    ),
}

data_mapping: TestData = {
    "modelstore": modelstore,
    "model": model,
}

__all__ = [
    "data_mapping",
    "TestData",
]
