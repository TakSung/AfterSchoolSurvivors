from dataclasses import dataclass
from core.component import Component

@dataclass
class TrapComponent(Component):
    """A component for trap entities."""
    duration: float = 3.0
    speed_reduction: float = 0.2
