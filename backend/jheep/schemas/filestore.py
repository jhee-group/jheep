from pathlib import Path

from pydantic import UUID4, AnyUrl, FileUrl

from .generics import UUIDModel, CreatedUpdatedAt


class FileStoreBase(UUIDModel):
    url: AnyUrl | FileUrl | str


class FileStore(FileStoreBase):
    pass


class FileStoreCreate(FileStoreBase):
    pass


class FileStoreUpdate(FileStoreBase):
    pass


class FileStoreRead(FileStoreBase):
    pass


class FileBase(UUIDModel, CreatedUpdatedAt):
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
