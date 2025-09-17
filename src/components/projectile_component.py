from dataclasses import dataclass
from core.component import Component

@dataclass
class ProjectileComponent(Component):
    """A component for projectile entities."""
    bounces: int = 0
    pierce: int = 0
    owner_id: int = -1 # The entity that fired the projectile
