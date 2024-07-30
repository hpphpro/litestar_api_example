from litestar import Router
from litestar.middleware.base import DefineMiddleware

from src.api.v1.middlewares.auth import JWTAuthMiddleware


def setup_middlewares(router: Router) -> None:
    router.middleware.append(
        DefineMiddleware(
            JWTAuthMiddleware,
            auth_header="Authorization",
            exclude_http_methods=["OPTIONS", "HEAD"],
        )
    )
