from .filestore import FileBase
from .generics import UUIDModel, CreatedUpdatedAt


class MLModelBase(FileBase):
    pass


class MLModel(UUIDModel, CreatedUpdatedAt, MLModelBase):
    pass


class MLModelCreate(MLModelBase):
    pass


class MLModelUpdate(MLModelBase):
    pass


class MLModelRead(MLModel):
    pass
