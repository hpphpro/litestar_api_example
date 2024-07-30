import math
from datetime import datetime, timezone
from typing import Annotated

from litestar import (
    Controller,
    MediaType,
    Request,
    Response,
    post,
    status_codes,
)
from litestar.datastructures.cookie import Cookie
from litestar.datastructures.state import State
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Body

from src.api.common.docs import TooManyRequests, UnAuthorized
from src.api.v1.commands import CommandMediatorProtocol
from src.common import dto


class AuthController(Controller):
    path = "/auth"
    tags = ["auth"]

    @post(
        "/login",
        status_code=status_codes.HTTP_200_OK,
        responses={
            status_codes.HTTP_401_UNAUTHORIZED: ResponseSpec(
                UnAuthorized,
                description="Unauthorized",
                examples=[
                    Example(summary="Unauthorized", value={"message": "Unauthorized"})
                ],
            ),
            status_codes.HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
                TooManyRequests,
                description="Too many requests",
                examples=[
                    Example(
                        summary="Too many requests",
                        value={"message": "Too many requests"},
                    )
                ],
            ),
        },
        exclude_from_auth=True,
        middleware=[RateLimitConfig(rate_limit=("minute", 5)).middleware],
    )
    async def login_endpoint(
        self,
        data: Annotated[
            dto.UserLogin,
            Body(
                title="User login",
            ),
        ],
        mediator: CommandMediatorProtocol,
    ) -> Response[dto.Token]:
        expire, refresh, access = await mediator.send(data)

        return Response(
            content=access,
            media_type=MediaType.JSON,
            status_code=status_codes.HTTP_200_OK,
            cookies=[
                Cookie(
                    "refresh",
                    value=refresh.token,
                    httponly=True,
                    max_age=math.ceil(
                        (expire - datetime.now(timezone.utc)).total_seconds()
                    ),
                    secure=True,
                    samesite="lax",
                )
            ],
        )

    @post(
        "/refresh",
        status_code=status_codes.HTTP_200_OK,
        security=[{"BearerToken": []}],
        responses={
            status_codes.HTTP_401_UNAUTHORIZED: ResponseSpec(
                UnAuthorized,
                description="Unauthorized",
                examples=[
                    Example(summary="Unauthorized", value={"message": "Unauthorized"})
                ],
            )
        },
        exclude_from_auth=True,
    )
    async def refresh_endpoint(
        self,
        data: Annotated[
            dto.Fingerprint,
            Body(
                title="Token refresh",
            ),
        ],
        request: Request[None, None, State],
        mediator: CommandMediatorProtocol,
    ) -> Response[dto.Token]:
        token = request.cookies.get("refresh", "")
        expire, refresh, access = await mediator.send(data, token=token)

        return Response(
            content=access,
            media_type=MediaType.JSON,
            status_code=status_codes.HTTP_200_OK,
            cookies=[
                Cookie(
                    "refresh",
                    value=refresh.token,
                    httponly=True,
                    max_age=math.ceil(
                        (expire - datetime.now(timezone.utc)).total_seconds()
                    ),
                    secure=True,
                    samesite="lax",
                )
            ],
        )

    @post(
        "/logout",
        status_code=status_codes.HTTP_200_OK,
        security=[{"BearerToken": []}],
        responses={
            status_codes.HTTP_401_UNAUTHORIZED: ResponseSpec(
                UnAuthorized,
                description="Unauthorized",
                examples=[
                    Example(summary="Unauthorized", value={"message": "Unauthorized"})
                ],
            )
        },
        exclude_from_auth=True,
    )
    async def logout_endpoint(
        self, request: Request[None, None, State], mediator: CommandMediatorProtocol
    ) -> Response[dto.Status]:
        token = dto.Token(token=request.cookies.get("refresh", ""))
        return Response(
            await mediator.send(token),
            cookies=[Cookie("refresh", max_age=0, expires=0)],
        )
