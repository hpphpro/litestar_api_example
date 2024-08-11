from datetime import datetime
from typing import Any

from src.common import dto
from src.interfaces.cache import Cache
from src.interfaces.command import Command
from src.interfaces.hasher import AbstractHasher
from src.interfaces.manager import AbstractTransactionManager
from src.interfaces.token import JWT
from src.services.auth import AuthService


class RefreshCommand(Command[dto.Fingerprint, dto.InternalToken]):
    __slots__ = (
        "_manager",
        "_auth",
    )

    def __init__(
        self,
        manager: AbstractTransactionManager,
        jwt: JWT[tuple[datetime, dto.Token], dto.TokenPayload],
        hasher: AbstractHasher,
        cache: Cache[str, str],
    ) -> None:
        self._manager = manager
        self._auth = AuthService(manager=manager, jwt=jwt, hasher=hasher, cache=cache)

    async def execute(
        self, query: dto.Fingerprint, /, **kwargs: Any
    ) -> dto.InternalToken:
        async with self._manager:
            return await self._auth.refresh(fingerprint=query, **kwargs)
