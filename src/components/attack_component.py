from dataclasses import dataclass
from core.component import Component

@dataclass
class AttackComponent(Component):
    base_damage: int = 0
    damage: int = 0
    attack_speed: float = 0.0
    attack_range: float = 0.0
