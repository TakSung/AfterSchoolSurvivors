from dataclasses import dataclass
from .enums import EntityStatus
from core.component import Component

@dataclass
class HealthComponent(Component):
    base_maximum: int
    current: int
    maximum: int
    status: EntityStatus = EntityStatus.ALIVE
