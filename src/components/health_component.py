from dataclasses import dataclass
from .enums import EntityStatus
from core.component import Component

@dataclass
class HealthComponent(Component):
    current: int
    maximum: int
    status: EntityStatus = EntityStatus.ALIVE
