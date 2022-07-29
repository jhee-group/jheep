from .filestore import BaseModel, FileStore, FileModel


class ModelFile(ModelFileBase, FileModel, table=True):
    pass
