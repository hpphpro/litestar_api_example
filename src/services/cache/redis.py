from typing import Any, Callable, Final, cast, get_args

import msgspec
from redis.asyncio.client import Redis

from src.common.dto.base import DTO
from src.core.logger import log
from src.core.settings import RedisSettings
from src.interfaces.cache import Cache

ONE_MINUTE: Final[int] = 60
ONE_HOUR: Final[int] = 3600
ONE_DAY: Final[int] = 86_400
ONE_MONTH: Final[int] = 2_592_000


class UnmatchedTypeError(Exception): ...


def _str_key(key: Any) -> str:
    return str(key)


def _default_converter(v: str | Any, typ: Any) -> Any:
    if issubclass(typ, bytes):
        return v.encode()
    elif issubclass(typ, DTO):
        return msgspec.convert(msgspec.json.decode(v), typ)
    elif issubclass(typ, list):
        arg = args[0] if (args := get_args(typ)) else None
        if not arg:
            raise UnmatchedTypeError(
                "Did you forget to set a generic type to your list?"
            )
        if isinstance(v, list):
            return [_default_converter(_v, arg) for _v in v]

        return [_default_converter(v, arg)]
    elif issubclass(typ, dict):
        return msgspec.json.decode(v)
    else:
        if not isinstance(v, str):
            log.warning(
                f"Could not convert type {type(v)} to a type {typ}. Types mismatch",
                stacklevel=3,
            )

        return v


class RedisCache(Cache[str, str]):
    __slots__ = ("_redis",)

    def __init__(self, redis: Redis) -> None:  # type: ignore
        self._redis = redis

    async def get_value(
        self, key: str, convert_to: Any | Callable[[Any], str] | None = None
    ) -> str | Any:
        v = await self._redis.get(key)
        if not convert_to:
            return v

        return (
            convert_to(v) if callable(convert_to) else _default_converter(v, convert_to)
        )

    async def set_value(
        self, key: str, value: str | Any, expire: int | None = None, **kw: Any
    ) -> None:
        await self._redis.set(
            _str_key(key), self._convert_value(value), ex=expire, **kw
        )

    async def del_keys(self, *keys: str) -> None:
        await self._redis.delete(*(_str_key(key) for key in keys))

    async def set_list(
        self, key: str, *values: str | Any, expire: int | None = None, **kw: Any
    ) -> None:
        await self._redis.lpush(key, *(self._convert_value(v) for v in values))

        if expire:
            await self._redis.expire(key, expire, **kw)

    async def get_list(
        self,
        key: str,
        convert_to: list[Any] | Callable[[Any], list[str]] | None = None,
        **kw: Any,
    ) -> list[str] | list[Any]:
        start, end = kw.get("start", 0), kw.get("end", -1)

        v = await self._redis.lrange(_str_key(key), start, end)

        if not convert_to:
            return v

        return (
            convert_to(v) if callable(convert_to) else _default_converter(v, convert_to)
        )

    async def pop(
        self,
        key: str,
        value: str | Any,
        convert_to: Any | Callable[[Any], str] | None = None,
        **kw: Any,
    ) -> str | None:
        count = kw.get("count", 0)
        v = self._convert_value(value)
        result = await self._redis.lrem(_str_key(key), count, v)

        if not result:
            return None

        if not convert_to:
            return cast(str, v)

        return (
            convert_to(v) if callable(convert_to) else _default_converter(v, convert_to)
        )

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
