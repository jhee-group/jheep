from datetime import datetime
from typing import Generic, List, TypeVar

from pydantic import UUID4
from pydantic import BaseModel as PydanticBaseModel
from pydantic.generics import GenericModel


class BaseModel(PydanticBaseModel):

    class Config:
        orm_mode = True


class UUIDModel(BaseModel):
    id: UUID4


class CreatedUpdatedAt(BaseModel):
    created_at: datetime
    updated_at: datetime


PM = TypeVar("PM", bound=BaseModel)
PM_UUID = TypeVar("PM_UUID", bound=UUIDModel)


class PaginatedResults(GenericModel, Generic[PM]):
    count: int
    results: List[PM]


PM_CREATE = TypeVar("PM_CREATE", bound=BaseModel)
PM_UPDATE = TypeVar("PM_UPDATE", bound=BaseModel)
