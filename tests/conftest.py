from functools import wraps
from typing import AsyncIterator, Awaitable, Callable, ParamSpec, TypeVar

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine

from src.api import init_app
from src.api.v1 import init_v1_router
from src.core.settings import DatabaseSettings, Settings, load_settings
from src.database.alchemy.connection import (
    create_sa_engine,
    create_sa_session_factory,
    create_session_factory,
)
from src.database.alchemy.entity import Entity
from src.database.manager import TransactionManager
from src.interfaces.connection import AbstractAsyncConnection
from src.interfaces.hasher import AbstractHasher
from src.interfaces.manager import AbstractTransactionManager
from src.services.security.argon2 import get_argon2_hasher

pytestmark = pytest.mark.anyio


R = TypeVar("R")
P = ParamSpec("P")


class MockDatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="MOCK_DB_",
        extra="ignore",
    )
    driver: str = "postgresql+asyncpg"
    name: str = "test"
    host: str = "postgres"
    port: int = 5439
    user: str = "test"
    password: str = "test"

    @property
    def url(self) -> str:
        if "sqlite" in self.driver:
            return f"{self.driver}://{self.name}"
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def app(settings: Settings) -> Litestar:
    return init_app(settings, init_v1_router())


@pytest.fixture(scope="session")
async def client(app: Litestar) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def mock_settings() -> MockDatabaseSettings:
    return MockDatabaseSettings()


@pytest.fixture(scope="session")
def settings(mock_settings: MockDatabaseSettings) -> Settings:
    return load_settings(db=DatabaseSettings(**mock_settings.model_dump()))


@pytest.fixture(scope="function", name="engine")
async def connection_engine(
    settings: Settings,
) -> AsyncIterator[AsyncEngine]:
    engine = create_sa_engine(settings.db.url)
    async with engine.begin() as conn:
        await conn.run_sync(Entity.metadata.drop_all)
        await conn.run_sync(Entity.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Entity.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
def connection_factory(engine: AsyncEngine) -> Callable[[], AbstractAsyncConnection]:
    return create_session_factory(create_sa_session_factory(engine))


@pytest.fixture(scope="function")
async def manager(
    connection_factory: Callable[[], AbstractAsyncConnection],
) -> AsyncIterator[AbstractTransactionManager]:
    async with TransactionManager(connection_factory()) as manager:
        yield manager


@pytest.fixture(scope="session")
def argon() -> AbstractHasher:
    return get_argon2_hasher()

# the same like pytest.raises() function
def handle_error(
    *skip: type[BaseException],
) -> Callable[
    [Callable[P, Awaitable[R | None]]],
    Callable[P, Awaitable[R | None]],
]:
    def _wrapper(
        func: Callable[P, Awaitable[R | None]],
    ) -> Callable[P, Awaitable[R | None]]:
        @wraps(func)
        async def _inner_wrapper(*args: P.args, **kw: P.kwargs) -> R | None:
            try:
                return await func(*args, **kw)
            except Exception as e:
                if skip and isinstance(e, skip):
                    return None

                raise

        return _inner_wrapper

    return _wrapper
