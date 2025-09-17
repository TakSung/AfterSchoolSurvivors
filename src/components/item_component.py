from dataclasses import dataclass, field
from core.component import Component
from .enums import ItemID

@dataclass
class ItemComponent(Component):
    item_id: ItemID
