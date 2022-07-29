from pathlib import Path

from furl import furl
from pydantic import UUID4, AnyUrl, FileUrl
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.orm import declarative_mixin, declared_attr, relationship
from sqlalchemy.types import String
from sqlalchemy_utils import UUIDType

from .generics import BaseModel, UUIDModel, CreatedUpdatedAt
from ..services.files import validate_url, get_file_contents, get_file_sha256_hash


# FileStore model

class FileStoreBase(BaseModel):
    url: AnyUrl | FileUrl | str | None = None


class FileStore(FileStoreBase, UUIDModel, CreatedUpdatedAt, table=True):
    __table_args__ = (UniqueConstraint("url"), )

    url: AnyUrl | FileUrl | str = Column(String, nullable=False)


# FileMixin

@declarative_mixin
class FileModel(BaseModel):
    __table_args__ = (UniqueConstraint("filestore_id", "path"), )

    path: Path | str = Column(String, nullable=False)
    filestore_id: UUID4 = Column(UUIDType, nullable=False, foreign_key="filestore.id")

    @declared_attr
    def filestore(cls):
        return relationship("FileStore")

    async def get_full_path(self):
        return furl(self.filestore.url).add({"path": self.path})

    async def validate(self) -> bool:
        full_path = await self.get_full_path()
        return validate_url(full_path)

    async def get_contents(self) -> bytes | None:
        full_path = await self.get_full_path()
        contents = await anext(get_file_contents(full_path))
        return contents

    async def get_hash(self) -> str | None:
        full_path = await self.get_full_path()
        sha256 = await get_file_sha256_hash(full_path.url)
        return sha256
