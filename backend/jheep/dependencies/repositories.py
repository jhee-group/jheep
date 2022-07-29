from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.main import get_async_session
from ..repositories.base import get_repository
from ..repositories.filestore import FileStoreRepository
from ..repositories.model import ModelRepository


async def get_filestore_repository(
    session: AsyncSession = Depends(get_async_session),
) -> FileStoreRepository:
    return get_repository(FileStoreRepository, session)


async def get_model_repository(
    session: AsyncSession = Depends(get_async_session),
) -> ModelRepository:
    return get_repository(ModelRepository, session)
