from dataclasses import dataclass, field
from core.component import Component

@dataclass
class PlayerComponent(Component):
    """
    A component for the player entity.
    """
    level: int = 1
    experience: int = 0
    experience_to_next_level: int = 100
    base_movement_speed: float = 5.0
    movement_speed: float = 5.0
