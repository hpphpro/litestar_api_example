import uuid
from typing import get_args

from sqlalchemy.exc import IntegrityError

from src.database.alchemy import entity, queries, types
from src.interfaces.manager import AbstractTransactionManager
from tests.conftest import *  # noqa
from tests.conftest import handle_error
from tests.repository.conftest import *  # noqa


async def test_create_failed(manager: AbstractTransactionManager) -> None:
    user = await manager.send(queries.user.Create(login="name", password="test"))

    assert user, "User was not created"

    same_user = await manager.send(queries.user.Create(login="name", password="test"))

    assert not same_user, "Same user was created"


async def test_get_one_failed(manager: AbstractTransactionManager) -> None:
    user = await manager.send(queries.user.Get(id=uuid.uuid4()))

    assert not user, "User found"


async def test_get_many_failed(manager: AbstractTransactionManager) -> None:
    total, users = await manager.send(queries.user.GetManyByOffset())

    assert not all([total, users]), "Users found"


async def test_get_with_relationships_failed(
    manager: AbstractTransactionManager, user: entity.User
) -> None:
    relations = get_args(types.user.LoadsType)
    existing_user = await manager.send(queries.user.Get(*relations, id=user.id))

    assert not all(
        bool(getattr(existing_user, v)) for v in relations if v != "permissions"
    ), "Relations were found"


async def test_update_failed(manager: AbstractTransactionManager) -> None:
    updated = await manager.send(
        queries.user.Update(id=uuid.uuid4(), login="new_login", password="new_password")
    )

    assert not updated, "User was updated"


@handle_error(IntegrityError)
async def test_update_same_login_failed(
    manager: AbstractTransactionManager, user: entity.User
) -> None:
    new_user = await manager.send(
        queries.user.Create(login="new_login", password="new_password")
    )

    assert new_user, "User was not created"

    updated = await manager.send(queries.user.Update(id=new_user.id, login=user.login))

    assert not updated, "Update to same login success"


async def test_delete_failed(manager: AbstractTransactionManager) -> None:
    deleted = await manager.send(queries.user.Delete(id=uuid.uuid4()))

    assert not deleted, "User was deleted"
