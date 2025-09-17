from dataclasses import dataclass, field
from .item import Item
from ..components.enums import ItemID, ItemType

@dataclass
class WeaponItem(Item):
    item_type: ItemType = field(default=ItemType.WEAPON, init=False)


@dataclass
class SoccerBall(WeaponItem):
    item_id: ItemID = field(default=ItemID.SOCCER_BALL, init=False)
    name: str = field(default="축구공", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="투사체 속도가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"projectile_speed_increase": 0.1 * self.level}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class Basketball(WeaponItem):
    item_id: ItemID = field(default=ItemID.BASKETBALL, init=False)
    name: str = field(default="농구공", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="투사체 크기가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"projectile_size_increase": 0.15 * self.level}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class BaseballBat(WeaponItem):
    item_id: ItemID = field(default=ItemID.BASEBALL_BAT, init=False)
    name: str = field(default="야구 배트", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="공격력이 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        return {"attack_power_increase": 0.2 * self.level}

    def apply_effect(self, target) -> None:
        pass
