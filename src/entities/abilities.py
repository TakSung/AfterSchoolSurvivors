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
    description: str = field(default="이동속도가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"movement_speed_increase": 0.08 * self.level}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class BasketballShoes(AbilityItem):
    item_id: ItemID = field(default=ItemID.BASKETBALL_SHOES, init=False)
    name: str = field(default="농구화", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="점프력/회피가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        # TODO: Define how evasion works
        return {"evasion_increase": 0.1 * self.level}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class RedGinseng(AbilityItem):
    item_id: ItemID = field(default=ItemID.RED_GINSENG, init=False)
    name: str = field(default="홍삼", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="최대체력이 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"max_health_increase": 25 * self.level}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class Milk(AbilityItem):
    item_id: ItemID = field(default=ItemID.MILK, init=False)
    name: str = field(default="우유", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="체력재생 속도가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"health_regen_increase": 2 * self.level}

    def apply_effect(self, target) -> None:
        pass
