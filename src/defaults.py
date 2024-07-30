import asyncio

from src.core.settings import load_settings
from src.database.alchemy.connection import create_sa_engine
from src.database.alchemy.queries.default import create_default_roles_if_not_exists


async def main() -> None:
    settings = load_settings()
    engine = create_sa_engine(settings.db.url)
    await create_default_roles_if_not_exists(engine)


if __name__ == "__main__":
    asyncio.run(main())
