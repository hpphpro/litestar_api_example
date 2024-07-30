from collections import deque
from functools import lru_cache
from typing import (
    Any,
    List,
    Optional,
    ParamSpec,
    Tuple,
    Type,
    TypeVar,
)

from sqlalchemy import Select, select
from sqlalchemy.orm import Load, RelationshipProperty, joinedload, subqueryload

from src.database.alchemy.entity import MODELS_RELATIONSHIPS_NODE
from src.database.alchemy.entity.base import Entity, EntityType

P = ParamSpec("P")
R = TypeVar("R")


def _bfs_search(
    start: Type[Entity],
    end: str,
) -> List[RelationshipProperty[Type[Entity]]]:
    queue = deque([[start]])
    checked = set()

    while queue:
        path = queue.popleft()
        current_node = path[-1]

        if current_node in checked:
            continue
        checked.add(current_node)

        current_relations = MODELS_RELATIONSHIPS_NODE.get(current_node, [])

        for relation in current_relations:
            new_path: List[Any] = list(path)
            new_path.append(relation)

            if relation.key == end:
                return [
                    rel for rel in new_path if isinstance(rel, RelationshipProperty)
                ]

            queue.append(new_path + [relation.mapper.class_])

    return []


def _construct_loads(
    relationships: List[RelationshipProperty[Type[Entity]]],
) -> Optional[Load]:
    if not relationships:
        return None

    load: Optional[Load] = None
    for relationship in relationships:
        loader = joinedload if not relationship.uselist else subqueryload

        if load is None:
            load = loader(relationship)  # type: ignore
        else:
            load = getattr(load, loader.__name__)(relationship)

    return load


@lru_cache
def select_with_relationships(
    *_should_load: str,
    model: Type[EntityType],
    query: Optional[Select[Tuple[Type[EntityType]]]] = None,
) -> Select[Any]:
    if query is None:
        query = select(model)

    options = []
    to_load = set(_should_load)
    while to_load:
        # we dont care if path is the same, alchemy will remove it by itself
        result = _bfs_search(model, to_load.pop())
        if not result:
            continue
        construct = _construct_loads(result)
        if construct:
            options += [construct]

    if options:
        return query.options(*options)

    return query
