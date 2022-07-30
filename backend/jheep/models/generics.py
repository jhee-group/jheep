import uuid
from datetime import datetime, timezone
from typing import TypeVar

from pydantic import UUID4
from sqlalchemy import Column
from sqlalchemy.orm import declarative_base, declarative_mixin
from sqlalchemy.sql import func
from sqlalchemy_utils import UUIDType

from .types import TIMESTAMPAware


Base = declarative_base()


class BaseModel:
    pass


@declarative_mixin
class UUIDModel(BaseModel):
    id: UUID4 = Column(UUIDType, primary_key=True, default=uuid.uuid4)


def now_utc():
    return datetime.now(timezone.utc)


@declarative_mixin
class CreatedUpdatedAt(BaseModel):
    created_at: datetime = Column(
        TIMESTAMPAware(timezone=True),
        nullable=False,
        index=True,
        default=now_utc,
        server_default=func.now(),
    )
    updated_at: datetime = Column(
        TIMESTAMPAware(timezone=True),
        nullable=False,
        index=True,
        default=now_utc,
        server_default=func.now(),
        onupdate=now_utc,
    )


M = TypeVar("M", bound=BaseModel)
M_UUID = TypeVar("M_UUID", bound=UUIDModel)
