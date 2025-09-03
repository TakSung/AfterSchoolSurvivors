from dataclasses import dataclass
from core.component import Component

@dataclass
class ExperienceComponent(Component):
    amount: int
