import uuid
from typing import Any

from src.common import dto
from src.interfaces.command import Command
from src.interfaces.hasher import AbstractHasher
from src.interfaces.manager import AbstractTransactionManager
from src.services.user import UserService


class UpdateUserById(dto.DTO):
    user_id: uuid.UUID
    data: dto.UserUpdate


class UpdateUserByIdCommand(Command[UpdateUserById, dto.User]):
    __slots__ = (
        "_manager",
        "_hasher",
    )

    def __init__(
        self, manager: AbstractTransactionManager, hasher: AbstractHasher
    ) -> None:
        self._manager = manager
        self._hasher = hasher

    async def execute(self, query: UpdateUserById, /, **kwargs: Any) -> dto.User:
        async with self._manager:
            await self._manager.create_transaction()

            return await UserService(self._manager).update(
                id=query.user_id, hasher=self._hasher, data=query.data
            )
