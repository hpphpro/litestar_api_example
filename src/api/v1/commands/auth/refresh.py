import uuid
from datetime import datetime
from typing import Any

from src.common import dto
from src.common.exceptions import UnAuthorizedError
from src.database.alchemy.queries.user import Get
from src.interfaces.cache import Cache
from src.interfaces.command import Command
from src.interfaces.manager import AbstractTransactionManager
from src.interfaces.token import JWT


class RefreshCommand(Command[dto.Fingerprint, tuple[datetime, dto.Token, dto.Token]]):
    __slots__ = (
        "_manager",
        "_jwt",
        "_cache",
    )

    def __init__(
        self,
        manager: AbstractTransactionManager,
        jwt: JWT[tuple[datetime, dto.Token], dto.TokenPayload],
        cache: Cache[str, str],
    ) -> None:
        self._manager = manager
        self._jwt = jwt
        self._cache = cache

    async def execute(
        self, query: dto.Fingerprint, /, **kwargs: Any
    ) -> tuple[datetime, dto.Token, dto.Token]:
        return await self._verify_refresh(query.fingerprint, **kwargs)

    async def _verify_refresh(
        self, fingerprint: str, token: str
    ) -> tuple[datetime, dto.Token, dto.Token]:
        async with self._manager:
            payload = self._jwt.decode(encoded=token)
            user = await self._manager(Get(id=uuid.UUID(payload.sub)))

            if not user or payload.type != "refresh":
                raise UnAuthorizedError("Unauthorized")

            user_id = user.id.hex

            token_pairs = await self._cache.get_list(user_id)
            verified: str | None = None

            for pair in token_pairs:
                fp, _, cached_token = pair.partition("::")
                if fp == fingerprint and cached_token == token:
                    verified = pair
                    break

            if not verified:
                await self._cache.del_keys(user_id)
                raise UnAuthorizedError(
                    "Unauthorized", detail="Current token is not valid anymore"
                )

            await self._cache.pop(user_id, verified)

            expire, refresh = self._jwt.encode(typ="refresh", sub=user_id)
            _, access = self._jwt.encode(typ="access", sub=user_id)

            await self._cache.set_list(str(user.id), f"{fingerprint}::{refresh.token}")

            return expire, refresh, access
