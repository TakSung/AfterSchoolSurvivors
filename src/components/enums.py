from enum import IntEnum

class EntityStatus(IntEnum):
    ALIVE = 0
    INVULNERABLE = 1
    DEAD = 2

    @property
    def display_name(self) -> str:
        return ["생존", "무적", "사망"][self.value]
