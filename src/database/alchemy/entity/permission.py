from typing import TYPE_CHECKING

from sqlalchemy import Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.alchemy.entity.associated import RolePermission
from src.database.alchemy.entity.base import Entity, mixins

if TYPE_CHECKING:
    from src.database.alchemy.entity.role import Role


class Permission(mixins.WithUUIDMixin, mixins.WithTimeMixin, Entity):
    name: Mapped[str] = mapped_column()

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        back_populates="permissions",
        secondary=RolePermission.__table__,
        primaryjoin="Permission.id == RolePermission.permission_id",
        secondaryjoin="RolePermission.role_id == Role.id",
    )

    __table_args__ = (
        Index(
            "idx_lower_permission_name",
            func.lower(name),
            unique=True,
        ),
    )
