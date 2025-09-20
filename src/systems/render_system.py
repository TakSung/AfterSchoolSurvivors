
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
import math

from core.system import ISystem
from components.position_component import PositionComponent
from components.sprite_component import SpriteComponent
from components.player_component import PlayerComponent
from components.hitbox_component import HitboxComponent

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

class RenderSystem(ISystem):
    """
    Renders all entities with a sprite and position.
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)

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

        # Draw hitboxes for visual debugging
        for entity in entity_manager.get_entities_with_components(HitboxComponent, PositionComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            hitbox = entity_manager.get_component(entity.id, HitboxComponent)

            # Create a surface for the arc since pygame.draw.arc doesn't support alpha
            arc_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            
            # Define the bounding rectangle for the arc
            arc_rect = pygame.Rect(pos.x - hitbox.width, pos.y - hitbox.width, hitbox.width * 2, hitbox.width * 2)

            # Calculate start and end angles
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
