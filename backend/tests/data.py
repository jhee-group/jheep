import uuid
from datetime import datetime, timezone
from typing import Mapping, TypedDict

from jheep.models import (
    M,
    FileStore,
    MLModel,
)
from jheep.config import settings


ModelMapping = Mapping[str, M]

now = datetime.now(timezone.utc)


class TestData(TypedDict):
    __test__ = False

    filestore: ModelMapping[FileStore]
    mlmodel: ModelMapping[MLModel]


filestore_id = uuid.uuid4()
mlmodel_id = uuid.uuid4()

filestore: ModelMapping[FileStore] = {
    "local": FileStore(
        id=filestore_id,
        url="file:///tmp",
    ),
}

mlmodel: ModelMapping[MLModel] = {
    "basic-model": MLModel(
        id=mlmodel_id,
        name="basic-model",
        path="basic-model/modelfile",
        filestore_id=filestore_id,
    ),
}

data_mapping: TestData = {
    "filestore": filestore,
    "mlmodel": mlmodel,
}

__all__ = [
    "data_mapping",
    "TestData",
]
