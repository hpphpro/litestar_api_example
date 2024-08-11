import uuid
from typing import Any, Sequence

from msgspec import field

from src.common import dto
from src.database.alchemy.types import OrderByType
from src.database.alchemy.types.user import LoadsType
from src.interfaces.command import Command
from src.interfaces.manager import AbstractTransactionManager
from src.services.user import UserService


class GetUserById(dto.DTO):
    id: uuid.UUID
    s: Sequence[LoadsType] = field(default_factory=list)


class GetUserCommand(Command[GetUserById, dto.User]):
    __slots__ = ("_manager",)

    def __init__(self, manager: AbstractTransactionManager) -> None:
        self._manager = manager

    async def execute(self, query: GetUserById, /, **kwargs: Any) -> dto.User:
        async with self._manager:
            return await UserService(self._manager).get_one(*query.s, id=query.id)


class GetManyUsersByOffset(dto.DTO):
    order_by: OrderByType
    offset: int | None = None
    limit: int | None = None
    s: Sequence[LoadsType] = field(default_factory=list)


class GetManyUsersByOffsetCommand(
    Command[GetManyUsersByOffset, tuple[int, list[dto.User]]]
):
    __slots__ = ("_manager",)

    def __init__(self, manager: AbstractTransactionManager) -> None:
        self._manager = manager

    async def execute(
        self, query: GetManyUsersByOffset, /, **kwargs: Any
    ) -> tuple[int, list[dto.User]]:
        async with self._manager:
            return await UserService(self._manager).get_many(
                *query.s, **query.to_dict(exclude={"s"})
            )
