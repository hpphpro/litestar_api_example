from functools import wraps
from typing import Any, Awaitable, Callable, NoReturn, ParamSpec, TypeVar

from src.common.exceptions import AppException, ConflictError

P = ParamSpec("P")
R = TypeVar("R")


def _raise_error(
    error: type[AppException] | AppException,
    reason: str,
    base_message: str,
    **additional: Any,
) -> NoReturn:
    if callable(error):
        if "{reason}" in base_message:
            message = base_message.format(reason=reason)
        else:
            message = f"{base_message}: <{reason}>"

        raise error(message, **additional)

    raise error


def on_error(
    *uniques: str,
    should_raise: type[AppException] | AppException = ConflictError,
    base_message: str = "{reason} already in use",
    **additional: Any,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    def _wrapper(coro: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(coro)
        async def _inner_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                if isinstance(e, AppException):
                    raise e
                origin = str(e.args[0]) if e.args else "Unknown"
                if not uniques:
                    _raise_error(should_raise, origin, base_message, **additional)

                for uniq in set(uniques):
                    if uniq in origin:
                        _raise_error(should_raise, uniq, base_message, **additional)

                raise AppException() from e

        return _inner_wrapper

    return _wrapper


def page_to_offset(page: int | None, limit: int | None) -> int | None:
    page = page if page and page > 0 else 1
    return ((page) - 1) * limit if limit else None
