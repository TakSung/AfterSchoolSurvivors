
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
import math

from core.system import ISystem
from components.position_component import PositionComponent
from components.sprite_component import SpriteComponent
from components.player_component import PlayerComponent
from components.hitbox_component import HitboxComponent
from components.health_component import HealthComponent

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

class RenderSystem(ISystem):
    """
    Renders all entities with a sprite and position.
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

    def _draw_hp_bar(self, pos: PositionComponent, sprite: SpriteComponent, health: HealthComponent) -> None:
        """Draws the HP bar above the entity's sprite."""
        hp_bar_width = sprite.rect.width
        hp_bar_height = 5
        hp_bar_x = pos.x - hp_bar_width / 2
        hp_bar_y = pos.y - sprite.rect.height / 2 - hp_bar_height - 2

        fill_ratio = health.current / health.maximum
        fill_width = hp_bar_width * fill_ratio

        # Draw background
        pygame.draw.rect(self.screen, (255, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        # Draw HP fill
        pygame.draw.rect(self.screen, (0, 255, 0), (hp_bar_x, hp_bar_y, fill_width, hp_bar_height))
        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 255), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 1)

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """
        Renders all entities and the player's UI.
        """
        self.screen.fill((0, 0, 0)) # Black background

        # Draw all entities
        for entity in entity_manager.get_entities_with_components(PositionComponent, SpriteComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            sprite = entity_manager.get_component(entity.id, SpriteComponent)

            sprite.rect.center = (pos.x, pos.y)
            self.screen.blit(sprite.surface, sprite.rect)

        # Draw HP bars
        for entity in entity_manager.get_entities_with_components(PositionComponent, SpriteComponent, HealthComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            sprite = entity_manager.get_component(entity.id, SpriteComponent)
            health = entity_manager.get_component(entity.id, HealthComponent)
            self._draw_hp_bar(pos, sprite, health)

        # Draw hitboxes for visual debugging or weapon animation
        for entity in entity_manager.get_entities_with_components(HitboxComponent, PositionComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            hitbox = entity_manager.get_component(entity.id, HitboxComponent)

            if hitbox.visual_type == 'baseball_bat':
                # Animate the bat swing
                progress = hitbox.timer / hitbox.duration
                start_angle_deg = hitbox.angle - hitbox.height / 2
                end_angle_deg = hitbox.angle + hitbox.height / 2
                current_angle_deg = start_angle_deg + (end_angle_deg - start_angle_deg) * progress

                # Create a bat surface
                bat_length = hitbox.width
                bat_width = 20
                bat_surface = pygame.Surface((bat_length, bat_width), pygame.SRCALPHA)
                bat_surface.fill((139, 69, 19)) # Brown color for the bat

                # Rotate and position the bat
                rotated_bat = pygame.transform.rotate(bat_surface, -current_angle_deg)
                
                # Offset the bat from the player center to make it swing
                offset_radius = bat_length / 2
                offset_angle_rad = math.radians(current_angle_deg)
                offset_x = offset_radius * math.cos(offset_angle_rad)
                offset_y = offset_radius * math.sin(offset_angle_rad)

                bat_rect = rotated_bat.get_rect(center=(pos.x + offset_x, pos.y + offset_y))
                self.screen.blit(rotated_bat, bat_rect)
            else:
                # Fallback to drawing a simple arc for other hitboxes
                arc_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
                arc_rect = pygame.Rect(pos.x - hitbox.width, pos.y - hitbox.width, hitbox.width * 2, hitbox.width * 2)
                start_angle = math.radians(hitbox.angle - hitbox.height / 2)
                end_angle = math.radians(hitbox.angle + hitbox.height / 2)
                pygame.draw.arc(arc_surface, (255, 255, 255, 100), arc_rect, -end_angle, -start_angle, 5)
                self.screen.blit(arc_surface, (0, 0))

        # Draw Player UI (XP Bar and Level)
        player_entities = entity_manager.get_entities_with_components(PlayerComponent)
        if player_entities:
            player_entity = player_entities[0]
            player_comp = entity_manager.get_component(player_entity.id, PlayerComponent)

            # XP Bar
            xp_bar_width = self.screen.get_width() - 40
            xp_bar_height = 20
            xp_bar_x = 20
            xp_bar_y = self.screen.get_height() - 30

            fill_ratio = player_comp.experience / player_comp.experience_to_next_level
            fill_width = xp_bar_width * fill_ratio

            # Draw background
            pygame.draw.rect(self.screen, (100, 100, 100), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
            # Draw XP fill
            pygame.draw.rect(self.screen, (150, 100, 255), (xp_bar_x, xp_bar_y, fill_width, xp_bar_height))
            # Draw border
            pygame.draw.rect(self.screen, (255, 255, 255), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 2)

            # Level Text
            level_text = self.font.render(f"Level: {player_comp.level}", True, (255, 255, 255))
            self.screen.blit(level_text, (25, self.screen.get_height() - 60))


        pygame.display.flip()
