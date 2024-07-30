from typing import Any, Callable, Protocol, TypeVar, runtime_checkable

KeyT = TypeVar("KeyT", contravariant=True)
RespT = TypeVar("RespT", contravariant=True)


@runtime_checkable
class Cache(Protocol[KeyT, RespT]):
    async def get_value(
        self, key: KeyT, convert_to: Any | Callable[[Any], RespT] | None = None
    ) -> RespT | Any: ...
    async def set_value(
        self, key: KeyT, value: RespT | Any, expire: int | None = None, **kw: Any
    ) -> None: ...
    async def del_keys(self, *keys: RespT) -> None: ...
    async def get_list(
        self,
        key: KeyT,
        convert_to: Any | Callable[[Any], list[RespT]] | None = None,
    ) -> list[RespT] | list[Any]: ...
    async def set_list(
        self, key: KeyT, *values: RespT | Any, expire: int | None = None, **kw: Any
    ) -> None: ...
    async def pop(
        self,
        key: KeyT,
        value: RespT | Any,
        convert_to: Any | Callable[[Any], RespT] | None = None,
        **kw: Any,
    ) -> RespT | Any | None: ...
    async def close(self) -> None: ...
