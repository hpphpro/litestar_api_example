from typing import get_args

from sqlalchemy.ext.asyncio import AsyncConnection

from src.database.alchemy.queries import role
from src.database.alchemy.types.role import RoleType


async def create_default_roles_if_not_exists(conn: AsyncConnection) -> None:
    roles = get_args(RoleType)
    for name in roles:
        await role.Create(name=name)(conn)  # type: ignore
