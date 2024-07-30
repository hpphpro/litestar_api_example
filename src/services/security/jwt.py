import base64
from datetime import datetime, timedelta, timezone
from typing import (
    Any,
    Literal,
    Tuple,
    get_args,
)

import jwt

from src.common.dto import Token, TokenPayload
from src.common.exceptions import ServiceNotImplementedError, UnAuthorizedError
from src.core.logger import log
from src.core.settings import CipherSettings
from src.interfaces.token import JWT

TokenType = Literal["access", "refresh"]


class JWTImpl(JWT[tuple[datetime, Token], TokenPayload]):
    __slots__ = ("_settings",)

    def __init__(self, settings: CipherSettings) -> None:
        self._settings = settings

    def encode(
        self,
        sub: str,
        typ: str | None = None,
        key: str | None = None,
        algorithm: str | None = None,
        exp_delta: timedelta | None = None,
        **kw: Any,
    ) -> Tuple[datetime, Token]:
        if not key:
            key = base64.b64decode(self._settings.secret_key).decode()
        if not algorithm:
            algorithm = self._settings.algorithm
        now = datetime.now(timezone.utc)
        if exp_delta:
            expire = now + exp_delta
        else:
            if not typ or typ not in get_args(TokenType):
                log.warning(
                    "No or wrong type provided, defaulting to `access`", stacklevel=3
                )
                seconds_delta = self._settings.access_token_expire_seconds
            else:
                seconds_delta = (
                    self._settings.access_token_expire_seconds
                    if typ == "access"
                    else self._settings.refresh_token_expire_seconds
                )
            expire = now + timedelta(seconds=seconds_delta)

        if now >= expire:
            raise ServiceNotImplementedError("Invalid expiration delta was provided")

        to_encode = {
            "exp": expire,
            "sub": sub,
            "iat": now,
            "type": typ,
        }
        try:
            token = jwt.encode(
                to_encode | kw,
                key,
                algorithm,
            )
        except jwt.PyJWTError as e:
            raise UnAuthorizedError("Token is expired") from e

        return expire, Token(token=token)

    def decode(
        self, encoded: str, key: str | None = None, algorithm: str | None = None
    ) -> TokenPayload:
        if not key:
            key = base64.b64decode(self._settings.public_key).decode()
        if not algorithm:
            algorithm = self._settings.algorithm

        try:
            result = jwt.decode(
                encoded,
                key,
                [algorithm],
            )
        except jwt.PyJWTError as e:
            raise UnAuthorizedError("Token is invalid or expired") from e

        return TokenPayload(**result)
