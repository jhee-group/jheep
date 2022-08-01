from typing import List
from pathlib import Path

from furl import furl
from pydantic import UUID4, AnyUrl, FileUrl
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import String
from sqlalchemy_utils import UUIDType

from .generics import Base, UUIDModel, CreatedUpdatedAt
from ..services.files import validate_url, get_file_contents, get_file_sha256_hash


# FileStore model

class FileStore(UUIDModel, Base):
    __tablename__ = "filestore"
    __table_args__ = (UniqueConstraint("url"), )

    url = Column(String, nullable=False)
    files = relationship("File", back_populates="filestore")

    async def validate(self) -> bool:
        return validate_url(self.url)


# File model
class File(UUIDModel, CreatedUpdatedAt, Base):
    __tablename__ = "file"
    __table_args__ = (UniqueConstraint("filestore_id", "path"), )

    type = Column(String(32))
    path = Column(String, nullable=False)
    filestore_id = Column(UUIDType, ForeignKey("filestore.id"))
    filestore = relationship("FileStore", back_populates="files")

    __mapper_args__ = {
        "polymorphic_identity": "file",
        "polymorphic_on": type,
    }

    async def get_full_path(self):
        url = furl(self.filestore.url).add(path=self.path)
        return url

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
