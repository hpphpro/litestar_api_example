from __future__ import annotations

import uuid
from typing import Annotated, Final

from msgspec import UNSET, Meta, UnsetType, field

import src.common.dto.role as role
from src.common.dto.base import DTO as DTO

MIN_PASSWORD_LENGTH: Final[int] = 8
MAX_PASSWORD_LENGTH: Final[int] = 32


class User(DTO):
    id: uuid.UUID
    login: str
    roles: list[role.Role] = field(default_factory=list)


class UserCreate(DTO):
    login: str
    password: Annotated[
        str,
        Meta(
            min_length=MIN_PASSWORD_LENGTH,
            max_length=MAX_PASSWORD_LENGTH,
            description=f"Password between `{MIN_PASSWORD_LENGTH}` and `{MAX_PASSWORD_LENGTH}` characters long",
        ),
    ]


class UserUpdate(DTO):
    login: str | UnsetType = UNSET
    password: (
        Annotated[
            str,
            Meta(
                min_length=MIN_PASSWORD_LENGTH,
                max_length=MAX_PASSWORD_LENGTH,
                description=f"Password between `{MIN_PASSWORD_LENGTH}` and `{MAX_PASSWORD_LENGTH}` characters long",
            ),
        ]
        | UnsetType
    ) = UNSET


class Fingerprint(DTO):
    fingerprint: str


class UserLogin(Fingerprint):
    login: str
    password: str
