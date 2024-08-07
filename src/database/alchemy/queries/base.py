from typing import Any, Generic, Sequence

from sqlalchemy import exists, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.alchemy.entity.base import EntityType
from src.database.alchemy.types import OrderByType
from src.interfaces.command import Query, R


class BaseQuery(Query[AsyncSession, R], Generic[EntityType, R]):
    entity: type[EntityType]
    __slots__ = ("kw",)

    def __init__(self, **kw: Any) -> None:
        self.kw = kw


class Create(BaseQuery[EntityType, EntityType | None]):
    __slots__ = ()

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> EntityType | None:
        result = (
            await conn.scalars(
                insert(self.entity)
                .on_conflict_do_nothing()
                .values(**self.kw)
                .returning(self.entity)
            )
        ).first()
        return result


class GetManyByOffset(BaseQuery[EntityType, Sequence[EntityType]]):
    __slots__ = (
        "offset",
        "limit",
        "order_by",
    )

    def __init__(
        self,
        order_by: OrderByType = "ASC",
        offset: int | None = None,
        limit: int | None = None,
    ) -> None:
        self.order_by = order_by
        self.offset = offset
        self.limit = limit

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> Sequence[EntityType]:
        result = (
            await conn.scalars(
                select(self.entity)
                .limit(self.limit)
                .offset(self.offset)
                .order_by(
                    self.entity.id.asc()
                    if self.order_by.upper() == "ASC"
                    else self.entity.id.desc()
                )
            )
        ).all()

        return result


class Get(BaseQuery[EntityType, EntityType | None]):
    __slots__ = ("clauses",)

    def __init__(self, **kw: Any) -> None:
        assert kw, "At least one identifier must be provided"
        super().__init__(**kw)
        self.clauses = [getattr(self.entity, k) == v for k, v in self.kw.items()]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> EntityType | None:
        return (await conn.scalars(select(self.entity).where(*self.clauses))).first()


class Update(BaseQuery[EntityType, Sequence[EntityType]]):
    __slots__ = ("clauses",)

    def __init__(self, *, id: Any, **data: Any) -> None:
        super().__init__(**data)
        self.clauses = [self.entity.id == id]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> Sequence[EntityType]:
        result = (
            await conn.scalars(
                update(self.entity)
                .where(*self.clauses)
                .values(**self.kw)
                .returning(self.entity)
            )
        ).all()

        return result


class Delete(BaseQuery[EntityType, EntityType | None]):
    __slots__ = ("clauses",)

    def __init__(self, *, id: Any) -> None:
        self.clauses = [self.entity.id == id]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> EntityType | None:
        result = (await conn.scalars(select(self.entity).where(*self.clauses))).first()
        if result:
            await conn.delete(result)

        return result


class Exist(BaseQuery[EntityType, bool]):
    __slots__ = ("clauses",)

    def __init__(self, **kw: Any) -> None:
        assert kw, "At least one identifier must be provided"
        super().__init__(**kw)
        self.clauses = [getattr(self.entity, k) == v for k, v in self.kw.items()]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> bool:
        is_exist = await conn.scalar(
            exists(select(self.entity.id).where(*self.clauses)).select()
        )
        return bool(is_exist)
