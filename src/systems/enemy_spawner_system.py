
from __future__ import annotations
import random
from typing import TYPE_CHECKING
import pygame

from core.system import ISystem
from core.entity_manager import EntityManager
from components.enemy_component import EnemyComponent
from components.position_component import PositionComponent
from components.velocity_component import VelocityComponent
from components.health_component import HealthComponent
from components.sprite_component import SpriteComponent
from components.enums import EnemyType, EntityStatus

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

# Spawn interval (seconds) managed as a module-level constant
DEFAULT_SPAWN_INTERVAL = 1.0

class EnemySpawnerSystem(ISystem):
    """
    Spawns enemies at regular intervals.
    """
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_timer = 0
        self.spawn_interval = DEFAULT_SPAWN_INTERVAL

    def update(self, entity_manager: EntityManager, delta_time: float, game_time: float) -> None:
        """
        Spawns a new enemy if the timer is up.
        """
        self.spawn_timer += delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._spawn_enemy(entity_manager, game_time)

    def _spawn_enemy(self, entity_manager: EntityManager, game_time: float):
        """Creates a new enemy entity with difficulty scaling."""
        enemy_entity = entity_manager.create_entity()
        
        # Difficulty scaling
        difficulty_factor = 1.0 + (game_time / 30.0) # Increases every 30 seconds

        # Position
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            x, y = (random.randint(0, self.screen_width), 0)
        elif edge == 'bottom':
            x, y = (random.randint(0, self.screen_width), self.screen_height)
        elif edge == 'left':
            x, y = (0, random.randint(0, self.screen_height))
        else: # right
            x, y = (self.screen_width, random.randint(0, self.screen_height))
        entity_manager.add_component(enemy_entity.id, PositionComponent(x=x, y=y))

        # Velocity
        entity_manager.add_component(enemy_entity.id, VelocityComponent(dx=0, dy=0))

        # Health (scaled)
        base_health = 100
        scaled_health = int(base_health * difficulty_factor)
        entity_manager.add_component(enemy_entity.id, HealthComponent(base_maximum=scaled_health, current=scaled_health, maximum=scaled_health, status=EntityStatus.ALIVE))

        # Enemy (scaled speed)
        base_speed = random.uniform(1.0, 3.0)
        scaled_speed = base_speed * (1 + game_time / 60.0) # Speed increases every 60 seconds
        entity_manager.add_component(enemy_entity.id, EnemyComponent(enemy_type=EnemyType.KOREAN_TEACHER, speed=scaled_speed))

        # Sprite
        enemy_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(enemy_surface, (255,0,0), (15, 15), 15)
        enemy_rect = enemy_surface.get_rect(center=(x,y))
        entity_manager.add_component(enemy_entity.id, SpriteComponent(surface=enemy_surface, rect=enemy_rect))

        print(f"Spawned enemy {enemy_entity.id} at ({x}, {y}) with health {scaled_health} and speed {scaled_speed:.2f}")
