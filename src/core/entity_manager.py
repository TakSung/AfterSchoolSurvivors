from typing import Type, TypeVar, Dict
from .entity import Entity
from .component import Component

T = TypeVar('T', bound=Component)

class EntityManager:
    def __init__(self):
        self.entities: Dict[int, Dict[Type[Component], Component]] = {}

    def create_entity(self) -> Entity:
        entity = Entity()
        self.entities[entity.id] = {}
        return entity

    def add_component(self, entity_id: int, component_instance: Component) -> None:
        component_type = type(component_instance)
        self.entities[entity_id][component_type] = component_instance

    def get_component(self, entity_id: int, component_type: Type[T]) -> T | None:
        return self.entities.get(entity_id, {}).get(component_type) # type: ignore

    def remove_component(self, entity_id: int, component_type: Type[Component]) -> None:
        if entity_id in self.entities and component_type in self.entities[entity_id]:
            del self.entities[entity_id][component_type]

    def has_component(self, entity_id: int, component_type: Type[Component]) -> bool:
        """Checks whether the specified entity has a component of the given type."""
        return component_type in self.entities.get(entity_id, {})

    def destroy_entity(self, entity_id: int) -> None:
        if entity_id in self.entities:
            del self.entities[entity_id]

    def get_entities_with_components(self, *component_types: Type[Component]) -> list[Entity]:
        """Gets all entities that have all of the specified component types."""
        entities = []
        for entity_id, components in self.entities.items():
            if all(ct in components for ct in component_types):
                entity = Entity()
                entity.id = entity_id
                entities.append(entity)
        return entities
