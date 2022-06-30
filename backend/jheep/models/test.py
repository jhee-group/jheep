from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel

from .generics import CreatedUpdatedAt, UUIDModel


class SongBase(SQLModel):
    __table_args__ = (UniqueConstraint("name", "artist"), )
    name: str
    artist: str
    year: Optional[int] = None


class Song(SongBase, UUIDModel, CreatedUpdatedAt, table=True):
    pass


class SongCreate(SongBase):
    pass
