import asyncio
from typing import (
    Any,
    Generic,
    List,
    Protocol,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from pydantic import UUID4
from sqlmodel import func, select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, RelationshipProperty
from sqlalchemy.sql import Executable, Select

from ..models import M_UUID, M


class BaseRepositoryProtocol(Protocol[M]):
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

    async def create(self, obj: M) -> M:
        ...  # pragma: no cover

    async def update(self, obj: M) -> None:
        ...  # pragma: no cover

    async def delete(self, obj: M) -> None:
        ...  # pragma: no cover

    async def _execute_statement(self, statement: Select) -> Result:
        ...  # pragma: no cover


class UUIDRepositoryProtocol(BaseRepositoryProtocol, Protocol[M_UUID]):
    model: Type[M_UUID]

    async def get_by_id(self, id: UUID4) -> M_UUID | None:
        ...  # pragma: no cover


class BaseRepository(BaseRepositoryProtocol, Generic[M]):

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
        obj = results.first()
        if obj is None:
            return None
        return obj[0]

    async def list(self, statement: Select) -> List[M]:
        results = await self._execute_statement(statement)
        return [result[0] for result in results.unique().all()]

    async def create(self, obj: M) -> M:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: M) -> None:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)

    async def delete(self, obj: M) -> None:
        await self.session.delete(obj)
        await self.session.commit()

    async def create_many(self, objs: List[M]) -> List[M]:
        for obj in objs:
            self.session.add(obj)
        await self.session.commit()
        return objs

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
