from furl import furl
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import String
from sqlalchemy_utils import UUIDType

from .generics import Base, UUIDModel, CreatedUpdatedAt


# FileStore model

class FileStore(UUIDModel, Base):
    __tablename__ = "filestore"
    __table_args__ = (UniqueConstraint("url"), )

    url = Column(String, nullable=False)
    files = relationship("File", back_populates="filestore")


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
