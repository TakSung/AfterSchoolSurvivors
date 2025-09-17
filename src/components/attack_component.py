from dataclasses import dataclass, field
from typing import Optional
from core.component import Component

@dataclass
class AttackComponent(Component):
    weapon_type: Optional[str] = None
    base_damage: int = 10
    damage: int = 10
    base_attack_speed: float = 1.0
    attack_speed: float = 1.0
    attack_range: float = 50.0

    # Weapon specific attributes
    projectiles: int = 1
    bounces: int = 0
    pierce: int = 0
    angle: int = 90
