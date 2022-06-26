from fastapi import APIRouter, Depends
from fastapi_versioning import version

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.main import get_session
from ..models import Song, SongCreate


router = APIRouter(
    prefix="/test",
    tags=['test'],
)


@router.get("/ping")
@version(1)
async def pong():
    return {"ping": "pong!"}


@router.get("/songs", response_model=list[Song])
@version(1)
async def get_songs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Song))
    return result.scalars().all()


@router.post("/songs")
@version(1)
async def add_song(song: SongCreate, session: AsyncSession = Depends(get_session)):
    song = Song(name=song.name, artist=song.artist, year=song.year)
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song
