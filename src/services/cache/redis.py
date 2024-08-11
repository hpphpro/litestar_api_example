from datetime import timedelta
from typing import Any, Final

import msgspec
from redis.asyncio.client import Redis

from src.common.dto.base import DTO
from src.core.settings import RedisSettings
from src.interfaces.cache import Cache

ONE_MINUTE: Final[int] = 60
FIVE_MINUTE: Final[int] = ONE_MINUTE * 5
TEN_MINUTES: Final[int] = FIVE_MINUTE * 2
ONE_HOUR: Final[int] = 3600
ONE_DAY: Final[int] = 86_400
ONE_MONTH: Final[int] = 2_592_000


class RedisCache(Cache[str, str]):
    __slots__ = ("_redis",)

    def __init__(self, redis: Redis) -> None:  # type: ignore
        self._redis = redis

    async def get_value(
        self,
        key: str,
    ) -> str | None:
        return await self._redis.get(key)

    async def set_value(
        self, key: str, value: Any, expire: int | timedelta | None = None, **kw: Any
    ) -> None:
        await self._redis.set(key, self._convert_value(value), ex=expire, **kw)

    async def del_keys(self, *keys: str) -> None:
        found_keys = [
            found for key in keys async for found in self._redis.scan_iter(key)
        ]
        if found_keys:
            await self._redis.delete(*found_keys)

    async def set_list(
        self, key: str, *values: Any, expire: int | timedelta | None = None, **kw: Any
    ) -> None:
        await self._redis.lpush(key, *(self._convert_value(v) for v in values))

        if expire:
            await self._redis.expire(key, expire, **kw)

    async def get_list(
        self,
        key: str,
        **kw: Any,
    ) -> list[str]:
        start, end = kw.pop("start", 0), kw.pop("end", -1)
        return await self._redis.lrange(key, start, end)

    async def pop(
        self,
        key: str,
        value: Any,
        **kw: Any,
    ) -> bool:
        count = kw.pop("count", 0)
        popped = await self._redis.lrem(key, count, value)

        return bool(popped)

    async def close(self) -> None:
        await self._redis.aclose(close_connection_pool=True)  # type: ignore

    def _convert_value(self, v: Any) -> Any:
        if isinstance(v, (DTO, dict, list)):
            serialized = msgspec.json.encode(v)
        else:
            serialized = v.encode("utf-8") if isinstance(v, str) else v

        return serialized


def get_redis(settings: RedisSettings, **kw: Any) -> RedisCache:
    return RedisCache(
        Redis(
            host=settings.host,
            port=settings.port,
            password=settings.password,
            decode_responses=True,
            **kw,
        )
    )
