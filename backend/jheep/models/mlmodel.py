from sqlalchemy import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import String
from sqlalchemy_utils import UUIDType

from .filestore import File


class MLModel(File):
    __tablename__ = "mlmodel"

    id = Column(UUIDType, ForeignKey("file.id"), primary_key=True)
    name = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "mlmodel",
    }
