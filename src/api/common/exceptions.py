from functools import partial
from typing import Any, Callable

from litestar import MediaType, Request, Response, Router
from litestar import status_codes as status
from litestar.types import ExceptionHandlersMap

import src.common.exceptions as exc
from src.core.logger import log

JsonResponse = Response[dict[str, Any]]
BasicRequest = Request[Any, Any, Any]


def get_current_common_exception_handlers() -> ExceptionHandlersMap:
    return {
        exc.UnAuthorizedError: error_handler(status.HTTP_401_UNAUTHORIZED),
        exc.NotFoundError: error_handler(status.HTTP_404_NOT_FOUND),
        exc.ConflictError: error_handler(status.HTTP_409_CONFLICT),
        exc.ServiceNotImplementedError: error_handler(status.HTTP_501_NOT_IMPLEMENTED),
        exc.ServiceUnavailableError: error_handler(status.HTTP_503_SERVICE_UNAVAILABLE),
        exc.BadRequestError: error_handler(status.HTTP_400_BAD_REQUEST),
        exc.ForbiddenError: error_handler(status.HTTP_403_FORBIDDEN),
        exc.TooManyRequestsError: error_handler(status.HTTP_429_TOO_MANY_REQUESTS),
        exc.AppException: error_handler(status.HTTP_500_INTERNAL_SERVER_ERROR),
    }


def setup_common_exception_handlers(router: Router) -> None:
    router.exception_handlers |= get_current_common_exception_handlers()


def error_handler(
    status_code: int,
) -> Callable[..., JsonResponse]:
    return partial(app_error_handler, status_code=status_code)


def app_error_handler(
    request: BasicRequest, exc: exc.AppException, status_code: int
) -> JsonResponse:
    return handle_error(
        request,
        exc=exc,
        status_code=status_code,
    )


def handle_error(
    _: BasicRequest,
    exc: exc.AppException,
    status_code: int,
) -> JsonResponse:
    log.error(f"Handle error: {type(exc).__name__}")
    error_data = exc.as_dict()

    return JsonResponse(
        **error_data, status_code=status_code, media_type=MediaType.JSON
    )
