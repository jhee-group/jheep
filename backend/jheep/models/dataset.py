from pydantic import UUID4, Json
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import JSON
from sqlalchemy_utils import UUIDType

from .filestore import File


class Dataset(File):
    __tablename__ = "dataset"

    id: UUID4 = Column(UUIDType, ForeignKey("file.id"), primary_key=True)
    name: str
    data_schema: Json | None = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "dataset",
    }
