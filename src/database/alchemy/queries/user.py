import uuid
from typing import Any, Unpack, overload

from src.database.alchemy.entity import User
from src.database.alchemy.queries import base
from src.database.alchemy.types import OrderByType, user


class Create(base.Create[User]):
    __slots__ = ()

    def __init__(self, **data: Unpack[user.CreateType]) -> None:
        super().__init__(**data)


class Get(base.Get[User]):
    __slots__ = ()

    @overload
    def __init__(
        self, *_loads: user.LoadsType, lock: bool = False, id: uuid.UUID
    ) -> None: ...
    @overload
    def __init__(
        self, *_loads: user.LoadsType, lock: bool = False, login: str
    ) -> None: ...
    def __init__(self, *_loads: user.LoadsType, lock: bool = False, **kw: Any) -> None:
        super().__init__(*_loads, lock_for_update=lock, **kw)


class Update(base.Update[User]):
    __slots__ = ()

    def __init__(self, id: uuid.UUID, **data: Unpack[user.UpdateType]) -> None:
        super().__init__(id=id, **data)


class Delete(base.Delete[User]):
    __slots__ = ()

    def __init__(
        self,
        id: uuid.UUID,
    ) -> None:
        super().__init__(id=id)


class Exists(base.Exists[User]):
    __slots__ = ()

    @overload
    def __init__(self, *, id: uuid.UUID) -> None: ...
    @overload
    def __init__(self, *, login: str) -> None: ...
    def __init__(self, **kw: Any) -> None:
        super().__init__(**kw)


class GetManyByOffset(base.GetManyByOffset[User]):
    __slots__ = ()

    def __init__(
        self,
        *_loads: user.LoadsType,
        order_by: OrderByType = 'ASC',
        offset: int | None = None,
        limit: int | None = None,
    ) -> None:
        super().__init__(*_loads, order_by=order_by, offset=offset, limit=limit)
