from typing import List

from fastapi import Depends
from fastapi_versioning import version
from sqlalchemy import select

from .. import models as m
from .. import schemas as s
from ..repositories import DatasetRepository
from ..dependencies.repositories import get_dataset_repository
from ..exceptions import ObjectNotFound
from .filestore import router


@router.get("/datasets", response_model=List[s.Dataset])
@version(1)
async def get_datasets(
    dataset_repo: DatasetRepository = Depends(get_dataset_repository),
):
    datasets = await dataset_repo.all()
    return [s.Dataset.from_orm(ds) for ds in datasets]


@router.post("/datasets")
@version(1)
async def add_dataset(
    obj: s.DatasetCreate,
    dataset_repo: DatasetRepository = Depends(get_dataset_repository),
):
    return await dataset_repo.create(obj)


@router.put("/datasets", response_model=s.Dataset)
@version(1)
async def update_dataset(
    obj: s.DatasetUpdate,
    dataset_repo: DatasetRepository = Depends(get_dataset_repository),
):
    statement = select(m.Dataset).where(m.Dataset.id == obj.id)
    db_obj = await dataset_repo.get_one_or_none(statement)
    if db_obj is None:
        raise ObjectNotFound
    db_obj = await dataset_repo.update(db_obj=db_obj, obj=obj)
    return s.Dataset.from_orm(db_obj)
