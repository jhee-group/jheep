from typing import List

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlalchemy import select

from .. import models as m, schemas as s
from ..repositories import FileStoreRepository
from ..dependencies.repositories import get_filestore_repository
from ..exceptions import ObjectNotFound


router = APIRouter(
    prefix="/artifact",
    tags=['artifact'],
)


@router.get("/filestores", response_model=List[s.FileStore])
@version(1)
async def get_filestores(
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
):
    db_objs = await filestore_repo.all()
    return [s.FileStore.from_orm(db_obj) for db_obj in db_objs]


@router.post("/filestore", response_model=s.FileStore)
@version(1)
async def add_filestore(
    obj: s.FileStoreCreate,
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
):
    return await filestore_repo.create(obj)


@router.put("/filestore", response_model=s.FileStore)
@version(1)
async def update_filestore(
    obj: s.FileStoreUpdate,
    filestore_repo: FileStoreRepository = Depends(get_filestore_repository),
):
    statement = select(m.FileStore).where(m.FileStore.id == obj.id)
    db_obj = await filestore_repo.get_one_or_none(statement)
    if db_obj is None:
        raise ObjectNotFound
    db_obj = await filestore_repo.update(db_obj=db_obj, obj=obj)
    return s.FileStore.from_orm(db_obj)
