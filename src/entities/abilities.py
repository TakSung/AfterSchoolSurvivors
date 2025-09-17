from dataclasses import dataclass, field
from .item import Item
from ..components.enums import ItemID, ItemType

@dataclass
class AbilityItem(Item):
    item_type: ItemType = field(default=ItemType.ABILITY, init=False)

@dataclass
class SoccerShoes(AbilityItem):
    item_id: ItemID = field(default=ItemID.SOCCER_SHOES, init=False)
    name: str = field(default="축구화", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="이동 속도가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        # Lv.1: 10%, Lv.2-5: 5% each
        increase_percentage = 0.10 + (0.05 * (self.level - 1))
        return {"movement_speed_increase": increase_percentage}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class BasketballShoes(AbilityItem):
    item_id: ItemID = field(default=ItemID.BASKETBALL_SHOES, init=False)
    name: str = field(default="농구화", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="주기적으로 점프하여 무적이 됩니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        # 10s cooldown, -1s per level
        cooldown = 10.0 - (1.0 * (self.level - 1))
        return {"invulnerability_jump": {"cooldown": cooldown, "duration": 1.0}}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class RedGinseng(AbilityItem):
    item_id: ItemID = field(default=ItemID.RED_GINSENG, init=False)
    name: str = field(default="홍삼", init=False)
    max_level: int = field(default=1, init=False)
    description: str = field(default="체력을 50% 즉시 회복합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"instant_heal_percentage": 0.5}

    def apply_effect(self, target) -> None:
        # This will be handled by the ItemSystem as a one-time effect
        pass

@dataclass
class Milk(AbilityItem):
    item_id: ItemID = field(default=ItemID.MILK, init=False)
    name: str = field(default="우유", init=False)
    max_level: int = field(default=1, init=False)
    description: str = field(default="체력을 10% 즉시 회복합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"instant_heal_percentage": 0.1}

    def apply_effect(self, target) -> None:
        # This will be handled by the ItemSystem as a one-time effect
        pass