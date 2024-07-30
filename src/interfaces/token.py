from datetime import timedelta
from typing import Any, Protocol, TypeVar, runtime_checkable

EncodeT = TypeVar("EncodeT", covariant=True)
DecodeT = TypeVar("DecodeT", covariant=True)


@runtime_checkable
class JWT(Protocol[EncodeT, DecodeT]):
    def encode(
        self,
        sub: str,
        typ: str | None = None,
        key: str | None = None,
        algorithm: str | None = None,
        exp_delta: timedelta | None = None,
        **kw: Any,
    ) -> EncodeT: ...
    def decode(
        self, encoded: str, key: str | None = None, algorithm: str | None = None
    ) -> DecodeT: ...
