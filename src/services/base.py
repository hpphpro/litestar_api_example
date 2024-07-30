from src.database import DatabaseManager


class Service:
    __slots__ = ("_manager",)

    def __init__(self, manager: DatabaseManager) -> None:
        self._manager = manager
