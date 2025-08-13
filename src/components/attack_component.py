from dataclasses import dataclass
from ..core.component import Component

@dataclass
class AttackComponent(Component):
    damage: int
    attack_speed: float
    attack_range: float
