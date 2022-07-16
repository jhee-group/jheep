from typing import List
from pathlib import Path

from pydantic import AnyUrl, FileUrl, Json
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.types import String
from sqlmodel import SQLModel, Field, Relationship

from .generics import UUID4, CreatedUpdatedAt, UUIDModel


# dataset store

class DatasetStoreBase(SQLModel):
    __table_args__ = (UniqueConstraint("url"), )

    name: str
    url: AnyUrl | FileUrl | None


class DatasetStore(DatasetStoreBase, UUIDModel, CreatedUpdatedAt, table=True):
    url: AnyUrl | FileUrl = Field(sa_column=Column(String, nullable=False))
    datasets: List["Dataset"] = Relationship(back_populates="datasetstore")


class DatasetStoreCreate(DatasetStoreBase):
    pass


# model

class DatasetBase(SQLModel):
    name: str
    manifest: Path
    schema: Json
    datasetstore_id: UUID4 | None = Field(default=None, foreign_key="datasetstore.id")


class Dataset(DatasetBase, UUIDModel, CreatedUpdatedAt, table=True):
    __table_args__ = (UniqueConstraint("modelstore_id", "path"), )

    manifest: str = Field(sa_column=Column(String, nullable=False))


class DatasetCreate(DatasetBase):
    pass
