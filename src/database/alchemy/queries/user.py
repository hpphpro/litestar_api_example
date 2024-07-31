import uuid
from typing import Any, Sequence, Unpack, overload

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.entity import User
from src.database.alchemy.queries import base, tools
from src.database.alchemy.types import OrderByType, user


class Create(base.Create[User, User | None]):
    entity: type[User] = User
    __slots__ = ()


class Get(base.BaseQuery[User, User | None]):
    entity: type[User] = User
    __slots__ = ("_loads", "clauses")

    @overload
    def __init__(self, *_loads: user.LoadsType, id: uuid.UUID) -> None: ...
    @overload
    def __init__(self, *_loads: user.LoadsType, login: str) -> None: ...
    def __init__(self, *_loads: user.LoadsType, **kw: Any) -> None:
        assert kw, "At least one identifier must be provided"
        super().__init__(**kw)
        self._loads = _loads
        self.clauses = [getattr(self.entity, k) == v for k, v in self.kw.items()]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> User | None:
        stmt = tools.select_with_relationships(*self._loads, model=self.entity).where(
            *self.clauses
        )

        result = (await conn.scalars(stmt)).first()

        return result if result else None


class Update(base.Update[User, Sequence[User]]):
    entity: type[User] = User
    __slots__ = ()

    def __init__(self, id: uuid.UUID, **data: Unpack[user.UpdateType]) -> None:
        super().__init__(id=id, **data)


class Delete(base.Delete[User, User | None]):
    entity: type[User] = User
    __slots__ = ()

    def __init__(
        self,
        id: uuid.UUID,
    ) -> None:
        super().__init__(id=id)


class Exist(base.Exist[User, bool]):
    entity: type[User] = User
    __slots__ = ()

    @overload
    def __init__(self, *, id: uuid.UUID) -> None: ...
    @overload
    def __init__(self, *, login: str) -> None: ...
    def __init__(self, **kw: Any) -> None:
        super().__init__(**kw)


class GetManyByOffset(base.GetManyByOffset[User, Sequence[User]]):
    entity: type[User] = User
    __slots__ = ("_loads",)

    def __init__(
        self,
        *_loads: user.LoadsType,
        order_by: OrderByType,
        offset: int | None = None,
        limit: int | None = None,
    ) -> None:
        super().__init__(order_by=order_by, offset=offset, limit=limit)
        self._loads = _loads

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> Sequence[User]:
        result = (
            await conn.scalars(
                tools.select_with_relationships(*self._loads, model=self.entity)
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
