from src.interfaces.manager import AbstractTransactionManager


class Service:
    __slots__ = ("_manager",)

    def __init__(self, manager: AbstractTransactionManager) -> None:
        self._manager = manager

    @property
    def manager(self) -> AbstractTransactionManager:
        return self._manager
