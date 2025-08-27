
from __future__ import annotations
from typing import TYPE_CHECKING

from core.system import ISystem
from components.position_component import PositionComponent
from components.velocity_component import VelocityComponent

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

class MovementSystem(ISystem):
    """
    Moves all entities with a velocity.
    """

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """
        Updates the position of all entities with a velocity.
        """
        for entity in entity_manager.get_entities_with_components(PositionComponent, VelocityComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            vel = entity_manager.get_component(entity.id, VelocityComponent)

            pos.x += vel.dx * delta_time
            pos.y += vel.dy * delta_time
