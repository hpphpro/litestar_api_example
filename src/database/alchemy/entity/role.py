from typing import TYPE_CHECKING

from sqlalchemy import Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alchemy.entity.associated import RolePermission, UserRole
from src.database.alchemy.entity.base import Entity, mixins

if TYPE_CHECKING:
    from src.database.alchemy.entity.permission import Permission
    from src.database.alchemy.entity.user import User


class Role(mixins.WithUUIDMixin, mixins.WithTimeMixin, Entity):
    name: Mapped[str] = mapped_column()
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="roles",
        secondary=UserRole.__table__,
        primaryjoin="Role.id == UserRole.role_id",
        secondaryjoin="UserRole.user_id == User.id",
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        back_populates="roles",
        secondary=RolePermission.__table__,
        primaryjoin="Role.id == RolePermission.role_id",
        secondaryjoin="RolePermission.permission_id == Permission.id",
    )
    __table_args__ = (
        Index(
            "idx_lower_role_name",
            func.lower(name),
            unique=True,
        ),
    )
