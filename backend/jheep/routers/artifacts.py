from fastapi import APIRouter, Depends
from fastapi_versioning import version

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.main import get_session
from ..models import Model, ModelCreate


router = APIRouter(
    prefix="/artifact",
    tags=['artifact'],
)


@router.get("/models", response_model=list[Model])
@version(1)
async def get_models(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Model))
    return result.scalars().all()


@router.post("/models")
@version(1)
async def add_model(model: ModelCreate, session: AsyncSession = Depends(get_session)):
    model = Model(name=model.name, url=model.url)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model
