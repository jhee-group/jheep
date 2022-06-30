from sqlalchemy.ext.declarative import declarative_base

from .generics import M_UUID, M
from .models import Model, ModelCreate

from .test import Song, SongCreate


Base = declarative_base()

__all__ = [
    "Base",
    "M",
    "M_UUID",
    "Model",
    "ModelCreate",
    "Song",
    "SongCreate",
]
