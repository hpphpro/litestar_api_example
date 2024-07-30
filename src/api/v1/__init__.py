from litestar import Router

from src.api.v1.endpoints import setup_controllers
from src.api.v1.middlewares import setup_middlewares
from src.core.logger import log


def get_v1_router() -> Router:
    log.info("Initialize V1 Router")
    router = Router("/v1", route_handlers=[])

    setup_controllers(router)
    setup_middlewares(router)

    return router
