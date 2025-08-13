from dataclasses import dataclass
from ..core.component import Component

@dataclass
class VelocityComponent(Component):
    dx: float
    dy: float
