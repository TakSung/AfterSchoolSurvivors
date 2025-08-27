
from __future__ import annotations
import math
from typing import TYPE_CHECKING

from core.system import ISystem
from components.position_component import PositionComponent
from components.health_component import HealthComponent
from components.player_component import PlayerComponent
from components.enemy_component import EnemyComponent
from components.attack_component import AttackComponent
from components.enums import EntityStatus

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

# AI-DEV : For performance, this should be data-driven from components.
# For now, we assume a fixed size for all entities.
ENTITY_SIZE = 32

class CollisionSystem(ISystem):
    """
    Handles collision detection and resolution between entities.
    """

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """
        Checks for and handles collisions between:
        - Player and Enemies
        - Player's weapons and Enemies
        """
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, PositionComponent, HealthComponent)
        enemy_entities = entity_manager.get_entities_with_components(EnemyComponent, PositionComponent, HealthComponent)
        weapon_entities = entity_manager.get_entities_with_components(AttackComponent, PositionComponent)

        if not player_entities:
            return

        player_entity = player_entities[0]
        player_pos = entity_manager.get_component(player_entity.id, PositionComponent)
        player_health = entity_manager.get_component(player_entity.id, HealthComponent)

        # 1. Player and Enemy collisions
        if player_health.status != EntityStatus.INVULNERABLE:
            for enemy_entity in enemy_entities:
                enemy_pos = entity_manager.get_component(enemy_entity.id, PositionComponent)
                if self._check_collision(player_pos, enemy_pos):
                    # For now, simple damage. In the future, this could be based on enemy stats.
                    player_health.current -= 10
                    if player_health.current <= 0:
                        player_health.status = EntityStatus.DEAD
                    # TODO: Add invulnerability timer
                    print(f"Player collided with enemy {enemy_entity.id}! Player health: {player_health.current}")


        # 2. Weapon and Enemy collisions
        enemies_to_destroy = set()
        for weapon_entity in weapon_entities:
            weapon_pos = entity_manager.get_component(weapon_entity.id, PositionComponent)
            weapon_attack = entity_manager.get_component(weapon_entity.id, AttackComponent)
            
            # Skip if weapon has no position or attack component
            if not weapon_pos or not weapon_attack:
                continue

            for enemy_entity in enemy_entities:
                # Skip if enemy is already marked for destruction
                if enemy_entity.id in enemies_to_destroy:
                    continue

                enemy_pos = entity_manager.get_component(enemy_entity.id, PositionComponent)
                enemy_health = entity_manager.get_component(enemy_entity.id, HealthComponent)

                # Skip if enemy has no position or health, or is already dead
                if not enemy_pos or not enemy_health or enemy_health.status == EntityStatus.DEAD:
                    continue

                if self._check_collision(weapon_pos, enemy_pos):
                    enemy_health.current -= weapon_attack.damage
                    print(f"Enemy {enemy_entity.id} hit by weapon! Enemy health: {enemy_health.current}")
                    
                    if enemy_health.current <= 0:
                        enemies_to_destroy.add(enemy_entity.id)
                        print(f"Enemy {enemy_entity.id} marked for destruction.")

                    # Destroy weapon on hit
                    entity_manager.destroy_entity(weapon_entity.id)
                    
                    # An enemy can only be hit by one weapon per frame, so we break
                    # after destroying the weapon.
                    break
        
        # Destroy all enemies marked for destruction
        for enemy_id in enemies_to_destroy:
            print(f"Destroying enemy {enemy_id}")
            entity_manager.destroy_entity(enemy_id)

    def _check_collision(self, pos1: PositionComponent, pos2: PositionComponent) -> bool:
        """
        Checks for collision between two entities based on their positions and a fixed size.
        Using simple Axis-Aligned Bounding Box (AABB) collision detection.
        """
        # AI-DEV: This is a simplified collision detection.
        # It assumes all entities are squares of ENTITY_SIZE.
        # This should be replaced with a more robust system that uses entity-specific bounding boxes.
        half_size = ENTITY_SIZE / 2
        rect1_left = pos1.x - half_size
        rect1_right = pos1.x + half_size
        rect1_top = pos1.y - half_size
        rect1_bottom = pos1.y + half_size

        rect2_left = pos2.x - half_size
        rect2_right = pos2.x + half_size
        rect2_top = pos2.y - half_size
        rect2_bottom = pos2.y + half_size

        if (rect1_right >= rect2_left and
            rect1_left <= rect2_right and
            rect1_bottom >= rect2_top and
            rect1_top <= rect2_bottom):
            return True
        return False
