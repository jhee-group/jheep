from .. import models as m, schemas as s
from .base import BaseRepository, UUIDRepositoryMixin


class DatasetRepository(
    BaseRepository[m.Dataset, s.DatasetCreate, s.DatasetUpdate],
    UUIDRepositoryMixin[m.Dataset],
):
    model = m.Dataset
