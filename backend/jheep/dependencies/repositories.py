from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.main import get_async_session
from ..repositories.base import get_repository
from ..repositories.filestore import FileStoreRepository
from ..repositories.mlmodel import MLModelRepository


async def get_filestore_repository(
    session: AsyncSession = Depends(get_async_session),
) -> FileStoreRepository:
    return get_repository(FileStoreRepository, session)


async def get_mlmodel_repository(
    session: AsyncSession = Depends(get_async_session),
) -> MLModelRepository:
    return get_repository(MLModelRepository, session)
