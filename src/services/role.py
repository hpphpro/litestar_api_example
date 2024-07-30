import uuid
from typing import Any, overload

from src.common import dto
from src.common.exceptions import ConflictError, NotFoundError
from src.database.alchemy import queries
from src.database.tools import on_error
from src.services.base import Service


class RoleService(Service):
    __slots__ = ()

    @on_error("name", base_message="{reason} already exists")
    async def create(self, name: str) -> dto.Role:
        role = await self._manager.send(queries.role.Create(name=name))
        if not role:
            raise ConflictError("This role already exists")

        return dto.Role.from_mapping(role.as_dict())

    @overload
    async def get_one(self, *, name: str) -> dto.Role: ...
    @overload
    async def get_one(self, *, id: uuid.UUID) -> dto.Role: ...
    async def get_one(self, **kw: Any) -> dto.Role:
        role = await self._manager.send(queries.role.Get(**kw))

        if not role:
            raise NotFoundError("Role not found", **kw)

        return dto.Role.from_mapping(role.as_dict())

    @on_error(base_message="Role was not set. {reason}", detail="Set Role Failed")
    async def set_role_to_user(self, data: dto.SetRoleToUser) -> dto.Status:
        role = await self.get_one(name=data.name)

        set_role = await self._manager.send(
            queries.role.SetToUser(user_id=data.user_id, role_id=role.id)
        )

        return dto.Status(success=bool(set_role))

    @on_error(
        base_message="Role was not changed. {reason}", detail="Change Role Failed"
    )
    async def change_user_role(self, data: dto.ChangeUserRole) -> dto.Status:
        old_role = await self.get_one(name=data.old_name)
        new_role = await self.get_one(name=data.new_name)

        changed = await self._manager.send(
            queries.role.ChangeUserRole(
                user_id=data.user_id, old_role_id=old_role.id, new_role_id=new_role.id
            )
        )

        return dto.Status(success=bool(changed))
