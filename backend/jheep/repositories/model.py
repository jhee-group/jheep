from pathlib import Path

from sqlalchemy.orm.exc import NoResultFound
from sqlmodel import select
from furl import furl

from ..models import M, ModelStore, Model
from ..services.files import validate_url, get_file_contents, get_file_sha256_hash
from .base import BaseRepository, UUIDRepositoryMixin


class ModelStoreRepository(BaseRepository[ModelStore], UUIDRepositoryMixin[ModelStore]):
    model = ModelStore

    async def count_all(self) -> int:
        statement = select(Model)
        return await self._count(statement)

    async def validate(self, object: M) -> bool:
        if validate_url(object.url):
            return True
        else:
            raise ValueError(f"{object.url} in invalid url")


class ModelRepository(BaseRepository[Model], UUIDRepositoryMixin[Model]):
    model = Model

    async def count_all(self) -> int:
        statement = select(Model)
        return await self._count(statement)

    async def validate(self, object: M) -> bool:
        full_path = await self._get_full_url(object)
        if validate_url(full_path):
            return True
        else:
            raise ValueError(f"{object.url} in invalid url")

    async def _get_store_url(self, object: M) -> furl | None:
        store_repo = ModelStoreRepository(self.session)
        statement = select(ModelStore).where(ModelStore.id == object.modelstore_id)
        try:
            store = await store_repo.get_one_or_none(statement)
            return furl(store.url)
        except NoResultFound:
            return None

    async def _get_full_url(self, object: M) -> furl | None:
        store_url = await self._get_store_url(object)
        if store_url is None:
            return None
        else:
            full_path = store_url.add(path=object.path)
            return full_path

    async def get_contents(self, object: M) -> bytes | None:
        full_path = await self._get_full_url(object)
        if full_path is None:
            return None
        else:
            contents = await anext(get_file_contents(full_path))
            return contents

    async def get_hash(self, object: M) -> str | None:
        full_path = await self._get_full_url(object)
        if full_path is None:
            return None
        else:
            sha256 = await get_file_sha256_hash(full_path.url)
            return sha256
