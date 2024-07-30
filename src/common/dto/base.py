from __future__ import annotations

from typing import Any, TypeVar, cast

import msgspec

DTOType = TypeVar("DTOType", bound="DTO")


class DTO(msgspec.Struct):
    @classmethod
    def from_mapping(
        cls: type[DTOType],
        value: Any,
        *,
        strict: bool = False,
        from_attributes: bool = False,
        **kw: Any,
    ) -> DTOType:
        return cast(
            DTOType,
            msgspec.convert(
                value, cls, strict=strict, from_attributes=from_attributes, **kw
            ),
        )

    def to_dict(
        self, exclude_none: bool = False, exclude: set[str] | None = None, **kw: Any
    ) -> dict[str, Any]:
        result = msgspec.to_builtins(self, **kw)
        if exclude_none:
            return {k: v for k, v in result.items() if v is not None}
        if exclude:
            return {k: v for k, v in result.items() if k not in exclude}

        return cast(dict[str, Any], result)
