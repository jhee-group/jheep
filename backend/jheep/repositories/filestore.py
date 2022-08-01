from .. import models as m, schemas as s
from ..services.files import validate_url
from .base import BaseRepository, UUIDRepositoryMixin


class FileStoreRepository(
    BaseRepository[m.FileStore, s.FileStoreCreate, s.FileStoreUpdate],
    UUIDRepositoryMixin[m.FileStore],
):
    model = m.FileStore

    async def validate(self, object: m.M) -> bool:
        if validate_url(object.url):
            return True
        else:
            raise ValueError(f"{object.url} in invalid url")
