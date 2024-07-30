from __future__ import annotations

from types import TracebackType
from typing import Any, Callable

from src.interfaces.command import Query, R
from src.interfaces.connection import AbstractAsyncConnection, AbstractAsyncTransaction


class DatabaseManager:
    __slots__ = (
        "conn",
        "_transaction",
    )

    def __init__(self, conn: AbstractAsyncConnection) -> None:
        self.conn = conn
        self._transaction: AbstractAsyncTransaction | None = None

    async def send(self, query: Query[Any, R], **kw: Any) -> R:
        return await query(self.conn, **kw)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._transaction:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()

        await self.close_transaction()

    async def __aenter__(self) -> DatabaseManager:
        await self.conn.start()
        return self

    async def commit(self) -> None:
        await self.conn.commit()

    async def rollback(self) -> None:
        await self.conn.rollback()

    async def create_transaction(self) -> None:
        if not self.conn.in_transaction() and not self.conn.closed:
            self._transaction = await self.conn.begin()

    async def close_transaction(self) -> None:
        if not self.conn.closed:
            await self.conn.close()

    __call__ = send


def create_db_manager_factory(
    conn_factory: Callable[..., AbstractAsyncConnection],
) -> Callable[[], DatabaseManager]:
    def _create() -> DatabaseManager:
        return DatabaseManager(conn=conn_factory())

    return _create
