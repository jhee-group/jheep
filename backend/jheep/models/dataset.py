from pydantic import AnyUrl, FileUrl
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy_utils import URLType
from sqlmodel import SQLModel, Field

from .generics import CreatedUpdatedAt, UUIDModel


class DatasetBase(SQLModel):
    __table_args__ = (UniqueConstraint("url"), )
    name: str
    url: AnyUrl | FileUrl


class Dataset(DatasetBase, UUIDModel, CreatedUpdatedAt, table=True):
    url: AnyUrl | FileUrl = Field(sa_column=Column(URLType))


class DatasetCreate(DatasetBase):
    pass
