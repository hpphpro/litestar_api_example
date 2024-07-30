from datetime import datetime
from typing import Any, Protocol, overload, runtime_checkable

from src.api.v1.commands import auth, user
from src.api.v1.commands.mediator import AwaitableProxy, CommandType
from src.common import dto
from src.interfaces.command import R, T


@runtime_checkable
class CommandMediatorProtocol(Protocol):
    @overload
    def send(
        self, query: dto.Token
    ) -> AwaitableProxy[auth.LogoutCommand, dto.Status]: ...
    @overload
    def send(
        self, query: dto.Fingerprint, *, token: str
    ) -> AwaitableProxy[auth.RefreshCommand, tuple[datetime, dto.Token, dto.Token]]: ...
    @overload
    def send(
        self, query: dto.UserLogin
    ) -> AwaitableProxy[auth.LoginCommand, tuple[datetime, dto.Token, dto.Token]]: ...
    @overload
    def send(
        self, query: user.DeleteUserById
    ) -> AwaitableProxy[user.DeleteUserByIdCommand, dto.User]: ...
    @overload
    def send(
        self, query: user.UpdateUserById
    ) -> AwaitableProxy[user.UpdateUserByIdCommand, dto.User]: ...
    @overload
    def send(
        self, query: user.GetManyUsersByOffset
    ) -> AwaitableProxy[user.GetManyUsersByOffsetCommand, list[dto.User]]: ...
    @overload
    def send(
        self, query: dto.UserCreate
    ) -> AwaitableProxy[user.CreateUserCommand, dto.User]: ...
    @overload
    def send(
        self, query: user.GetUserById
    ) -> AwaitableProxy[user.GetUserCommand, dto.User]: ...

    # dont touch this
    def send(self, query: T, **kwargs: Any) -> AwaitableProxy[CommandType, R]: ...
