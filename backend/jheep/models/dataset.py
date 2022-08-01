from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import JSON, String
from sqlalchemy_utils import UUIDType

from .filestore import File


class Dataset(File):
    __tablename__ = "dataset"

    id = Column(UUIDType, ForeignKey("file.id"), primary_key=True)
    name = Column(String)
    data_schema = Column(JSON, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "dataset",
    }
