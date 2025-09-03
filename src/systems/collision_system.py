
from __future__ import annotations
import math
from typing import TYPE_CHECKING
import pygame

from core.system import ISystem
from components.position_component import PositionComponent
from components.health_component import HealthComponent
from components.player_component import PlayerComponent
from components.enemy_component import EnemyComponent
from components.attack_component import AttackComponent
from components.item_component import ItemComponent
from components.experience_component import ExperienceComponent
from components.sprite_component import SpriteComponent
from components.enums import EntityStatus, ItemType

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

# AI-DEV : For performance, this should be data-driven from components.
# For now, we assume a fixed size for all entities.
ENTITY_SIZE = 32
EXP_ORB_SIZE = 10

class CollisionSystem(ISystem):
    """
    Handles collision detection and resolution between entities.
    """

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """
        Checks for and handles collisions between:
        - Player and Enemies
        - Player's weapons and Enemies
        - Player and Items
        """
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, PositionComponent, HealthComponent)
        enemy_entities = entity_manager.get_entities_with_components(EnemyComponent, PositionComponent, HealthComponent)
        weapon_entities = entity_manager.get_entities_with_components(AttackComponent, PositionComponent)
        item_entities = entity_manager.get_entities_with_components(ItemComponent, PositionComponent, ExperienceComponent)

        if not player_entities:
            return

        player_entity = player_entities[0]
        player_pos = entity_manager.get_component(player_entity.id, PositionComponent)
        player_health = entity_manager.get_component(player_entity.id, HealthComponent)
        player_component = entity_manager.get_component(player_entity.id, PlayerComponent)

        # 1. Player and Enemy collisions
        if player_health.status != EntityStatus.INVULNERABLE:
            for enemy_entity in enemy_entities:
                enemy_pos = entity_manager.get_component(enemy_entity.id, PositionComponent)
                if self._check_collision(player_pos, enemy_pos, ENTITY_SIZE, ENTITY_SIZE):
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

                if self._check_collision(weapon_pos, enemy_pos, ENTITY_SIZE, ENTITY_SIZE):
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
        
        # 3. Player and Item collisions
        for item_entity in item_entities:
            item_pos = entity_manager.get_component(item_entity.id, PositionComponent)
            if self._check_collision(player_pos, item_pos, ENTITY_SIZE, EXP_ORB_SIZE):
                exp_component = entity_manager.get_component(item_entity.id, ExperienceComponent)
                player_component.experience += exp_component.amount
                print(f"Player collected {exp_component.amount} EXP! Total EXP: {player_component.experience}")
                entity_manager.destroy_entity(item_entity.id)

        # Destroy all enemies marked for destruction and drop EXP
        for enemy_id in enemies_to_destroy:
            enemy_pos = entity_manager.get_component(enemy_id, PositionComponent)
            enemy_comp = entity_manager.get_component(enemy_id, EnemyComponent)
            if enemy_pos and enemy_comp:
                self._create_exp_orb(entity_manager, enemy_pos.x, enemy_pos.y, enemy_comp.enemy_type.base_experience_yield)
            print(f"Destroying enemy {enemy_id}")
            entity_manager.destroy_entity(enemy_id)

    def _create_exp_orb(self, entity_manager: EntityManager, x: float, y: float, exp_amount: int):
        orb_entity = entity_manager.create_entity()
        entity_manager.add_component(orb_entity.id, PositionComponent(x=x, y=y))
        entity_manager.add_component(orb_entity.id, ItemComponent(item_type=ItemType.EXPERIENCE_ORB))
        entity_manager.add_component(orb_entity.id, ExperienceComponent(amount=exp_amount))
        
        # Create a simple sprite for the orb
        orb_surface = pygame.Surface((EXP_ORB_SIZE, EXP_ORB_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(orb_surface, (255, 255, 0), (EXP_ORB_SIZE // 2, EXP_ORB_SIZE // 2), EXP_ORB_SIZE // 2)
        orb_rect = orb_surface.get_rect(center=(x, y))
        entity_manager.add_component(orb_entity.id, SpriteComponent(surface=orb_surface, rect=orb_rect))
        print(f"Created EXP orb with {exp_amount} EXP at ({x}, {y})")

    def _check_collision(self, pos1: PositionComponent, pos2: PositionComponent, size1: int, size2: int) -> bool:
        """
        Checks for collision between two entities based on their positions and sizes.
        Using simple Axis-Aligned Bounding Box (AABB) collision detection.
        """
        half_size1 = size1 / 2
        rect1_left = pos1.x - half_size1
        rect1_right = pos1.x + half_size1
        rect1_top = pos1.y - half_size1
        rect1_bottom = pos1.y + half_size1

        half_size2 = size2 / 2
        rect2_left = pos2.x - half_size2
        rect2_right = pos2.x + half_size2
        rect2_top = pos2.y - half_size2
        rect2_bottom = pos2.y + half_size2

        if (rect1_right >= rect2_left and
            rect1_left <= rect2_right and
            rect1_bottom >= rect2_top and
            rect1_top <= rect2_bottom):
            return True
        return False
