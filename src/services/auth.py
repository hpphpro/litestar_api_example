import math
import uuid
from datetime import datetime, timezone
from typing import Final

from src.common import dto
from src.common.exceptions import UnAuthorizedError
from src.database.alchemy import entity, queries
from src.interfaces.cache import Cache
from src.interfaces.hasher import AbstractHasher
from src.interfaces.manager import AbstractTransactionManager
from src.interfaces.token import JWT
from src.services.base import Service

MAXIMUM_TOKENS_COUNT: Final[int] = 5


class AuthService(Service):
    __slots__ = (
        "_hasher",
        "_jwt",
        "_cache",
        "_max_tokens",
    )
    _cache_key: str = "auth:{key}"

    def __init__(
        self,
        manager: AbstractTransactionManager,
        hasher: AbstractHasher,
        jwt: JWT[tuple[datetime, dto.Token], dto.TokenPayload],
        cache: Cache[str, str],
        maximum_tokens: int = MAXIMUM_TOKENS_COUNT,
    ) -> None:
        super().__init__(manager)
        self._hasher = hasher
        self._jwt = jwt
        self._cache = cache
        self._max_tokens = maximum_tokens

    async def authenticate(self, token: str, typ: str) -> entity.User:
        payload = self._jwt.decode(token)
        user = await self.manager.send(queries.user.Get(id=uuid.UUID(payload.sub)))

        if not user or payload.type != typ:
            raise UnAuthorizedError("Unauthorized")

        return user

    async def login(self, credentials: dto.UserLogin) -> dto.InternalToken:
        user = await self.manager.send(queries.user.Get(login=credentials.login))

        if not user or not self._hasher.verify_password(
            user.password, credentials.password
        ):
            raise UnAuthorizedError("Incorrect login or password")

        user_id = user.id.hex
        cache_key = self._cache_key.format(key=user_id)

        expire, refresh = self._jwt.encode(sub=user_id, typ="refresh")
        _, access = self._jwt.encode(sub=user_id, typ="access")

        old_tokens = await self._cache.get_list(cache_key)

        if len(old_tokens) > self._max_tokens:
            await self._cache.del_keys(cache_key)

        seconds_expire = math.ceil(
            (expire - datetime.now(timezone.utc)).total_seconds()
        )
        await self._cache.set_list(
            cache_key,
            f"{credentials.fingerprint}::{refresh.token}",
            expire=seconds_expire,
        )

        return dto.InternalToken(
            access=access, refresh=refresh, refresh_expire=seconds_expire
        )

    async def refresh(
        self, fingerprint: dto.Fingerprint, token: str
    ) -> dto.InternalToken:
        user = await self.authenticate(token, "refresh")

        user_id = user.id.hex
        cache_key = self._cache_key.format(key=user_id)
        token_pairs = await self._cache.get_list(cache_key)

        verified: str | None = None

        for pair in token_pairs:
            fp, _, cached_token = pair.partition("::")
            if fp == fingerprint.fingerprint and cached_token == token:
                verified = pair
                break

        if not verified:
            await self._cache.del_keys(cache_key)
            raise UnAuthorizedError(
                "Unauthorized", detail="Current token is not valid anymore"
            )

        await self._cache.pop(cache_key, verified)

        expire, refresh = self._jwt.encode(sub=user_id, typ="refresh")
        _, access = self._jwt.encode(sub=user_id, typ="access")
        seconds_expire = math.ceil(
            (expire - datetime.now(timezone.utc)).total_seconds()
        )
        await self._cache.set_list(
            cache_key,
            f"{fingerprint}::{refresh.token}",
            expire=seconds_expire,
        )

        return dto.InternalToken(
            access=access, refresh=refresh, refresh_expire=seconds_expire
        )

    async def logout(self, token: dto.Token) -> dto.Status:
        user = await self.authenticate(token.token, "refresh")

        user_id = user.id.hex
        cache_key = self._cache_key.format(key=user_id)

        token_pairs = await self._cache.get_list(cache_key)

        for pair in token_pairs:
            _, _, cached_token = pair.partition("::")
            if cached_token == token.token:
                await self._cache.pop(cache_key, pair)
                break
        else:
            raise UnAuthorizedError("Invalid token")

        return dto.Status(success=True)
