
from __future__ import annotations
from typing import TYPE_CHECKING

from core.system import ISystem
from components.position_component import PositionComponent
from components.velocity_component import VelocityComponent
from components.player_component import PlayerComponent

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
        # Handle player debuffs first
        for player_entity in entity_manager.get_entities_with_components(PlayerComponent, VelocityComponent):
            player_comp = entity_manager.get_component(player_entity.id, PlayerComponent)
            if player_comp.slow_debuff_stacks > 0:
                player_comp.slow_debuff_timer -= delta_time
                if player_comp.slow_debuff_timer <= 0:
                    player_comp.slow_debuff_stacks = 0
                    player_comp.slow_debuff_timer = 0

        # Generic movement
        for entity in entity_manager.get_entities_with_components(PositionComponent, VelocityComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            vel = entity_manager.get_component(entity.id, VelocityComponent)
            
            final_dx = vel.dx
            final_dy = vel.dy

            if entity_manager.has_component(entity.id, PlayerComponent):
                player_comp = entity_manager.get_component(entity.id, PlayerComponent)
                if player_comp.slow_debuff_stacks > 0:
                    reduction = 0.2 * player_comp.slow_debuff_stacks
                    final_dx *= (1.0 - reduction)
                    final_dy *= (1.0 - reduction)

            pos.x += final_dx * delta_time
            pos.y += final_dy * delta_time
