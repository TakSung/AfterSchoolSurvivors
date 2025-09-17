from dataclasses import dataclass
from core.component import Component

@dataclass
class HitboxComponent(Component):
    """A component for melee attack hitboxes."""
    width: float
    height: float # For arc-based hitboxes, this can be the angle
    angle: float
    duration: float # How long the hitbox lasts in seconds
    timer: float = 0.0
