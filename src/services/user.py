import uuid
from typing import Any, Literal, overload

import msgspec

from src.common import dto
from src.common.exceptions import ConflictError, NotFoundError
from src.database.alchemy import queries
from src.database.alchemy.types import OrderByType, user
from src.database.tools import on_error
from src.interfaces.hasher import AbstractHasher
from src.services.base import Service


class UserService(Service):
    __slots__ = ()

    @overload
    async def get_one(
        self, *_loads: user.LoadsType, lock: bool = False, id: uuid.UUID
    ) -> dto.User: ...
    @overload
    async def get_one(
        self, *_loads: user.LoadsType, lock: bool = False, login: str
    ) -> dto.User: ...
    async def get_one(
        self, *_loads: user.LoadsType, lock: bool = False, **kw: Any
    ) -> dto.User:
        user = await self._manager.send(queries.user.Get(*_loads, lock=lock, **kw))

        if not user:
            raise NotFoundError("User not found", **kw)

        return dto.User.from_mapping(user.as_dict())

    async def get_many(
        self,
        *_loads: user.LoadsType,
        order_by: OrderByType = "ASC",
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[int, list[dto.User]]:
        total, users = await self._manager.send(
            queries.user.GetManyByOffset(
                *_loads, order_by=order_by, offset=offset, limit=limit
            )
        )

        return total, [dto.User.from_mapping(user.as_dict()) for user in users]

    @on_error("login", detail="Creation failed")
    async def create(self, data: dto.UserCreate, hasher: AbstractHasher) -> dto.User:
        data.password = hasher.hash_password(data.password)

        user = await self._manager.send(queries.user.Create(**data.to_dict()))

        if not user:
            raise ConflictError("This user already exists")

        return dto.User.from_mapping(user.as_dict())

    @on_error("login", detail="Updating failed")
    async def update(
        self, id: uuid.UUID, hasher: AbstractHasher, data: dto.UserUpdate
    ) -> dto.User:
        await self.ensure_exists(id=id)

        if data.password and data.password != msgspec.UNSET:
            data.password = hasher.hash_password(data.password)

        user = await self._manager.send(queries.user.Update(id=id, **data.to_dict()))
        if not user:
            raise NotFoundError("User to update not found", id=id)

        return dto.User.from_mapping(user.as_dict())

    @on_error(
        base_message="You cannot delete this user. {reason}",
        detail="Deleting failed",
    )
    async def delete(self, id: uuid.UUID) -> dto.User:
        await self.ensure_exists(id=id)

        user = await self._manager.send(queries.user.Delete(id=id))
        if not user:
            raise ConflictError("Couldn't delete user", id=id)

        return dto.User.from_mapping(user.as_dict())

    @overload
    async def ensure_exists(self, *, id: uuid.UUID) -> Literal[True]: ...
    @overload
    async def ensure_exists(self, *, login: str) -> Literal[True]: ...
    async def ensure_exists(self, **kw: Any) -> Literal[True]:
        exists = await self._manager.send(queries.user.Exists(**kw))
        if not exists:
            raise NotFoundError(message="User not found", **kw)

        return True
