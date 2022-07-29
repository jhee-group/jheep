from sqlmodel.sql.expression import Select, SelectOfScalar

from .generics import M, M_UUID
from .filestore import FileStore
from .dataset import Dataset, DatasetCreate, DatasetRead
from .modelfile import ModelFile, ModelFileCreate, ModelFileRead
from .test import Song, SongCreate


SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

__all__ = [
    "M",
    "M_UUID",
    "FileStore",
    "Dataset",
    "DatasetCreate",
    "DatasetRead",
    "ModelFile",
    "ModelFileCreate",
    "ModelFileRead",
    "Song",
    "SongCreate",
]
