from pathlib import Path

from pydantic import UUID4, AnyUrl, FileUrl

from .generics import BaseModel, UUIDModel, CreatedUpdatedAt


# FileStore schema

class FileStoreBase(BaseModel):
    url: AnyUrl | FileUrl | str


class FileStore(FileStoreBase, UUIDModel):
    pass

    class Config:
        orm_mode = True


class FileStoreCreate(FileStoreBase):
    pass


class FileStoreUpdate(FileStoreBase):
    pass


class FileStoreRead(FileStore):
    pass


# File schema

class FileBase(BaseModel):
    path: Path | str
    filestore_id: UUID4


class File(UUIDModel, CreatedUpdatedAt, FileBase):
    filestore: FileStore


class FileCreate(FileBase):
    pass


class FileUpdate(FileBase):
    pass


class FileRead(File):
    pass
