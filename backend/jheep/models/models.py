from pydantic import AnyUrl, FileUrl
from sqlalchemy import Column
from sqlalchemy_utils.types.url import URLType
from sqlmodel import SQLModel, Field

from .generics import CreatedUpdatedAt, UUIDModel


class ModelBase(SQLModel):
    name: str
    url: AnyUrl | FileUrl


class Model(ModelBase, UUIDModel, CreatedUpdatedAt, table=True):
    url: AnyUrl | FileUrl = Field(sa_column=Column(URLType))


class ModelCreate(ModelBase):
    pass
