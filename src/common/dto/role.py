from __future__ import annotations

import uuid

from msgspec import field

import src.common.dto.permission as permission
import src.common.dto.user as user
from src.common.dto.base import DTO as DTO


class Role(DTO):
    id: uuid.UUID
    name: str
    users: list[user.User] = field(default_factory=list)
    permissions: list[permission.Permission] = field(default_factory=list)


class RoleCreate(DTO):
    name: str


class SetRoleToUser(DTO):
    user_id: uuid.UUID
    name: str


class ChangeUserRole(DTO):
    user_id: uuid.UUID
    old_name: str
    new_name: str
