import uuid
from datetime import datetime, timezone
from typing import Mapping, TypedDict

from jheep.models import (
    M,
    FileStore,
    ModelFile,
)
from jheep.config import settings


ModelMapping = Mapping[str, M]

now = datetime.now(timezone.utc)


class TestData(TypedDict):
    __test__ = False

    filestore: ModelMapping[FileStore]
    modelfile: ModelMapping[ModelFile]


filestore_id = uuid.uuid4()
modelfile_id = uuid.uuid4()

filestore: ModelMapping[FileStore] = {
    "local": FileStore(
        id=filestore_id,
        url="file:///tmp",
    ),
}

model: ModelMapping[ModelFile] = {
    "basic-model": ModelFile(
        id=modelfile_id,
        name="basic-model",
        path="basic-model/modelfile",
        filestore_id=filestore_id,
    ),
}

data_mapping: TestData = {
    "filestore": filestore,
    "model": model,
}

__all__ = [
    "data_mapping",
    "TestData",
]
