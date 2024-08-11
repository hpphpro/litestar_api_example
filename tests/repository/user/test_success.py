from typing import get_args

from src.database.alchemy import entity, queries, types
from src.interfaces.manager import AbstractTransactionManager
from tests.conftest import *  # noqa
from tests.repository.conftest import *  # noqa


async def test_create_success(manager: AbstractTransactionManager) -> None:
    user = await manager.send(queries.user.Create(login="name", password="test"))

    assert user, "User was not created"

    user2 = await manager.send(queries.user.Create(login="name2", password="test"))

    assert user2, "user was not created"


async def test_get_one_success(
    manager: AbstractTransactionManager, user: entity.User
) -> None:
    existing_user = await manager.send(queries.user.Get(id=user.id))
    existing_with_login = await manager.send(queries.user.Get(login=user.login))

    assert all([existing_user, existing_with_login]), "User not found"


async def test_get_many_success(
    manager: AbstractTransactionManager, user: entity.User
) -> None:
    total, users = await manager.send(queries.user.GetManyByOffset())

    assert all([total, users]), "Users not found"


async def test_update_success(
    manager: AbstractTransactionManager, user: entity.User
) -> None:
    old_login = user.login
    updated = await manager.send(queries.user.Update(id=user.id, login="new_login"))

    assert updated and old_login != updated.login, "User was not updated"


async def test_delete_success(
    manager: AbstractTransactionManager, user: entity.User
) -> None:
    deleted = await manager.send(queries.user.Delete(id=user.id))

    assert deleted, "User was not deleted"


async def test_get_with_relationships_success(
    manager: AbstractTransactionManager, user: entity.User, with_roles: None
) -> None:
    role = await manager.send(queries.role.Get(name="ADMIN"))

    assert role, "Role not found"

    is_set = await manager.send(queries.role.SetToUser(user.id, role_id=role.id))

    assert is_set, "Role was not set"

    relations = get_args(types.user.LoadsType)
    existing_user = await manager.send(queries.user.Get(*relations, id=user.id))

    assert all(
        getattr(existing_user, v) for v in relations if v != "permissions"
    ), "Relations were not found"
