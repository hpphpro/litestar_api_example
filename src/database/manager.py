from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any, Callable

from src.interfaces.command import Query, R
from src.interfaces.connection import (
    AbstractAsyncConnection,
    AbstractAsyncTransaction,
    IsolationLevel,
)


class TransactionManager:
    __slots__ = (
        "conn",
        "_transaction",
    )

    def __init__(self, conn: AbstractAsyncConnection) -> None:
        self.conn = conn
        self._transaction: AbstractAsyncTransaction | None = None

    async def send(self, query: Query[Any, R], /, **kw: Any) -> R:
        return await query(self.conn, **kw)

    __call__ = send

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

    async def __aenter__(self) -> TransactionManager:
        await self.conn.start()
        return self

    async def commit(self) -> None:
        await self.conn.commit()

    async def rollback(self) -> None:
        await self.conn.rollback()

    async def create_transaction(
        self, isolation_level: IsolationLevel | None = None
    ) -> None:
        if not self.conn.in_transaction() and not self.conn.closed:
            self._transaction = await self.conn.begin(isolation_level=isolation_level)

    async def close_transaction(self) -> None:
        await asyncio.shield(asyncio.create_task(self.conn.close()))


def create_db_manager_factory(
    conn_factory: Callable[..., AbstractAsyncConnection],
) -> Callable[[], TransactionManager]:
    def _create() -> TransactionManager:
        return TransactionManager(conn=conn_factory())

    return _create
