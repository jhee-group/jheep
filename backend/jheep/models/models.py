from typing import List
from pathlib import Path

from pydantic import AnyUrl, FileUrl
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.types import String
from sqlmodel import SQLModel, Field, Relationship

from .generics import UUID4, CreatedUpdatedAt, UUIDModel


# model store

class ModelStoreBase(SQLModel):
    __table_args__ = (UniqueConstraint("url"), )

    name: str
    url: AnyUrl | FileUrl | None


class ModelStore(ModelStoreBase, UUIDModel, CreatedUpdatedAt, table=True):

    url: AnyUrl | FileUrl = Field(sa_column=Column(String, nullable=False))
    models: List["Model"] = Relationship(back_populates="modelstore")


class ModelStoreCreate(ModelStoreBase):
    pass


# model

class ModelBase(SQLModel):
    name: str
    path: Path
    modelstore_id: UUID4 | None = Field(default=None, foreign_key="modelstore.id")


class Model(ModelBase, UUIDModel, CreatedUpdatedAt, table=True):
    __table_args__ = (UniqueConstraint("modelstore_id", "path"), )

    path: str
    modelstore: ModelStore = Relationship(back_populates="models")


class ModelCreate(ModelBase):
    pass
