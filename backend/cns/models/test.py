from typing import Optional

from sqlalchemy import UniqueConstraint

from .generics import CreatedUpdatedAt, UUIDModel
from sqlmodel import SQLModel


class SongBase(SQLModel):
    __table_args__ = (UniqueConstraint("name", "artist"), )
    name: str
    artist: str
    year: Optional[int] = None


class Song(SongBase, UUIDModel, CreatedUpdatedAt, table=True):
    pass


class SongCreate(SongBase):
    pass
