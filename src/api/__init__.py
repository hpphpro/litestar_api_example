from contextlib import asynccontextmanager
from typing import AsyncIterator, Literal, cast

from litestar import Litestar, Router
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.spec import Components, SecurityScheme
from litestar.types import Method

from src.api.common.exceptions import setup_common_exception_handlers
from src.api.common.middlewares import setup_common_middlewares
from src.api.dependencies import setup_common_dependencies
from src.core.logger import log
from src.core.settings import Settings


@asynccontextmanager
async def release_resources(app: Litestar) -> AsyncIterator[None]:
    try:
        yield
    finally:
        if engine := getattr(app.state, "engine", None):
            await engine.dispose()
        if redis := getattr(app.state, "redis", None):
            await redis.close()


def init_app(settings: Settings, *routers: Router) -> Litestar:
    log.info("Initialize Application")

    app = Litestar(
        [],
        path="/api",
        cors_config=CORSConfig(
            allow_origins=settings.server.cors_origins,
            allow_methods=cast(
                list[Method | Literal["*"]], settings.server.cors_methods
            ),
            allow_headers=settings.server.cors_headers,
            expose_headers=settings.server.cors_expose_headers,
            allow_credentials=True,
        )
        if settings.server.cors
        else None,
        csrf_config=(
            CSRFConfig(secret=settings.server.csrf_secret)
            if settings.server.csrf_secret
            else None
        ),
        openapi_config=(
            OpenAPIConfig(
                title=settings.server.title,
                version=settings.server.version,
                components=Components(
                    security_schemes={
                        "BearerToken": SecurityScheme(
                            type="http",
                            scheme="Bearer",
                            name="Authorization",
                            bearer_format="JWT",
                            description=None,
                        )
                    }
                ),
            )
            if settings.server.title
            else None
        ),
        debug=bool(settings.server.debug),
        lifespan=[release_resources],
    )

    setup_common_middlewares(app)
    setup_common_exception_handlers(app)
    setup_common_dependencies(app, settings)

    for router in routers:
        app.register(router)

    return app
