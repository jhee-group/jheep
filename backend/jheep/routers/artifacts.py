from fastapi import APIRouter, Depends
from fastapi_versioning import version

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..db.main import get_session
from ..models import (
    ModelStore, ModelStoreCreate,
    Model, ModelCreate,
)


router = APIRouter(
    prefix="/artifact",
    tags=['artifact'],
)


@router.get("/modelstores", response_model=list[ModelStore])
@version(1)
async def get_modelstores(session: AsyncSession = Depends(get_session)):
    statements = select(ModelStore)
    result = await session.execute(statements)
    return result.scalars().all()


@router.get("/models", response_model=list[Model])
@version(1)
async def get_models(session: AsyncSession = Depends(get_session)):
    statements = select(Model).join(ModelStore)
    result = await session.execute(statements)
    return result.scalars().all()


@router.post("/modelstore")
@version(1)
async def add_modelstore(modelstore: ModelStoreCreate, session: AsyncSession = Depends(get_session)):
    s = ModelStore(name=modelstore.name, url=modelstore.url)
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return s


@router.post("/model")
@version(1)
async def add_model(model: ModelCreate, session: AsyncSession = Depends(get_session)):
    m = Model(name=model.name, path=model.path, modelstore_id=model.modelstore_id)
    session.add(m)
    await session.commit()
    await session.refresh(m)
    return m
