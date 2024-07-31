import abc
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
R = TypeVar("R")


@runtime_checkable
class CommandProtocol(Protocol):
    def __init__(self, **dependencies: Any) -> None: ...
    async def __call__(self, query: Any, /, **kwargs: Any) -> Any: ...
    async def execute(self, query: Any, /, **kwargs: Any) -> Any: ...


class Command(CommandProtocol, Generic[T, R]):
    __slots__ = ()

    async def __call__(self, query: T, /, **kwargs: Any) -> R:
        return await self.execute(query, **kwargs)

    @abc.abstractmethod
    async def execute(self, query: T, /, **kwargs: Any) -> R:
        raise NotImplementedError


Query = Command[T, R]
