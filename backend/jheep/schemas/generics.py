from datetime import datetime
from typing import Generic, List, TypeVar

from pydantic import UUID4
from pydantic import BaseModel as PydanticBaseModel
from pydantic.generics import GenericModel


class BaseModel(PydanticBaseModel):

    class Config:
        orm_mode = True


PM = TypeVar("PM", bound=BaseModel)


class UUIDModel(BaseModel):
    id: UUID4


class CreatedUpdatedAt(BaseModel):
    created_at: datetime
    updated_at: datetime


class PaginatedResults(GenericModel, Generic[PM]):
    count: int
    results: List[PM]
