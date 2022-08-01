from .. import models as m, schemas as s
from .base import BaseRepository, UUIDRepositoryMixin


class MLModelRepository(
    BaseRepository[m.MLModel, s.MLModelCreate, s.MLModelUpdate],
    UUIDRepositoryMixin[m.MLModel],
):
    model = m.MLModel
