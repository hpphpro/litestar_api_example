from datetime import timedelta
from typing import Any, Protocol, TypeVar, runtime_checkable

KeyT = TypeVar("KeyT", contravariant=True)
RespT = TypeVar("RespT")


@runtime_checkable
class Cache(Protocol[KeyT, RespT]):
    async def get_value(
        self,
        key: KeyT,
    ) -> RespT | None: ...
    async def set_value(
        self, key: KeyT, value: Any, expire: int | timedelta | None = None, **kw: Any
    ) -> None: ...
    async def del_keys(self, *keys: KeyT) -> None: ...
    async def get_list(
        self,
        key: KeyT,
    ) -> list[RespT]: ...
    async def set_list(
        self, key: KeyT, *values: Any, expire: int | timedelta | None = None, **kw: Any
    ) -> None: ...
    async def pop(
        self,
        key: KeyT,
        value: Any,
        **kw: Any,
    ) -> bool: ...
    async def close(self) -> None: ...
