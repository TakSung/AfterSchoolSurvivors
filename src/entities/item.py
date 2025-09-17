from abc import ABC, abstractmethod
from dataclasses import dataclass
from ..components.enums import ItemID, ItemType

@dataclass
class Item(ABC):
    item_id: ItemID
    name: str
    item_type: ItemType
    level: int
    max_level: int
    description: str

    def level_up(self) -> bool:
        if self.can_level_up():
            self.level += 1
            return True
        return False

    def can_level_up(self) -> bool:
        return self.level < self.max_level

    @abstractmethod
    def get_effect(self) -> dict:
        pass

    @abstractmethod
    def apply_effect(self, target) -> None:
        pass
