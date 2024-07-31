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


class LogoutCommand(Command[dto.Token, dto.Status]):
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

    async def execute(self, query: dto.Token, /, **kwargs: Any) -> dto.Status:
        return await self._invalidate_refresh(token=query)

    async def _invalidate_refresh(self, token: dto.Token) -> dto.Status:
        async with self._manager:
            payload = self._jwt.decode(encoded=token.token)
            user = await self._manager(Get(id=uuid.UUID(payload.sub)))

            if not user or payload.type != "refresh":
                raise UnAuthorizedError("Unauthorized")

            user_id = user.id.hex

            token_pairs = await self._cache.get_list(user_id)
            for pair in token_pairs:
                _, _, cached_token = pair.partition("::")
                if cached_token == token.token:
                    await self._cache.pop(user.id.hex, pair)
                    break
            else:
                raise UnAuthorizedError("Invalid token")

            return dto.Status(success=True)
