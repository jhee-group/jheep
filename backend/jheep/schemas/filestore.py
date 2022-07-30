from pathlib import Path

from frul import furl
from pydantic import UUID4, AnyUrl, FileUrl

from .generics import BaseModel, UUIDModel, CreatedUpdatedAt


class FileStoreBase(BaseModel, UUIDModel):
    url: AnyUrl | FileUrl | furl | str


class FileStore(FileStoreBase):
    pass


class FileStoreCreate(FileStoreBase):
    pass


class FileStoreUpdate(FileStoreBase):
    pass


class FileStoreRead(FileStoreBase):
    pass


class FileBase(BaseModel, UUIDModel, CreatedUpdatedAt):
    path: Path | str
    filestore_id: UUID4
    filestore: FileStore


class File(FileBase):
    pass


class FileCreate(FileBase):
    pass


class FileUpdate(FileBase):
    pass


class FileRead(FileBase):
    pass
