from __future__ import annotations
import math
from typing import TYPE_CHECKING

from ..core.system import ISystem
from ..components.position_component import PositionComponent
from ..components.velocity_component import VelocityComponent
from ..components.enemy_component import EnemyComponent
from ..components.player_component import PlayerComponent

if TYPE_CHECKING:
    from ..core.entity_manager import EntityManager


class EnemyMovementSystem(ISystem):
    """Handles the movement of enemies, guiding them towards the player."""

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """Updates the velocity of all enemies to move towards the player.

        Args:
            entity_manager: The manager for all entities and components.
            delta_time: The time elapsed since the last frame.
        """
        # AI-DEV: This system assumes the player is a single entity with
        # both a PlayerComponent and a PositionComponent.
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, PositionComponent)
        if not player_entities:
            # No player entity found, so do nothing.
            return

        player_entity = player_entities[0]
        player_pos = entity_manager.get_component(player_entity.id, PositionComponent)

        # AI-DEV: This system acts on all entities that have EnemyComponent,
        # PositionComponent, and VelocityComponent.
        for entity in entity_manager.get_entities_with_components(EnemyComponent, PositionComponent, VelocityComponent):
            enemy_pos = entity_manager.get_component(entity.id, PositionComponent)
            enemy_vel = entity_manager.get_component(entity.id, VelocityComponent)
            enemy_stats = entity_manager.get_component(entity.id, EnemyComponent)

            if not all([enemy_pos, enemy_vel, enemy_stats]):
                continue

            # Calculate direction vector from enemy to player
            dx = player_pos.x - enemy_pos.x
            dy = player_pos.y - enemy_pos.y

            # Normalize the vector
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                normalized_dx = dx / distance
                normalized_dy = dy / distance

                # Update velocity based on speed from EnemyComponent
                enemy_vel.dx = normalized_dx * enemy_stats.speed
                enemy_vel.dy = normalized_dy * enemy_stats.speed
            else:
                enemy_vel.dx = 0
                enemy_vel.dy = 0
