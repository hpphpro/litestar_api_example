from typing import TYPE_CHECKING

from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alchemy.entity.associated import UserRole
from src.database.alchemy.entity.base import Entity, mixins

if TYPE_CHECKING:
    from src.database.alchemy.entity.role import Role


class User(mixins.WithUUIDMixin, mixins.WithTimeMixin, Entity):
    login: Mapped[str] = mapped_column(String(length=55))
    password: Mapped[str]
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        back_populates="users",
        primaryjoin="User.id == UserRole.user_id",
        secondaryjoin="UserRole.role_id == Role.id",
        secondary=UserRole.__table__,
    )

    __table_args__ = (
        Index(
            "idx_lower_login",
            func.lower(login),
            unique=True,
        ),
    )
