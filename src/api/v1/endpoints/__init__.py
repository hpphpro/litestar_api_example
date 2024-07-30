from litestar import Router

from src.api.v1.endpoints.auth import AuthController
from src.api.v1.endpoints.healthcheck import healthcheck_endpoint
from src.api.v1.endpoints.user import UserController

__all__ = (
    "UserController",
    "healthcheck_endpoint",
)


def setup_controllers(app: Router) -> None:
    app.register(healthcheck_endpoint)
    app.register(AuthController)
    app.register(UserController)
