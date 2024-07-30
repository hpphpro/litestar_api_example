from typing import get_args

from sqlalchemy.ext.asyncio import AsyncEngine

from src.database.alchemy.queries import role
from src.database.alchemy.types.role import RoleType


async def create_default_roles_if_not_exists(engine: AsyncEngine) -> None:
    roles = get_args(RoleType)

    async with engine.execution_options(isolation_level="SERIALIZABLE").begin() as conn:
        for name in roles:
            exist = role.Get(name=name)
            if await exist(conn):  # type: ignore
                continue
            create = role.Create(name=name)
            await create(conn)  # type: ignore

        await conn.commit()
