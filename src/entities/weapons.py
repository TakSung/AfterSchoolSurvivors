from dataclasses import dataclass, field
from .item import Item
from components.enums import ItemID, ItemType

@dataclass
class WeaponItem(Item):
    item_type: ItemType = field(default=ItemType.WEAPON, init=False)


@dataclass
class SoccerBall(WeaponItem):
    item_id: ItemID = field(default=ItemID.SOCCER_BALL, init=False)
    name: str = field(default="축구공", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="여러 개의 공을 발사하고 튕기는 효과를 추가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        projectiles = 1
        if self.level >= 2:
            projectiles = 2
        if self.level >= 4:
            projectiles = 3
        
        bounces = 0
        if self.level >= 3:
            bounces = 1
        if self.level >= 5:
            bounces = 2
            
        return {"weapon_type": "soccer_ball", "projectiles": projectiles, "bounces": bounces}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class Basketball(WeaponItem):
    item_id: ItemID = field(default=ItemID.BASKETBALL, init=False)
    name: str = field(default="농구공", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="관통 능력이 생기고 발사 속도가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        pierce = 1
        if self.level >= 3:
            pierce = 2
        if self.level >= 5:
            pierce = 4

        attack_speed_increase = 0.0
        if self.level >= 2:
            attack_speed_increase += 0.2
        if self.level >= 4:
            attack_speed_increase += 0.3

        return {"weapon_type": "basketball", "pierce": pierce, "attack_speed_increase": attack_speed_increase}

    def apply_effect(self, target) -> None:
        pass

@dataclass
class BaseballBat(WeaponItem):
    item_id: ItemID = field(default=ItemID.BASEBALL_BAT, init=False)
    name: str = field(default="야구 배트", init=False)
    max_level: int = field(default=5, init=False)
    description: str = field(default="공격 범위와 속도가 증가합니다.", init=False)
    level: int = 1

    def get_effect(self) -> dict:
        angle = 90
        if self.level >= 3:
            angle = 180
        if self.level >= 5:
            angle = 360

        attack_speed_increase = 0.0
        if self.level >= 2:
            attack_speed_increase += 0.2
        if self.level >= 4:
            attack_speed_increase += 0.3
            
        return {"weapon_type": "baseball_bat", "angle": angle, "attack_speed_increase": attack_speed_increase}

    def apply_effect(self, target) -> None:
        pass
