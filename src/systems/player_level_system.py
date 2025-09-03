
from __future__ import annotations
from typing import TYPE_CHECKING

from core.system import ISystem
from components.player_component import PlayerComponent

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

class PlayerLevelSystem(ISystem):
    """
    Handles player leveling based on experience.
    """

    def __init__(self):
        self.experience_to_next_level = 100

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        player_entities = entity_manager.get_entities_with_components(PlayerComponent)

        if not player_entities:
            return

        player_entity = player_entities[0]
        player_component = entity_manager.get_component(player_entity.id, PlayerComponent)

        if player_component.experience >= self.experience_to_next_level:
            player_component.level += 1
            player_component.experience -= self.experience_to_next_level
            self.experience_to_next_level = int(self.experience_to_next_level * 1.5) # Increase exp needed for next level
            print(f"Player leveled up to level {player_component.level}!")
            print(f"Next level at {self.experience_to_next_level} EXP.")
