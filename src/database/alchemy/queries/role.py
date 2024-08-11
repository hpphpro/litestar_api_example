import uuid
from typing import Any, overload

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy.entity.associated import UserRole
from src.database.alchemy.entity.role import Role
from src.database.alchemy.queries import base
from src.database.alchemy.types import role


class Create(base.Create[Role]):
    __slots__ = ()

    def __init__(self, name: role.RoleType) -> None:
        super().__init__(name=name)


class Get(base.Get[Role]):
    __slots__ = ()

    @overload
    def __init__(
        self, *loads: role.RoleLoadsType, lock: bool = False, id: uuid.UUID
    ) -> None: ...
    @overload
    def __init__(
        self, *loads: role.RoleLoadsType, lock: bool = False, name: role.RoleType
    ) -> None: ...
    def __init__(
        self, *loads: role.RoleLoadsType, lock: bool = False, **kw: Any
    ) -> None:
        super().__init__(*loads, lock_for_update=lock, **kw)


class SetToUser(base.Create[UserRole]):
    __slots__ = ()

    def __init__(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        super().__init__(user_id=user_id, role_id=role_id)


class ChangeUserRole(base.BaseQuery[UserRole, int]):
    __slots__ = ()

    def __init__(
        self, user_id: uuid.UUID, old_role_id: uuid.UUID, new_role_id: uuid.UUID
    ) -> None:
        super().__init__(role_id=new_role_id)
        self.clauses = [
            self.entity.user_id == user_id,
            self.entity.role_id == old_role_id,
        ]

    async def execute(self, conn: AsyncSession, /, **kw: Any) -> int:
        result = await conn.execute(
            update(self.entity).where(*self.clauses).values(**self.kw)
        )

        return result.rowcount
