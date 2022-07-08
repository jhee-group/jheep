from typing import List

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import select

from ..models import (
    ModelStore, ModelStoreCreate,
    Model, ModelCreate,
)
from ..repositories.model import (
    ModelStoreRepository,
    ModelRepository,
)
from ..dependencies.repositories import (
    get_modelstore_repository,
    get_model_repository,
)


router = APIRouter(
    prefix="/artifact",
    tags=['artifact'],
)


@router.get("/modelstores", response_model=List[ModelStore])
@version(1)
async def get_modelstores(
    modelstore_repo: ModelStoreRepository = Depends(get_modelstore_repository),
):
    return await modelstore_repo.all()


@router.get("/models", response_model=List[Model])
@version(1)
async def get_models(
    model_repo: ModelRepository = Depends(get_model_repository),
):
    return await model_repo.all()


@router.post("/modelstore")
@version(1)
async def add_modelstore(
    modelstore: ModelStoreCreate,
    modelstore_repo: ModelStoreRepository = Depends(get_modelstore_repository),
):
    s = ModelStore(name=modelstore.name, url=modelstore.url)
    return await modelstore_repo.create(s)


@router.post("/model")
@version(1)
async def add_model(
    model: ModelCreate,
    modelstore_repo: ModelStoreRepository = Depends(get_modelstore_repository),
    model_repo: ModelRepository = Depends(get_model_repository),
):
    statement = select(ModelStore).where(ModelStore.id == model.modelstore_id)
    ms = await modelstore_repo.get_one_or_none(statement)
    m = Model(name=model.name, path=str(model.path), modelstore_id=ms.id)
    return await model_repo.create(m)
