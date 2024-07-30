from typing import Any

from litestar.connection import ASGIConnection
from litestar.datastructures.state import State
from litestar.handlers.base import BaseRouteHandler

from src.common import dto
from src.common.exceptions import ForbiddenError


class Permission:
    __slots__ = (
        "id_key",
        "same_user",
        "roles",
        "permissions",
    )

    def __init__(
        self,
        *roles: Any,
        identifier_key: str = "id",
        same_user: bool = True,
        **permissions: Any,
    ) -> None:
        self.id_key = identifier_key
        self.same_user = same_user
        self.roles = roles
        self.permissions = permissions

    async def __call__(
        self,
        conn: ASGIConnection[BaseRouteHandler, dto.User, dto.TokenPayload, State],
        _: BaseRouteHandler,
    ) -> None:
        if self.roles:
            valid_roles = self.ensure_valid_roles(conn.user)
            if valid_roles:
                if not self.permissions:
                    return
                valid_permissions = self.ensure_valid_permissions(conn.user)
                if valid_permissions:
                    return

        if self.same_user:
            key = conn.path_params.get(self.id_key, "")
            if str(key) == str(getattr(conn.user, self.id_key, "")):
                return

        raise ForbiddenError("You have no permissions to do that")

    def ensure_valid_roles(self, user: dto.User) -> bool:
        actual_roles = [role.name for role in user.roles]
        return any(role in actual_roles for role in self.roles)

    def ensure_valid_permissions(self, user: dto.User) -> bool:
        roles_set = set(self.roles)
        permissions = {role: set(perms) for role, perms in self.permissions.items()}

        for role in user.roles:
            if role.name in roles_set and role.name in permissions:
                if permissions[role.name] - set(role.permissions):
                    return False

        return True
