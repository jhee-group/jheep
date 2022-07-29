from ..models import ModelFile
from .base import BaseRepository, UUIDRepositoryMixin


class ModelFileRepository(BaseRepository[ModelFile], UUIDRepositoryMixin[ModelFile]):
    model = ModelFile
