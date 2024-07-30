from __future__ import annotations

from typing import Any, Callable, Generator, cast

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    AsyncSessionTransaction,
    AsyncTransaction,
    async_sessionmaker,
    create_async_engine,
)

from src.interfaces.connection import AbstractAsyncConnection, AbstractAsyncTransaction


class AlchemyAsyncTransactionAdapter:
    __slots__ = ("_transaction",)

    def __init__(self, transaction: AsyncTransaction) -> None:
        self._transaction = transaction

    def __await__(self) -> Generator[None, None, AbstractAsyncTransaction]:
        return cast(
            Generator[None, None, AbstractAsyncTransaction],
            self._transaction.__await__(),
        )

    def __getattr__(self, name: str) -> Any:
        return self._transaction.__getattribute__(name)

    async def __aenter__(self) -> AbstractAsyncTransaction:
        return cast(AbstractAsyncTransaction, await self._transaction.__aenter__())

    async def __aexit__(self, *args: Any) -> None:
        return await self._transaction.__aexit__(*args)

    async def commit(self) -> None:
        return await self._transaction.commit()

    async def rollback(self) -> None:
        return await self._transaction.rollback()

    @property
    def is_valid(self) -> bool:
        return self._transaction.is_valid

    @property
    def is_active(self) -> bool:
        return self._transaction.is_active


class AlchemyAsyncConnectionAdapter:
    __slots__ = ("_conn",)

    def __init__(self, conn: AsyncConnection) -> None:
        self._conn = conn

    def __await__(self) -> Generator[None, None, AbstractAsyncConnection]:
        return cast(
            Generator[None, None, AbstractAsyncConnection],
            self._conn.__await__(),
        )

    def __getattr__(self, name: str) -> Any:
        return self._conn.__getattribute__(name)

    async def __aenter__(self) -> AbstractAsyncConnection:
        return cast(AbstractAsyncConnection, await self._conn.__aenter__())

    async def __aexit__(self, *args: Any) -> None:
        return await self._conn.__aexit__(*args)

    async def start(self, **kw: Any) -> AbstractAsyncConnection:
        return cast(AbstractAsyncConnection, await self._conn.start(**kw))

    async def execute(self, *args: Any, **kw: Any) -> Any:
        return await self._conn.execute(*args, **kw)

    async def stream(self, *args: Any, **kw: Any) -> Any:
        return await self._conn.stream(*args, **kw)

    async def close(self) -> None:
        return await self._conn.close()

    async def commit(self) -> None:
        return await self._conn.commit()

    async def rollback(self) -> None:
        return await self._conn.rollback()

    def in_transaction(self) -> bool:
        return self._conn.in_transaction()

    def in_nested_transaction(self) -> bool:
        return self._conn.in_nested_transaction()

    def begin(self) -> AbstractAsyncTransaction:
        return cast(AbstractAsyncTransaction, self._conn.begin())

    def begin_nested(self) -> AbstractAsyncTransaction:
        return cast(AbstractAsyncTransaction, self._conn.begin_nested())

    @property
    def closed(self) -> bool:
        return cast(bool, self._conn.closed)


class AlchemyAsyncSessionTransactionAdapter:
    __slots__ = ("_transaction",)

    def __init__(self, transaction: AsyncSessionTransaction) -> None:
        self._transaction = transaction

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)

    def __await__(self) -> Generator[None, None, AbstractAsyncTransaction]:
        return cast(
            Generator[None, None, AbstractAsyncTransaction],
            self._transaction.__await__(),
        )

    async def __aenter__(self) -> AbstractAsyncTransaction:
        return cast(AbstractAsyncTransaction, await self._transaction.__aenter__())

    async def __aexit__(self, *args: Any) -> None:
        return await self._transaction.__aexit__(*args)

    async def commit(self) -> None:
        return await self._transaction.commit()

    async def rollback(self) -> None:
        return await self._transaction.rollback()

    @property
    def is_valid(self) -> bool:
        return self._transaction.is_active

    @property
    def is_active(self) -> bool:
        return self.is_valid


class AlchemyAsyncSessionConnectionAdapter:
    __slots__ = ("_conn",)

    def __init__(self, conn: AsyncSession) -> None:
        self._conn = conn

    def __await__(self) -> Generator[None, None, AbstractAsyncConnection]:
        return cast(
            Generator[None, None, AbstractAsyncConnection],
            self,
        )

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)

    async def __aenter__(self) -> AbstractAsyncConnection:
        return cast(AbstractAsyncConnection, await self._conn.__aenter__())

    async def __aexit__(self, *args: Any) -> None:
        return await self._conn.__aexit__(*args)

    async def start(self, **kw: Any) -> AbstractAsyncConnection:
        return cast(AbstractAsyncConnection, self)

    async def execute(self, *args: Any, **kw: Any) -> Any:
        return await self._conn.execute(*args, **kw)

    async def stream(self, *args: Any, **kw: Any) -> Any:
        return await self._conn.stream(*args, **kw)

    async def close(self) -> None:
        return await self._conn.close()

    async def commit(self) -> None:
        return await self._conn.commit()

    async def rollback(self) -> None:
        return await self._conn.rollback()

    def in_transaction(self) -> bool:
        return self._conn.in_transaction()

    def in_nested_transaction(self) -> bool:
        return self._conn.in_nested_transaction()

    def begin(self) -> AbstractAsyncTransaction:
        return cast(AbstractAsyncTransaction, self._conn.begin())

    def begin_nested(self) -> AbstractAsyncTransaction:
        return cast(AbstractAsyncTransaction, self._conn.begin_nested())

    @property
    def closed(self) -> bool:
        return not self._conn.is_active


def create_sa_engine(url: str, **kw: Any) -> AsyncEngine:
    return create_async_engine(url, **kw)


def create_sa_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


def create_connection_factory(
    engine: AsyncEngine,
) -> Callable[[], AbstractAsyncConnection]:
    def _factory() -> AbstractAsyncConnection:
        return AlchemyAsyncConnectionAdapter(engine.connect())

    return _factory


def create_session_factory(
    session_factory: async_sessionmaker[AsyncSession],
) -> Callable[[], AbstractAsyncConnection]:
    def _factory() -> AbstractAsyncConnection:
        return AlchemyAsyncSessionConnectionAdapter(session_factory())

    return _factory
