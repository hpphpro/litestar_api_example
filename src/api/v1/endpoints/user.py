import uuid
from typing import Annotated, get_args

from litestar import (
    Controller,
    MediaType,
    Request,
    delete,
    get,
    patch,
    post,
    status_codes,
)
from litestar.datastructures.state import State
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi.datastructures import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Body, Parameter

from src.api.common.constants import MAX_PAGINATION_LIMIT, MIN_PAGINATION_LIMIT
from src.api.common.docs import Conflict, NotFound, TooManyRequests
from src.api.common.permission import Permission
from src.api.v1.commands import CommandMediatorProtocol
from src.api.v1.commands.user import (
    DeleteUserById,
    GetManyUsersByOffset,
    GetUserById,
    UpdateUserById,
)
from src.common import dto
from src.database.alchemy.types import OrderByType
from src.database.alchemy.types import user as user_types
from src.database.tools import page_to_offset


class UserController(Controller):
    path = "/users"
    tags = ["users"]

    @post(
        status_code=status_codes.HTTP_201_CREATED,
        media_type=MediaType.JSON,
        responses={
            status_codes.HTTP_409_CONFLICT: ResponseSpec(
                Conflict,
                description="User already exists",
                examples=[
                    Example(
                        summary="User already exists",
                        value={"message": "User already exists"},
                    )
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
    async def create_user_endpoint(
        self,
        data: Annotated[
            dto.UserCreate,
            Body(
                title="Create User",
                description="Create a new user.",
            ),
        ],
        mediator: CommandMediatorProtocol,
    ) -> dto.User:
        created_user = await mediator.send(data)

        return await mediator.send(GetUserById(id=created_user.id, s=["permissions"]))

    @get(
        status_code=status_codes.HTTP_200_OK,
        media_type=MediaType.JSON,
        security=[{"BearerToken": []}],
    )
    async def get_many_users_by_offset_endpoint(
        self,
        mediator: CommandMediatorProtocol,
        s: Annotated[
            list[user_types.LoadsType] | None,
            Parameter(
                required=False,
                default=None,
                description="Search for additional user relation",
                examples=[
                    Example(value=value, summary=value)
                    for value in get_args(user_types.LoadsType)
                ],
            ),
        ],
        page: Annotated[
            int, Parameter(default=1, required=False, title="Current page")
        ],
        limit: Annotated[
            int,
            Parameter(
                default=MIN_PAGINATION_LIMIT,
                ge=MIN_PAGINATION_LIMIT,
                le=MAX_PAGINATION_LIMIT,
                required=False,
                title="Page size limit",
            ),
        ],
        order_by: Annotated[
            OrderByType, Parameter(default="ASC", required=False, title="Item ordering")
        ],
    ) -> list[dto.User]:
        return await mediator.send(
            GetManyUsersByOffset(
                order_by=order_by,
                offset=page_to_offset(page, limit),
                limit=limit,
                s=s or [],
            )
        )

    @get(
        "/me",
        status_code=status_codes.HTTP_200_OK,
        media_type=MediaType.JSON,
        security=[{"BearerToken": []}],
        responses={
            status_codes.HTTP_404_NOT_FOUND: ResponseSpec(
                NotFound,
                description="Not found",
                examples=[
                    Example(
                        summary="User not found", value={"message": "User not found"}
                    )
                ],
            )
        },
    )
    async def get_me_endpoint(
        self,
        request: Request[dto.User, dto.TokenPayload, State],
        mediator: CommandMediatorProtocol,
    ) -> dto.User:
        return await mediator.send(GetUserById(id=request.user.id))

    @get(
        "/{id:uuid}",
        status_code=status_codes.HTTP_200_OK,
        media_type=MediaType.JSON,
        security=[{"BearerToken": []}],
        responses={
            status_codes.HTTP_404_NOT_FOUND: ResponseSpec(
                NotFound,
                description="Not found",
                examples=[
                    Example(
                        summary="User not found", value={"message": "User not found"}
                    )
                ],
            )
        },
    )
    async def get_user_by_id_endpoint(
        self,
        id: uuid.UUID,
        s: Annotated[
            list[user_types.LoadsType] | None,
            Parameter(
                required=False,
                default=None,
                description="Search for additional user relation",
                examples=[
                    Example(value=value, summary=value)
                    for value in get_args(user_types.LoadsType)
                ],
            ),
        ],
        mediator: CommandMediatorProtocol,
    ) -> dto.User:
        return await mediator.send(GetUserById(id=id, s=s or []))

    @patch(
        "/{id:uuid}",
        status_code=status_codes.HTTP_200_OK,
        media_type=MediaType.JSON,
        security=[{"BearerToken": []}],
        guards=[Permission("ADMIN", same_user=True)],
        responses={
            status_codes.HTTP_409_CONFLICT: ResponseSpec(
                Conflict,
                description="Conflict Update",
                examples=[
                    Example(
                        summary="Conflict Update",
                        value={"message": "already in use"},
                    )
                ],
            ),
            status_codes.HTTP_404_NOT_FOUND: ResponseSpec(
                NotFound,
                description="Not found",
                examples=[
                    Example(
                        summary="User not found", value={"message": "User not found"}
                    )
                ],
            ),
        },
    )
    async def update_user_by_id_endpoint(
        self,
        id: uuid.UUID,
        data: Annotated[
            dto.UserUpdate,
            Body(
                title="Update user",
            ),
        ],
        mediator: CommandMediatorProtocol,
    ) -> dto.User:
        return await mediator.send(UpdateUserById(user_id=id, data=data))

    @delete(
        "/{id:uuid}",
        status_code=status_codes.HTTP_200_OK,
        media_type=MediaType.JSON,
        security=[{"BearerToken": []}],
        guards=[Permission("ADMIN", same_user=True)],
        responses={
            status_codes.HTTP_404_NOT_FOUND: ResponseSpec(
                NotFound,
                description="Not found",
                examples=[
                    Example(
                        summary="User not found", value={"message": "User not found"}
                    )
                ],
            ),
        },
    )
    async def delete_user_by_id_endpoint(
        self,
        id: uuid.UUID,
        mediator: CommandMediatorProtocol,
    ) -> dto.User:
        return await mediator.send(DeleteUserById(user_id=id))
