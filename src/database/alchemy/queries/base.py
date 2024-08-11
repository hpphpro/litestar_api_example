from typing import Any, Generic, Self, Sequence, get_args, get_origin

from sqlalchemy import ColumnExpressionArgument, Select, exists, func, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.alchemy.entity.base import Entity, EntityType
from src.database.alchemy.queries.tools import select_with_relationships
from src.database.alchemy.types import OrderByType
from src.interfaces.command import Query, R


class BaseQuery(Query[AsyncSession, R], Generic[EntityType, R]):
    __slots__ = ("kw",)
    _entity: type[EntityType]

    def __init__(self, **kw: Any) -> None:
        self.kw = kw

    @property
    def entity(self) -> type[EntityType]:
        if getattr(self, "_entity", None):
            return self._entity

        orig_bases = getattr(self, "__orig_bases__", None)

        assert orig_bases and issubclass(
            get_origin(orig_bases[0]), BaseQuery
        ), "First generic type should be a subclass of `BaseQuery`"

        sub_orig_bases = get_args(orig_bases[0])

        assert sub_orig_bases and issubclass(
            sub_orig_bases[0], Entity
        ), "Generic first type must be a subclass of `Entity`"

        self._entity = sub_orig_bases[0]

        return self._entity

    @classmethod
    def with_entity(cls, entity: type[EntityType]) -> type[Self]:
        return type(cls.__name__, (cls,), {"_entity": entity})


class Create(BaseQuery[EntityType, EntityType | None]):
    __slots__ = ()

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> EntityType | None:
        result = await conn.scalars(
            insert(self.entity)
            .on_conflict_do_nothing()
            .values(**self.kw)
            .returning(self.entity)
        )
        return result.first()


class GetManyByOffset(BaseQuery[EntityType, tuple[int, Sequence[EntityType]]]):
    __slots__ = (
        "loads",
        "offset",
        "limit",
        "order_by",
    )

    def __init__(
        self,
        *loads: str,
        order_by: OrderByType = "ASC",
        offset: int | None = None,
        limit: int | None = None,
        **kw: Any,
    ) -> None:
        self.loads = loads
        self.order_by = order_by
        self.offset = offset
        self.limit = limit
        self.clauses = [
            getattr(self.entity, k) == v for k, v in kw.items() if v is not None
        ]

    async def execute(
        self, conn: AsyncSession, /, **kw: Any
    ) -> tuple[int, Sequence[EntityType]]:
        count = (await conn.scalar(self._count_stmt())) or 0

        if count <= 0:
            return count, []

        items: Any = (await conn.scalars(self._stmt())).all()

        return count, items

    def _stmt(
        self, *additional_clauses: ColumnExpressionArgument[bool]
    ) -> Select[tuple[EntityType]]:
        return (
            select_with_relationships(*self.loads, model=self.entity)
            .limit(self.limit)
            .offset(self.offset)
            .order_by(
                self.entity.id.asc()
                if self.order_by.upper() == "ASC"
                else self.entity.id.desc()
            )
            .where(*(self.clauses + list(additional_clauses)))
        )

    def _count_stmt(
        self, *additional_clauses: ColumnExpressionArgument[bool]
    ) -> Select[tuple[int]]:
        stmt = select(func.count()).select_from(self.entity)
        return stmt.where(*(self.clauses + list(additional_clauses)))


class Get(BaseQuery[EntityType, EntityType | None]):
    __slots__ = (
        "loads",
        "clauses",
        "lock_for_update",
    )

    def __init__(self, *loads: str, lock_for_update: bool = False, **kw: Any) -> None:
        assert kw, "At least one identifier must be provided"
        super().__init__(**kw)
        self.loads = loads
        self.lock_for_update = lock_for_update
        self.clauses = [
            getattr(self.entity, k) == v for k, v in self.kw.items() if v is not None
        ]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> EntityType | None:
        stmt = select_with_relationships(*self.loads, model=self.entity)

        if self.lock_for_update:
            stmt = stmt.with_for_update()

        result = (await conn.scalars(stmt.where(*self.clauses))).first()

        return result


class Update(BaseQuery[EntityType, EntityType | None]):
    __slots__ = ("clauses",)

    def __init__(self, *, id: Any, **data: Any) -> None:
        super().__init__(**data)
        self.clauses = [self.entity.id == id]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> EntityType | None:
        result = await conn.scalars(
            update(self.entity)
            .where(*self.clauses)
            .values(**self.kw)
            .returning(self.entity)
        )

        return result.first()


class Delete(BaseQuery[EntityType, EntityType | None]):
    __slots__ = ("clauses",)

    def __init__(self, *, id: Any) -> None:
        self.clauses = [self.entity.id == id]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> EntityType | None:
        result = (await conn.scalars(select(self.entity).where(*self.clauses))).first()
        if result:
            # to cascades capability
            await conn.delete(result)

        return result


class Exists(BaseQuery[EntityType, bool]):
    __slots__ = ("clauses",)

    def __init__(self, **kw: Any) -> None:
        assert kw, "At least one identifier must be provided"
        super().__init__(**kw)
        self.clauses = [
            getattr(self.entity, k) == v for k, v in self.kw.items() if v is not None
        ]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> bool:
        is_exist = await conn.scalar(
            exists(select(self.entity.id).where(*self.clauses)).select()
        )

        return bool(is_exist)
