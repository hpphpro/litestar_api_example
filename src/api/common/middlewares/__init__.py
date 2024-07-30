from litestar import Router
from litestar.middleware.base import MiddlewareProtocol

from src.api.common.middlewares.process_time import ProcessTimeMiddleware

__all__ = ("ProcessTimeMiddleware",)


def get_current_common_middlewares() -> tuple[type[MiddlewareProtocol], ...]:
    return (ProcessTimeMiddleware,)


def setup_common_middlewares(app: Router) -> None:
    app.middleware.extend(get_current_common_middlewares())
