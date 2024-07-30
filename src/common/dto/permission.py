from __future__ import annotations

import uuid

from msgspec import field

import src.common.dto.role as role
from src.common.dto.base import DTO as DTO


class Permission(DTO):
    id: uuid.UUID
    name: str
    roles: list[role.Role] = field(default_factory=list)
