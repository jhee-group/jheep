from pathlib import Path

from frul import furl
from pydantic import UUID4, AnyUrl, FileUrl

from .generics import BaseModel, UUIDModel, CreatedUpdatedAt


class FileStore(BaseModel, UUIDModel):
    url: AnyUrl | FileUrl | furl | str


class FileStoreCreate(FileStore):
    pass


class FileStoreUpdate(FileStore):
    pass


class FileModel(BaseModel, UUIDModel, CreatedUpdatedAt):
    path: Path | str
    filestore_id: UUID4
    filestore: FileStore
