from __future__ import annotations

from typing import Any, Callable

import msgspec
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.database.alchemy.adapters import (
    AlchemyAsyncConnectionAdapter,
    AlchemyAsyncSessionConnectionAdapter,
)
from src.interfaces.connection import AbstractAsyncConnection


def create_sa_engine(url: str, **kw: Any) -> AsyncEngine:
    return create_async_engine(
        url,
        json_serializer=msgspec.json.encode,
        json_deserializer=msgspec.json.decode,
        **kw,
    )


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
