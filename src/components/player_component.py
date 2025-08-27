from dataclasses import dataclass
from core.component import Component

@dataclass
class PlayerComponent(Component):
    """A marker component for the player entity."""
    pass
