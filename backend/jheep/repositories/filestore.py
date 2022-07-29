from ..models import M, FileStore
from ..services.files import validate_url
from .base import BaseRepository, UUIDRepositoryMixin


class FileStoreRepository(BaseRepository[FileStore], UUIDRepositoryMixin[FileStore]):
    model = FileStore

    async def validate(self, object: M) -> bool:
        if validate_url(object.url):
            return True
        else:
            raise ValueError(f"{object.url} in invalid url")
