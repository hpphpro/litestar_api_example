import uuid
from typing import Any

from src.common import dto
from src.interfaces.command import Command
from src.interfaces.manager import AbstractTransactionManager
from src.services.user import UserService


class DeleteUserById(dto.DTO):
    user_id: uuid.UUID


class DeleteUserByIdCommand(Command[DeleteUserById, dto.User]):
    __slots__ = ("_manager",)

    def __init__(self, manager: AbstractTransactionManager) -> None:
        self._manager = manager

    async def execute(self, query: DeleteUserById, /, **kwargs: Any) -> dto.User:
        async with self._manager:
            await self._manager.create_transaction()

            return await UserService(self._manager).delete(id=query.user_id)
