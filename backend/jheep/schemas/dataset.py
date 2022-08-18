from .filestore import FileBase
from .generics import UUIDModel, CreatedUpdatedAt


class DatasetBase(FileBase):
    name: str


class Dataset(UUIDModel, CreatedUpdatedAt, DatasetBase):
    pass


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(UUIDModel, DatasetBase):
    pass
