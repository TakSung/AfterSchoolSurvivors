from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from ..core.component import Component
from ..entities.item import Item

from ..core.exceptions import InventoryFullException

if TYPE_CHECKING:
    from ..components.enums import ItemType

@dataclass
class InventoryComponent(Component):
    items: list[Optional[Item]] = field(default_factory=lambda: [None] * 6)
    max_slots: int = 6

    def add_item(self, new_item: Item) -> None:
        # First, check if the same item exists to level it up
        for i, item in enumerate(self.items):
            if item and item.item_id == new_item.item_id:
                if item.can_level_up():
                    item.level_up()
                    # TODO: Create level-up effect
                    return
                # If item is at max level, do nothing and proceed to find an empty slot.

        # If not found for leveling up, or if at max level, find an empty slot for the new item
        for i, item in enumerate(self.items):
            if item is None:
                self.items[i] = new_item
                return

        raise InventoryFullException("Inventory is full and no item could be leveled up.")

    def remove_item(self, slot_index: int) -> Optional[Item]:
        if 0 <= slot_index < self.max_slots:
            item = self.items[slot_index]
            self.items[slot_index] = None
            return item
        return None

    def get_item(self, slot_index: int) -> Optional[Item]:
        if 0 <= slot_index < self.max_slots:
            return self.items[slot_index]
        return None

    @property
    def is_full(self) -> bool:
        return all(item is not None for item in self.items)

    def get_items_by_type(self, item_type: "ItemType") -> list[Item]:
        return [item for item in self.items if item and item.item_type == item_type]

    # TODO: Implement serialization/deserialization
