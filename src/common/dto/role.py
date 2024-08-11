from __future__ import annotations

import uuid

from msgspec import field

import src.common.dto.permission as permission
import src.common.dto.user as user
from src.common.dto.base import DTO as DTO
from src.database.alchemy import types


class Role(DTO):
    id: uuid.UUID
    name: types.role.RoleType
    users: list[user.User] = field(default_factory=list)
    permissions: list[permission.Permission] = field(default_factory=list)


class RoleCreate(DTO):
    name: types.role.RoleType


class SetRoleToUser(DTO):
    user_id: uuid.UUID
    name: types.role.RoleType


class ChangeUserRole(DTO):
    user_id: uuid.UUID
    old_name: types.role.RoleType
    new_name: types.role.RoleType
