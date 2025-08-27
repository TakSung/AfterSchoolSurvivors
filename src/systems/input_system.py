
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

from core.system import ISystem
from components.player_component import PlayerComponent
from components.velocity_component import VelocityComponent
from components.position_component import PositionComponent

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

class InputSystem(ISystem):
    """
    Handles player input for movement.
    """

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """
        Updates the player's velocity based on mouse position.
        """
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, PositionComponent, VelocityComponent)

        if not player_entities:
            return

        player_entity = player_entities[0]
        player_pos = entity_manager.get_component(player_entity.id, PositionComponent)
        player_vel = entity_manager.get_component(player_entity.id, VelocityComponent)

        mouse_pos = pygame.mouse.get_pos()
        direction_x = mouse_pos[0] - player_pos.x
        direction_y = mouse_pos[1] - player_pos.y

        # Normalize
        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if distance > 1:
            player_vel.dx = (direction_x / distance) * 5 # speed
            player_vel.dy = (direction_y / distance) * 5 # speed
        else:
            player_vel.dx = 0
            player_vel.dy = 0
