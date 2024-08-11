from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column


@declarative_mixin
class WithIDMixin:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
