import asyncio
from pathlib import Path

from pydantic import AnyUrl, FileUrl, validator
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import URLType
from sqlmodel import SQLModel, Field, Relationship, select

from ..services.files import validate_url, get_file_contents, get_file_sha256_hash
from ..db.main import get_session_manager
from .generics import UUID4, CreatedUpdatedAt, UUIDModel


class ModelStoreBase(SQLModel):
    __table_args__ = (UniqueConstraint("url"), )

    name: str
    url: AnyUrl | FileUrl | None

    @validator('url')
    def validate_url(cls, v, values, **kwargs):
        if validate_url(v):
            return v
        else:
            raise ValueError(f"{v} in invalid url")


class ModelStore(ModelStoreBase, UUIDModel, CreatedUpdatedAt, table=True):

    url: AnyUrl | FileUrl = Field(sa_column=Column(URLType, nullable=False))
    models: list["Model"] = Relationship(back_populates="modelstore")


class ModelStoreCreate(ModelStoreBase):
    pass


class ModelStoreRead(ModelStoreBase, UUIDModel, CreatedUpdatedAt):
    pass


class ModelBase(SQLModel):
    name: str
    path: str
    modelstore_id: UUID4 | None = Field(default=None, foreign_key="modelstore.id")


class Model(ModelBase, UUIDModel, CreatedUpdatedAt, table=True):
    __table_args__ = (UniqueConstraint("modelstore_id", "path"), )

    modelstore: ModelStore | None = Relationship(back_populates="models")

    """
    @validator('path')
    def validate_path(cls, v, values, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # The default policy doesn't create a loop by default for threads (only for main process)
            # Thus, we create one here and set it for future works.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        get_session_manager,
        full_path = loop.run_until_complete(cls._get_full_url(session, v))
        if validate_url(full_path):
            return v
        else:
            raise ValueError(f"{v} in invalid url")
    """
    async def _get_full_url(self, session: AsyncSession):
        statement = select(ModelStore.url).where(ModelStore.id == self.modelstore_id)
        try:
            results = await session.scalars(statement)
            store_url = results.unique().one()
            full_path = Path(str(store_url.path), self.path)
            return full_path
        except NoResultFound:
            return None

    async def get_contents(self, session: AsyncSession):
        full_path = await self._get_full_url(session)
        if full_path is None:
            return None
        else:
            contents = await anext(get_file_contents(full_path))
            return contents

    async def get_hash(self, session: AsyncSession):
        full_path = await self._get_full_url(session)
        if full_path is None:
            return None
        else:
            sha256 = await get_file_sha256_hash(full_path)
            return sha256


class ModelCreate(ModelBase):
    pass
