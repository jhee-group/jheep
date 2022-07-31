from typing import List

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlalchemy import select

from .. import models
from .. import schemas
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


@router.get("/filestores", response_model=List[schemas.FileStore])
@version(1)
async def get_modelstores(
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
):
    stores = await filestore_repo.all()
    return [schemas.FileStore.from_orm(fs) for fs in stores]


@router.get("/mlmodels", response_model=List[schemas.MLModel])
@version(1)
async def get_mlmodels(
    mlmodel_repo: MLModelRepository = Depends(get_mlmodel_repository),
):
    mlmodels = await mlmodel_repo.all()
    return [schemas.MLModel.from_orm(mm) for mm in mlmodels]


@router.post("/filestore")
@version(1)
async def add_filestore(
    filestore: schemas.FileStoreCreate,
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
):
    fs = models.FileStore(url=filestore.url)
    return await filestore_repo.create(fs)


@router.post("/mlmodel")
@version(1)
async def add_mlmodel(
    mlmodel: schemas.MLModelCreate,
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
    mlmodel_repo: MLModelRepository = Depends(get_mlmodel_repository),
):
    statement = select(models.FileStore).where(models.FileStore.id == mlmodel.filestore_id)
    fs = await filestore_repo.get_one_or_none(statement)
    m = models.MLModel(name=mlmodel.name, path=mlmodel.path, filestore_id=fs.id)
    return await mlmodel_repo.create(m)
