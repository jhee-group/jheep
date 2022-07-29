from pathlib import Path

from pydantic import Json
from sqlalchemy import Column
from sqlalchemy.types import JSON

from .generics import BaseModel, UUIDModel, CreatedUpdatedAt
from .filestore import FileStore, FileModel


class DatasetBase(BaseModel):
    path: Path | str
    data_schema: Json | None
    filestore: FileStore


class Dataset(DatasetBase, FileModel, UUIDModel, CreatedUpdatedAt, table=True):
    name: str
    data_schema: Json | None = Column(JSON, nullable=True)


class DatasetCreate(DatasetBase):
    pass


class DatasetRead(DatasetBase):
    pass
