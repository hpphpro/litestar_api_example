import inspect
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Set,
    Type,
    Union,
    get_args,
    get_origin,
    get_overloads,
    get_type_hints,
)

from src.api.v1.commands import CommandMediatorProtocol
from src.api.v1.commands.mediator import AwaitableProxy, CommandMediator
from src.common.dto.base import DTO
from src.interfaces.command import Command, CommandProtocol


def _predict_dependency_or_raise(
    actual: Dict[str, Any],
    expectable: Dict[str, Any],
    non_checkable: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    if not non_checkable:
        non_checkable = set()

    missing = [k for k in actual if k not in expectable and k not in non_checkable]
    if missing:
        details = ", ".join(f"`{k}`:`{actual[k]}`" for k in missing)
        raise TypeError(f"Did you forget to set dependency for {details}?")

    return {k: value if (value := expectable.get(k)) else actual[k] for k in actual}


def _retrieve_command_params(command: CommandProtocol) -> Dict[str, Any]:
    return {k: v.annotation for k, v in inspect.signature(command).parameters.items()}


def get_query_commands() -> (
    Dict[Type[DTO], Dict[str, Union[Type[CommandProtocol], Any]]]
):
    commands = {}
    overloads = get_overloads(CommandMediatorProtocol.send)
    for send in overloads:
        hints = get_type_hints(send)
        query, proxy = hints.get("query"), hints.get("return")

        if not query or not proxy:
            raise TypeError(
                "Did you forget to annotate your overloads? "
                "It should contain :query: param and :return: AwaitableProxy generic"
            )
        origin = get_origin(proxy)
        if origin is not AwaitableProxy:
            raise TypeError("Return type must be a type of AwaitableProxy.")

        args = get_args(proxy)

        if len(args) < 2:
            raise TypeError("AwaitableProxy must have two generic parameters")

        command = args[0]
        if not issubclass(command, Command):
            raise TypeError("command must inherit from base Command class.")

        commands[query] = {"command": command, **_retrieve_command_params(command)}

    return commands


def create_command_lazy(
    command: Type[CommandProtocol], **dependencies: Union[Callable[[], Any], Any]
) -> Callable[[], CommandProtocol]:
    def _create() -> CommandProtocol:
        return command(
            **{k: v() if callable(v) else v for k, v in dependencies.items()}
        )

    return _create


def setup_command_mediator(
    mediator: CommandMediator | None = None, /, **dependencies: Any
) -> CommandMediator:
    if mediator is None:
        mediator = CommandMediator()

    for query, command in get_query_commands().items():
        mediator.add(
            query=query,
            command_or_factory=create_command_lazy(
                **_predict_dependency_or_raise(command, dependencies, {"command"})
            ),
        )

    return mediator
