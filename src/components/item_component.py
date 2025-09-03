from dataclasses import dataclass, field
from core.component import Component
from .enums import ItemType

@dataclass
class ItemComponent(Component):
    item_type: ItemType
