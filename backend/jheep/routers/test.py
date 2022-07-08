from typing import List

from fastapi import APIRouter, Depends
from fastapi_versioning import version

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from ..db.main import get_async_session
from ..models import Song, SongCreate


router = APIRouter(
    prefix="/test",
    tags=['test'],
)


@router.get("/ping")
@version(1)
async def pong():
    return {"ping": "pong!"}


@router.get("/songs", response_model=List[Song])
@version(1)
async def get_songs(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Song))
    return result.scalars().all()


@router.post("/songs")
@version(1)
async def add_song(song: SongCreate, session: AsyncSession = Depends(get_async_session)):
    song = Song(name=song.name, artist=song.artist, year=song.year)
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song
