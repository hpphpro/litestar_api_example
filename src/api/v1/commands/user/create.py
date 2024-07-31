from typing import Any

from src.common import dto
from src.interfaces.command import Command
from src.interfaces.hasher import AbstractHasher
from src.interfaces.manager import AbstractTransactionManager
from src.services import RoleService, UserService


class CreateUserCommand(Command[dto.UserCreate, dto.User]):
    __slots__ = (
        "_manager",
        "_hasher",
        "_role_service",
        "_user_service",
    )

    def __init__(
        self, manager: AbstractTransactionManager, hasher: AbstractHasher
    ) -> None:
        self._manager = manager
        self._hasher = hasher
        self._role_service = RoleService(self._manager)
        self._user_service = UserService(self._manager)

    async def execute(self, query: dto.UserCreate, /, **kwargs: Any) -> dto.User:
        async with self._manager:
            await self._manager.create_transaction()

            user = await self._user_service.create(query, self._hasher)
            await self._role_service.set_role_to_user(
                dto.SetRoleToUser(user_id=user.id, name="USER")
            )

            return user
