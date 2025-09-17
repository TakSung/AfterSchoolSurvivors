import pygame
import random
from core.system import ISystem
from core.entity_manager import EntityManager
from components.trap_component import TrapComponent
from components.player_component import PlayerComponent
from components.position_component import PositionComponent
from components.sprite_component import SpriteComponent

class TrapSystem(ISystem):
    def __init__(self, entity_manager: EntityManager, screen_width: int, screen_height: int):
        self.entity_manager = entity_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_timer = 0.0
        self.trap_spawn_start_time = 180.0  # 3 minutes
        self.trap_spawn_interval = 5.0  # seconds
        self.trap_spawn_timer = 0.0

    def update(self, dt: float):
        self.game_timer += dt

        if self.game_timer < self.trap_spawn_start_time:
            return

        self.trap_spawn_timer += dt
        if self.trap_spawn_timer >= self.trap_spawn_interval:
            self.spawn_trap()
            self.trap_spawn_timer = 0.0

        self.check_collisions(dt)

    def spawn_trap(self):
        trap_entity = self.entity_manager.create_entity()
        x = random.randint(0, self.screen_width)
        y = random.randint(0, self.screen_height)
        self.entity_manager.add_component(trap_entity.id, PositionComponent(x=x, y=y))
        self.entity_manager.add_component(trap_entity.id, TrapComponent())

        trap_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(trap_surface, (128, 128, 128), (5, 5), 5)
        trap_rect = trap_surface.get_rect(center=(x, y))
        self.entity_manager.add_component(trap_entity.id, SpriteComponent(surface=trap_surface, rect=trap_rect))

    def check_collisions(self, dt: float):
        player_entities = self.entity_manager.get_entities_with_components(PlayerComponent, PositionComponent)
        trap_entities = self.entity_manager.get_entities_with_components(TrapComponent, PositionComponent, SpriteComponent)

        for player_entity in player_entities:
            player_pos = self.entity_manager.get_component(player_entity.id, PositionComponent)
            player_comp = self.entity_manager.get_component(player_entity.id, PlayerComponent)
            player_rect = pygame.Rect(player_pos.x - 25, player_pos.y - 25, 50, 50) # Assuming player size is 50x50

            if player_comp.is_invulnerable:
                continue

            for trap_entity in trap_entities:
                trap_sprite = self.entity_manager.get_component(trap_entity.id, SpriteComponent)
                
                if player_rect.colliderect(trap_sprite.rect):
                    trap_comp = self.entity_manager.get_component(trap_entity.id, TrapComponent)
                    if player_comp.slow_debuff_stacks < 3:
                        player_comp.slow_debuff_stacks += 1
                    player_comp.slow_debuff_timer = trap_comp.duration
                    self.entity_manager.destroy_entity(trap_entity.id)
