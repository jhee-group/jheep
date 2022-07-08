from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.main import get_async_session
from ..repositories.base import get_repository
from ..repositories.model import ModelStoreRepository, ModelRepository


async def get_modelstore_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ModelStoreRepository:
    return get_repository(ModelStoreRepository, session)


async def get_model_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ModelRepository:
    return get_repository(ModelRepository, session)
