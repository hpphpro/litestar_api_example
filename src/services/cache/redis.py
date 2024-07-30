from typing import (
    Any,
    Final,
)

import msgspec
import redis.asyncio as aioredis

from src.common.dto.base import DTO
from src.core.settings import RedisSettings

ONE_MINUTE: Final[int] = 60
ONE_HOUR: Final[int] = 3600
ONE_DAY: Final[int] = 86_400
ONE_MONTH: Final[int] = 2_592_000


def _str_key(key: Any) -> str:
    return str(key)


class RedisCache:
    __slots__ = ("_redis",)

    def __init__(self, redis: aioredis.Redis) -> None:  # type: ignore
        self._redis = redis

    async def get_value(self, key: Any) -> Any:
        return await self._redis.get(key)

    async def set_value(
        self, key: Any, value: Any, expire: int | None = None, **kw: Any
    ) -> None:
        if isinstance(value, (DTO, dict, list)):
            serialized = msgspec.json.encode(value)
        else:
            serialized = value

        await self._redis.set(_str_key(key), serialized, ex=expire, **kw)

    async def del_keys(self, *keys: str) -> None:
        await self._redis.delete(*(_str_key(key) for key in keys))

    async def set_list(
        self, key: Any, *values: Any, expire: int | None = None, **kw: Any
    ) -> None:
        await self._redis.lpush(key, *values)

        if expire:
            await self._redis.expire(key, expire, **kw)

    async def get_list(self, key: Any, **kw: Any) -> list[str]:
        start, end = kw.get("start", 0), kw.get("end", -1)

        return await self._redis.lrange(_str_key(key), start, end)

    async def remove_from_list(self, key: Any, value: str, **kw: Any) -> Any:
        count = kw.get("count", 0)
        return await self._redis.lrem(_str_key(key), count, value)


def get_redis(settings: RedisSettings, **kw: Any) -> RedisCache:
    return RedisCache(
        aioredis.Redis(
            host=settings.host,
            port=settings.port,
            password=settings.password,
            decode_responses=True,
            **kw,
        )
    )
