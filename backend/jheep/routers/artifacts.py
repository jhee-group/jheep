from typing import List

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlalchemy import select

from ..schemas import (
    FileStore, FileStoreCreate, FileRead,
    MLModel, MLModelCreate, MLModelRead,
)
from ..repositories import (
    FileStoreRepository,
    MLModelRepository,
)
from ..dependencies.repositories import (
    get_filestore_repository,
    get_mlmodel_repository,
)


router = APIRouter(
    prefix="/artifact",
    tags=['artifact'],
)


@router.get("/filestores", response_model=List[FileStore])
@version(1)
async def get_modelstores(
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
):
    return await filestore_repo.all()


@router.get("/mlmodels", response_model=List[MLModel])
@version(1)
async def get_mlmodels(
    mlmodel_repo: MLModelRepository = Depends(get_mlmodel_repository),
):
    return await mlmodel_repo.all()


@router.post("/filestore")
@version(1)
async def add_filestore(
    filestore: FileStoreCreate,
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
):
    s = FileStore(url=filestore.url)
    return await filestore_repo.create(s)


@router.post("/mlmodel")
@version(1)
async def add_mlmodel(
    mlmodel: MLModelCreate,
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
    mlmodel_repo: MLModelRepository = Depends(get_mlmodel_repository),
):
    statement = select(FileStore).where(FileStore.id == mlmodel.filestore_id)
    fs = await filestore_repo.get_one_or_none(statement)
    m = MLModel(name=mlmodel.name, path=mlmodel.path, filestore_id=fs.id)
    return await mlmodel_repo.create(m)
