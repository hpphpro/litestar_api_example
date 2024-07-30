from typing import Any, Callable, Mapping, Sequence

from litestar.di import Provide
from litestar.utils import ensure_async_callable


async def find_and_resolve_simple_dependencies(
    dependencies: Mapping[str, Provide | Callable[..., Any]], names: Sequence[str]
) -> dict[str, Any]:
    resolved = {}
    for name, provide_or_callable in dependencies.items():
        if name not in names:
            continue
        if isinstance(provide_or_callable, Provide):
            assert (
                not provide_or_callable.has_async_generator_dependency
                and not provide_or_callable.has_sync_generator_dependency
            ), "Incomplete with generators"
            resolved[name] = await provide_or_callable()
        else:
            resolved[name] = await ensure_async_callable(provide_or_callable)()

    return resolved
