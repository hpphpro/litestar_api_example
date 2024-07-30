from typing import Any, Callable, Dict, Generator, Generic, Type, TypeVar, Union, cast

from src.interfaces.command import CommandProtocol, R, T

CommandType = TypeVar("CommandType", bound=CommandProtocol)


class AwaitableProxy(Generic[CommandType, R]):
    __slots__ = (
        "_command",
        "_kw",
    )

    def __init__(self, command: CommandType, **kw: Any) -> None:
        self._command = command
        self._kw = kw

    def __await__(self) -> Generator[None, None, R]:
        result = yield from self._command(**self._kw).__await__()
        return cast(R, result)


def _resolve_factory(
    command_or_factory: Union[Callable[[], CommandProtocol], CommandProtocol],
) -> CommandProtocol:
    if isinstance(command_or_factory, CommandProtocol):
        return command_or_factory
    return command_or_factory()


class CommandMediator:
    def __init__(self) -> None:
        self._commands: Dict[
            Type[Any], Union[Callable[[], CommandProtocol], CommandProtocol]
        ] = {}

    def add(
        self,
        query: Type[T],
        command_or_factory: Union[Callable[[], CommandProtocol], CommandProtocol],
    ) -> None:
        self._commands[query] = command_or_factory

    def send(self, query: T, **kwargs: Any) -> AwaitableProxy[CommandProtocol, R]:
        handler = _resolve_factory(self._commands[type(query)])
        return AwaitableProxy(handler, query=query, **kwargs)
