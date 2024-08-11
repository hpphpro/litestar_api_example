from typing import Literal

from src.database.alchemy.types import role, user

OrderByType = Literal["ASC", "DESC"]

__all__ = ("user", "role")
