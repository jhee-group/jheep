from pathlib import Path

from furl import furl
from pydantic import UUID4, AnyUrl, FileUrl

from .generics import BaseModel, UUIDModel, CreatedUpdatedAt


# FileStore schema

class FileStoreBase(BaseModel):
    url: AnyUrl | FileUrl | str


class FileStore(FileStoreBase, UUIDModel):

    class Config:
        orm_mode = True


class FileStoreCreate(FileStoreBase):
    pass


class FileStoreUpdate(FileStore):
    pass


# File schema

class FileBase(BaseModel):
    path: Path | str
    filestore_id: UUID4


class File(UUIDModel, CreatedUpdatedAt, FileBase):
    filestore: FileStore

    async def get_full_path(self):
        url = furl(self.filestore.url).add(path=self.path)
        return url


class FileCreate(FileBase):
    pass


class FileUpdate(UUIDModel, FileBase):
    pass
