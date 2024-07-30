import re
from typing import Any, Dict, TypeVar

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

EntityType = TypeVar("EntityType", bound="Entity")


class Entity(DeclarativeBase):
    __abstract__: bool = True
    id: Any

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    def __repr__(self) -> str:
        params = ", ".join(
            f"{attr}={value!r}"
            for attr, value in self.__dict__.items()
            if not attr.startswith("_")
        )
        return f"{type(self).__name__}({params})"

    def as_dict(self) -> Dict[str, Any]:
        return {
            attr: _convert(value)
            for attr, value in self.__dict__.items()
            if not attr.startswith("_")
        }


def _convert(v: Any) -> Any:
    if isinstance(v, Entity):
        return v.as_dict()
    elif isinstance(v, (list, tuple, set)):
        return type(v)(_convert(_v) for _v in v)

    return v
