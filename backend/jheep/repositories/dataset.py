from ..models import Dataset
from .base import BaseRepository, UUIDRepositoryMixin


class DatasetRepository(BaseRepository[Dataset], UUIDRepositoryMixin[Dataset]):
    model = Dataset
