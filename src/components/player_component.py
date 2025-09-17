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
    base_attack_speed: float = 1.0  # attacks per second
    attack_speed: float = 1.0

    # for basketball shoes
    is_invulnerable: bool = False
    invulnerability_timer: float = 0.0
    invulnerability_cooldown: float = 10.0
    invulnerability_duration: float = 1.0

    # for baseball bat synergy
    trigger_bat_swing: bool = False
