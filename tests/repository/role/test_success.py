from typing import get_args

from src.database.alchemy import entity, queries, types
from src.interfaces.manager import AbstractTransactionManager
from tests.conftest import *  # noqa
from tests.repository.conftest import *  # noqa


async def test_create_success(manager: AbstractTransactionManager) -> None:
    role = await manager.send(queries.role.Create(name="USER"))

    assert role, "Role was not created"


async def test_get_one_success(
    manager: AbstractTransactionManager, with_roles: None
) -> None:
    role = await manager.send(queries.role.Get(name="ADMIN"))

    assert role, "Role was not found"


async def test_get_with_relationships(
    manager: AbstractTransactionManager, with_roles: None, user: entity.User
) -> None:
    role = await manager.send(queries.role.Get(name="ADMIN"))

    assert role, "Role not found"

    is_set = await manager.send(
        queries.role.SetToUser(user_id=user.id, role_id=role.id)
    )
    permission = await manager.send(
        queries.base.Create.with_entity(entity.Permission)(name="test")
    )
    assert permission, "Permission was not created"

    is_permission_set = await manager.send(
        queries.base.Create.with_entity(entity.RolePermission)(
            role_id=role.id, permission_id=permission.id
        )
    )

    assert is_permission_set, "Permission was not set to role"

    assert is_set, "Role was not set"

    relations = get_args(types.role.RoleLoadsType)

    role = await manager.send(queries.role.Get(*relations, id=role.id))

    assert role and all(getattr(role, v) for v in relations), "Relations were not found"


async def test_set_success(
    manager: AbstractTransactionManager, with_roles: None, user: entity.User
) -> None:
    role = await manager.send(queries.role.Get(name="ADMIN"))

    assert role, "Role not found"

    is_set = await manager.send(
        queries.role.SetToUser(user_id=user.id, role_id=role.id)
    )

    assert is_set, "Role was not set"


async def test_change_failed(
    manager: AbstractTransactionManager, with_roles: None, user: entity.User
) -> None:
    old = await manager.send(queries.role.Get(name="ADMIN"))

    assert old, "Role was not found"
    is_set = await manager.send(queries.role.SetToUser(user_id=user.id, role_id=old.id))

    assert is_set, "Role was not set"

    new = await manager.send(queries.role.Get(name="USER"))

    assert new, "Role was not found"

    is_changed = await manager.send(
        queries.role.ChangeUserRole(
            user_id=user.id, old_role_id=old.id, new_role_id=new.id
        )
    )

    assert is_changed, "Role was not changed"
