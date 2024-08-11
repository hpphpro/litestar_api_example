from litestar import Litestar
from litestar.di import Provide

from src.api.v1.commands.setup import setup_command_mediator
from src.common.helpers import singleton
from src.core.logger import log
from src.core.settings import Settings
from src.database.alchemy.connection import (
    create_sa_engine,
    create_sa_session_factory,
    create_session_factory,
)
from src.database.manager import create_db_manager_factory
from src.services.cache.redis import get_redis
from src.services.security.argon2 import get_argon2_hasher
from src.services.security.jwt import JWTImpl


def setup_common_dependencies(app: Litestar, settings: Settings) -> None:
    log.info("Setup dependencies")
    engine = create_sa_engine(
        settings.db.url,
        pool_size=settings.db.connection_pool_size,
        max_overflow=settings.db.connection_max_overflow,
        pool_pre_ping=settings.db.connection_pool_pre_ping,
    )
    redis = get_redis(settings.redis)
    app.state.engine = engine
    app.state.redis = redis
    session_factory = create_session_factory(create_sa_session_factory(engine))
    manager_factory = create_db_manager_factory(session_factory)
    hasher = get_argon2_hasher()
    jwt = JWTImpl(settings.cipher)
    mediator = setup_command_mediator(
        manager=manager_factory,
        hasher=hasher,
        jwt=jwt,
        cache=redis,
    )

    app.dependencies["mediator"] = Provide(
        singleton(mediator), use_cache=True, sync_to_thread=False
    )
    app.dependencies["jwt"] = Provide(
        singleton(jwt), use_cache=True, sync_to_thread=False
    )
    app.dependencies["cache"] = Provide(
        singleton(redis), use_cache=True, sync_to_thread=False
    )
