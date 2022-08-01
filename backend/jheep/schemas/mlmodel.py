from .filestore import FileBase
from .generics import UUIDModel, CreatedUpdatedAt


class MLModelBase(FileBase):
    name: str


class MLModel(UUIDModel, CreatedUpdatedAt, MLModelBase):
    pass


class MLModelCreate(MLModelBase):
    pass


class MLModelUpdate(UUIDModel, MLModelBase):
    pass
