import asyncio
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy import func, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty
from sqlalchemy.sql import Executable, Select

from ..models import M, M_UUID
from ..schemas import PM_CREATE, PM_UPDATE


class BaseRepositoryProtocol(Protocol[M, PM_CREATE, PM_UPDATE]):
    model: Type[M]
    session: AsyncSession

    async def paginate(
        self,
        statement: Select,
        limit=10,
        skip=0,
    ) -> Tuple[List[M], int]:
        ...  # pragma: no cover

    def orderize(
        self, statement: Select, ordering: List[Tuple[List[str], bool]]
    ) -> Select:
        ...  # pragma: no cover

    async def get_one_or_none(self, statement: Select) -> M | None:
        ...  # pragma: no cover

    async def list(self, statement: Select) -> List[M]:
        ...  # pragma: no cover

    async def create(self, obj: PM_CREATE) -> M:
        ...  # pragma: no cover

    async def update(self, *, db_obj: M, obj: PM_UPDATE | Dict[str, Any]) -> None:
        ...  # pragma: no cover

    async def delete(self, db_obj: M) -> None:
        ...  # pragma: no cover

    async def _execute_statement(self, statement: Select) -> Result:
        ...  # pragma: no cover


class UUIDRepositoryProtocol(BaseRepositoryProtocol, Protocol[M_UUID]):
    model: Type[M_UUID]

    async def get_by_id(self, id: UUID4) -> M_UUID | None:
        ...  # pragma: no cover


class BaseRepository(BaseRepositoryProtocol, Generic[M, PM_CREATE, PM_UPDATE]):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def paginate(
        self,
        statement: Select,
        limit=10,
        skip=0,
    ) -> Tuple[List[M], int]:
        paginated_statement = statement.offset(skip).limit(limit)
        [count, results] = await asyncio.gather(
            self._count(statement), self._execute_statement(paginated_statement)
        )

        return [result[0] for result in results.unique().all()], count

    def orderize(
        self, statement: Select, ordering: List[Tuple[List[str], bool]]
    ) -> Select:
        for (accessors, is_desc) in ordering:
            field: InstrumentedAttribute
            # Local field
            if len(accessors) == 1:
                try:
                    field = getattr(self.model, accessors[0])
                    if not isinstance(
                        field.prop, RelationshipProperty
                    ):  # Prevent ordering by raw relation ship field -> "tenant" instead of "tenant.id"
                        statement = statement.order_by(
                            field.desc() if is_desc else field.asc()
                        )
                except AttributeError:
                    pass
            # Relationship field
            else:
                valid_field = True
                model = self.model
                for accessor in accessors:
                    try:
                        field = getattr(model, accessor)
                        if isinstance(field.prop, RelationshipProperty):
                            if field.prop.lazy != "joined":
                                statement = statement.join(field)
                            model = field.prop.entity.class_
                    except AttributeError:
                        valid_field = False
                        break
                if valid_field:
                    statement = statement.order_by(
                        field.desc() if is_desc else field.asc()
                    )
        return statement

    async def all(self) -> List[M]:
        return await self.list(select(self.model))

    async def get_one_or_none(self, statement: Select) -> M | None:
        results = await self._execute_statement(statement)
        return results.scalar()

    async def list(self, statement: Select) -> List[M]:
        results = await self._execute_statement(statement)
        return [result[0] for result in results.unique().all()]

    async def create(self, obj: PM_CREATE) -> M:
        obj_data = jsonable_encoder(obj)
        db_obj = self.model(**obj_data)  # type: ignore
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, *, db_obj: M, obj: PM_UPDATE | Dict[str, Any]) -> M:
        obj_data = jsonable_encoder(db_obj)
        upd_data = jsonable_encoder(obj)
        #if isinstance(obj, dict):
        #    upd_data = obj
        #else:
        #    upd_data = obj.dict(exclude_unset=True)
        for field in obj_data:
            if field in upd_data:
                setattr(db_obj, field, upd_data[field])
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: M) -> None:
        await self.session.delete(db_obj)
        await self.session.commit()

    async def create_many(self, objs: List[PM_CREATE]) -> List[M]:
        objs_data = [jsonable_encoder(obj) for obj in objs]
        db_objs = [self.model(**obj_data) for obj_data in objs_data]
        for db_obj in db_objs:
            self.session.add(db_obj)
        await self.session.commit()
        for db_obj in db_objs:
            await self.session.refresh(db_obj)
        return db_objs

    async def count_all(self) -> int:
        statement = select(self.model)
        return await self._count(statement)

    async def _count(self, statement: Select) -> int:
        count_statement = statement.with_only_columns(
            [func.count()], maintain_column_froms=True  # type: ignore
        ).order_by(None)
        results = await self._execute_statement(count_statement)
        return results.scalar_one()

    async def _execute_statement(self, statement: Executable) -> Result:
        return await self.session.execute(statement)


class UUIDRepositoryMixin(Generic[M_UUID]):

    async def get_by_id(
        self: UUIDRepositoryProtocol[M_UUID],
        id: UUID4,
        options: Sequence[Any] | None = None,
    ) -> M_UUID | None:
        statement = select(self.model).where(self.model.id == id)

        if options is not None:
            statement = statement.options(*options)

        return await self.get_one_or_none(statement)


REPOSITORY = TypeVar("REPOSITORY", bound=BaseRepository)


def get_repository(repository_class: Type[REPOSITORY], session: AsyncSession) -> REPOSITORY:
    return repository_class(session)
