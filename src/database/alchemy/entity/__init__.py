from types import MappingProxyType
from typing import Mapping

from sqlalchemy.orm import RelationshipProperty

from src.database.alchemy.entity.associated import RolePermission, UserRole
from src.database.alchemy.entity.base import Entity
from src.database.alchemy.entity.permission import Permission
from src.database.alchemy.entity.role import Role
from src.database.alchemy.entity.user import User

__all__ = (
    "Entity",
    "User",
    "UserRole",
    "RolePermission",
    "Role",
    "Permission",
)


def _retrieve_relationships() -> (
    dict[type[Entity], list[RelationshipProperty[type[Entity]]]]
):
    return {
        mapper.class_: list(mapper.relationships.values())
        for mapper in Entity.registry.mappers
    }


MODELS_RELATIONSHIPS_NODE: Mapping[
    type[Entity], list[RelationshipProperty[type[Entity]]]
] = MappingProxyType(_retrieve_relationships())
