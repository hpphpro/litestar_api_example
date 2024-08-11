import uuid

from sqlalchemy.exc import IntegrityError

from src.database.alchemy import queries
from src.interfaces.manager import AbstractTransactionManager
from tests.conftest import *  # noqa
from tests.conftest import handle_error
from tests.repository.conftest import *  # noqa


async def test_get_one_failed(manager: AbstractTransactionManager) -> None:
    role = await manager.send(queries.role.Get(id=uuid.uuid4()))

    assert not role, "Role found"


@handle_error(IntegrityError)
async def test_set_failed(
    manager: AbstractTransactionManager, with_roles: None
) -> None:
    role = await manager.send(queries.role.Get(name="ADMIN"))

    assert role, "Role not found"

    is_set = await manager.send(
        queries.role.SetToUser(user_id=uuid.uuid4(), role_id=role.id)
    )

    assert not is_set, "Role was set"


async def test_change_failed(
    manager: AbstractTransactionManager, with_roles: None
) -> None:
    old = await manager.send(queries.role.Get(name="ADMIN"))
    new = await manager.send(queries.role.Get(name="USER"))

    assert old and new, "Roles were not found"

    is_changed = await manager.send(
        queries.role.ChangeUserRole(
            user_id=uuid.uuid4(), old_role_id=old.id, new_role_id=new.id
        )
    )

    assert not is_changed, "Role was changed"
