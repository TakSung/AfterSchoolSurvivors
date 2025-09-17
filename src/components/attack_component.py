from dataclasses import dataclass
from core.component import Component

@dataclass
class AttackComponent(Component):
    base_damage: int
    damage: int
    attack_speed: float
    attack_range: float
