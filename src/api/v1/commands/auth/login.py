from datetime import datetime
from typing import Any

from src.api.common.constants import MAXIMUM_TOKENS_COUNT
from src.common import dto
from src.common.exceptions import UnAuthorizedError
from src.database.alchemy.queries.user import Get
from src.database.manager import DatabaseManager
from src.interfaces.cache import Cache
from src.interfaces.command import Command
from src.interfaces.hasher import AbstractHasher
from src.interfaces.token import JWT


class LoginCommand(Command[dto.UserLogin, tuple[datetime, dto.Token, dto.Token]]):
    __slots__ = (
        "_manager",
        "_jwt",
        "_hasher",
        "_cache",
    )

    def __init__(
        self,
        manager: DatabaseManager,
        jwt: JWT[tuple[datetime, dto.Token], dto.TokenPayload],
        hasher: AbstractHasher,
        cache: Cache,
    ) -> None:
        self._manager = manager
        self._jwt = jwt
        self._hasher = hasher
        self._cache = cache

    async def execute(
        self, query: dto.UserLogin, **kwargs: Any
    ) -> tuple[datetime, dto.Token, dto.Token]:
        async with self._manager:
            user = await self._manager(Get(login=query.login))

            if not user or not self._hasher.verify_password(
                user.password, query.password
            ):
                raise UnAuthorizedError("Incorrect login or password")

            user_id = user.id.hex

            expire, refresh = self._jwt.encode(typ="refresh", sub=user_id)
            _, access = self._jwt.encode(typ="access", sub=user_id)

            old_tokens = await self._cache.get_list(user_id)
            if len(old_tokens) > MAXIMUM_TOKENS_COUNT:
                await self._cache.del_keys(user_id)

            await self._cache.set_list(user_id, f"{query.fingerprint}::{refresh.token}")

            return expire, refresh, access
