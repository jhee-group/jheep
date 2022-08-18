import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, TypedDict

from jheep import models as m
from jheep.config import settings


ModelMapping = Mapping[str, Dict[str, Any]]

now = datetime.now(timezone.utc)


class TestData(TypedDict):
    __test__ = False

    filestores: ModelMapping
    datasets: ModelMapping
    mlmodels: ModelMapping


filestore_id = uuid.uuid4()
dataset_id = uuid.uuid4()
mlmodel_id = uuid.uuid4()

data_mapping: TestData = {
    "filestores": {
        "local": {
            "model": m.FileStore(
                id=filestore_id,
                url="file:///tmp",
            ),
        },
    },
    "datasets": {
        "qm9": {
            "model": m.Dataset(
                id=dataset_id,
                path="dataset/qm9",
                filestore_id=filestore_id,
            ),
            "contents": b"1234567890",
        },
    },
    "mlmodels": {
        "basic-model": {
            "model": m.MLModel(
                id=mlmodel_id,
                name="basic-model",
                path="mlmodel/basic-model",
                filestore_id=filestore_id,
            ),
            "contents": b"1234567890",
        },
    },
}

__all__ = [
    "data_mapping",
    "TestData",
]
