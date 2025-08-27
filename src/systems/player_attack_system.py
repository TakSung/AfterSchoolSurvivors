
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
import math

from core.system import ISystem
from core.entity_manager import EntityManager
from ..components.player_component import PlayerComponent
from ..components.position_component import PositionComponent
from ..components.attack_component import AttackComponent
from ..components.velocity_component import VelocityComponent
from ..components.sprite_component import SpriteComponent

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

class PlayerAttackSystem(ISystem):
    """
    Handles the player's attacks.
    """
    def __init__(self):
        self.attack_speed = 4.0  # Attacks per second
        self.last_attack_time = 0

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """
        Creates projectiles when the player attacks.
        """
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, PositionComponent)
        if not player_entities:
            return

        player_entity = player_entities[0]
        player_pos = entity_manager.get_component(player_entity.id, PositionComponent)

        now = pygame.time.get_ticks()
        attack_cooldown = 1000 / self.attack_speed  # Cooldown in milliseconds
        if now - self.last_attack_time > attack_cooldown:
            self.last_attack_time = now
            self._create_projectile(entity_manager, player_pos)

    def _create_projectile(self, entity_manager: EntityManager, player_pos: PositionComponent):
        """Creates a new projectile entity.
        """
        projectile_entity = entity_manager.create_entity()

        # Position
        entity_manager.add_component(projectile_entity.id, PositionComponent(x=player_pos.x, y=player_pos.y))

        # Velocity
        mouse_pos = pygame.mouse.get_pos()
        direction_x = mouse_pos[0] - player_pos.x
        direction_y = mouse_pos[1] - player_pos.y
        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if distance > 0:
            vel_x = (direction_x / distance) * 10
            vel_y = (direction_y / distance) * 10
        else:
            vel_x, vel_y = 10, 0
        entity_manager.add_component(projectile_entity.id, VelocityComponent(dx=vel_x, dy=vel_y))

        # Attack
        entity_manager.add_component(projectile_entity.id, AttackComponent(damage=25, attack_speed=0, attack_range=0))

        # Sprite
        projectile_surface = pygame.Surface((10, 5), pygame.SRCALPHA)
        projectile_surface.fill((255, 255, 0)) # Yellow
        projectile_rect = projectile_surface.get_rect(center=(player_pos.x, player_pos.y))
        entity_manager.add_component(projectile_entity.id, SpriteComponent(surface=projectile_surface, rect=projectile_rect))

        print(f"Player fired projectile {projectile_entity.id}")
