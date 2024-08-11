import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database.alchemy import entity, queries
from src.database.alchemy.queries.default import create_default_roles_if_not_exists
from src.interfaces.manager import AbstractTransactionManager
from tests.conftest import *  # noqa


@pytest.fixture(scope="function")
async def user(manager: AbstractTransactionManager) -> entity.User:
    user = await manager.send(queries.user.Create(login="test", password="test_test"))

    assert user, "User was not created"

    return user


@pytest.fixture(scope="function")
async def with_roles(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await create_default_roles_if_not_exists(conn)
