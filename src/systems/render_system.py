
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from core.system import ISystem
from components.position_component import PositionComponent
from components.sprite_component import SpriteComponent

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

class RenderSystem(ISystem):
    """
    Renders all entities with a sprite and position.
    """
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """
        Renders all entities.
        """
        # AI-DEV: This is a simple render system. For better performance,
        # it could be optimized to only draw things that are on screen,
        # and to draw in a specific order (e.g., background, then enemies, then player).
        self.screen.fill((0, 0, 0)) # Black background

        for entity in entity_manager.get_entities_with_components(PositionComponent, SpriteComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            sprite = entity_manager.get_component(entity.id, SpriteComponent)

            sprite.rect.center = (pos.x, pos.y)
            self.screen.blit(sprite.surface, sprite.rect)

        pygame.display.flip()
