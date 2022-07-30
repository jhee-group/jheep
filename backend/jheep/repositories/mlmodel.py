from ..models import MLModel
from .base import BaseRepository, UUIDRepositoryMixin


class MLModelRepository(BaseRepository[MLModel], UUIDRepositoryMixin[MLModel]):
    model = MLModel
