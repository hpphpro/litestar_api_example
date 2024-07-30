import uuid
from typing import Any, Optional, Sequence

from litestar.connection import ASGIConnection
from litestar.datastructures.state import State
from litestar.handlers.base import BaseRouteHandler
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar.types import ASGIApp, Method, Scopes

from src.api.common.tools import find_and_resolve_simple_dependencies
from src.api.v1.commands import CommandMediatorProtocol
from src.api.v1.commands.user import GetUserById
from src.common import dto
from src.common.exceptions import NotFoundError, UnAuthorizedError
from src.services.security.jwt import JWTImpl


class JWTAuthMiddleware(AbstractAuthenticationMiddleware):
    __slots__ = ("auth_header",)

    def __init__(
        self,
        app: ASGIApp,
        auth_header: str = "Authorization",
        exclude: str | list[str] | None = None,
        exclude_from_auth_key: str = "exclude_from_auth",
        exclude_http_methods: Sequence[Method] | None = None,
        scopes: Optional[Scopes] = None,
    ) -> None:
        super().__init__(
            app=app,
            exclude=exclude,
            exclude_from_auth_key=exclude_from_auth_key,
            exclude_http_methods=exclude_http_methods,
            scopes=scopes,
        )
        self.auth_header = auth_header

    async def authenticate_request(
        self, connection: ASGIConnection[BaseRouteHandler, Any, Any, State]
    ) -> AuthenticationResult:
        auth_header = connection.headers.get(self.auth_header)
        if not auth_header:
            raise UnAuthorizedError("Token is missing")

        encoded_token = auth_header.partition(" ")[-1]

        return await self.authenticate_token(
            encoded_token,
            **(
                await find_and_resolve_simple_dependencies(
                    connection.app.dependencies, ("jwt", "mediator")
                )
            ),
        )

    async def authenticate_token(
        self, encoded_token: str, jwt: JWTImpl, **kw: Any
    ) -> AuthenticationResult:
        payload = jwt.decode(encoded_token)
        if not payload or payload.type != "access":
            raise UnAuthorizedError("Invalid token provided")

        user = await self.authenticate_user(sub=payload.sub, **kw)

        return AuthenticationResult(user=user, auth=payload)

    async def authenticate_user(
        self,
        sub: str,
        mediator: CommandMediatorProtocol,
    ) -> dto.User:
        try:
            user = await mediator.send(
                GetUserById(s=["permissions"], id=uuid.UUID(sub))
            )
        except NotFoundError:
            raise UnAuthorizedError("Unauthorized") from None

        return user
