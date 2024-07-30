from typing import Callable, TypeVar

DT = TypeVar("DT")


def singleton(value: DT) -> Callable[[], DT]:
    def _factory() -> DT:
        return value

    return _factory
