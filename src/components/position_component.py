from dataclasses import dataclass
from core.component import Component

@dataclass
class PositionComponent(Component):
    x: float
    y: float
