from typing import Any, Generic, cast

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


class Create(BaseQuery[EntityType, R]):
    __slots__ = ()

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> R:
        result = (
            await conn.scalars(
                insert(self.entity)
                .on_conflict_do_nothing()
                .values(**self.kw)
                .returning(self.entity)
            )
        ).first()
        return cast(R, result if result else None)


class GetManyByOffset(BaseQuery[EntityType, R]):
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

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> R:
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

        return cast(R, result)


class Get(BaseQuery[EntityType, R]):
    __slots__ = ("clauses",)

    def __init__(self, **kw: Any) -> None:
        assert kw, "At least one identifier must be provided"
        super().__init__(**kw)
        self.clauses = [getattr(self.entity, k) == v for k, v in self.kw.items()]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> R:
        result = (await conn.scalars(select(self.entity).where(*self.clauses))).first()

        return cast(R, result if result else None)


class Update(BaseQuery[EntityType, R]):
    __slots__ = ("clauses",)

    def __init__(self, *, id: Any, **data: Any) -> None:
        super().__init__(**data)
        self.clauses = [self.entity.id == id]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> R:
        result = (
            await conn.scalars(
                update(self.entity)
                .where(*self.clauses)
                .values(**self.kw)
                .returning(self.entity)
            )
        ).all()

        return cast(R, result)


class Delete(BaseQuery[EntityType, R]):
    __slots__ = ("clauses",)

    def __init__(self, *, id: Any) -> None:
        self.clauses = [self.entity.id == id]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> R:
        result = (await conn.scalars(select(self.entity).where(*self.clauses))).first()
        if result:
            await conn.delete(result)

        return cast(R, result)


class Exist(BaseQuery[EntityType, R]):
    __slots__ = ("clauses",)

    def __init__(self, **kw: Any) -> None:
        assert kw, "At least one identifier must be provided"
        super().__init__(**kw)
        self.clauses = [getattr(self.entity, k) == v for k, v in self.kw.items()]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> R:
        is_exist = await conn.scalar(
            exists(select(self.entity.id).where(*self.clauses)).select()
        )
        return cast(R, is_exist)
