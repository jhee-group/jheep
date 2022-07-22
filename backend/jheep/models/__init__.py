from sqlmodel.sql.expression import Select, SelectOfScalar

from .generics import M_UUID, M
from .models import (
    ModelStore, ModelStoreCreate,
    Model, ModelCreate,
)

from .test import Song, SongCreate


SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

__all__ = [
    "M",
    "M_UUID",
    "Dataset",
    "ModelStore",
    "ModelStoreCreate",
    "Model",
    "ModelCreate",
    "Song",
    "SongCreate",
]
