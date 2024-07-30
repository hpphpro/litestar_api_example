from __future__ import annotations

from datetime import datetime

from src.common.dto.base import DTO as DTO


class Token(DTO):
    token: str


class TokenPayload(DTO):
    exp: datetime
    sub: str
    iat: datetime
    iss: str | None = None
    aud: str | None = None
    jti: str | None = None
    type: str | None = None
