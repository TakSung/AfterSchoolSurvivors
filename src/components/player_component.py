from dataclasses import dataclass, field
from core.component import Component

@dataclass
class PlayerComponent(Component):
    """
    A component for the player entity.
    """
    level: int = 1
    experience: int = 0
    total_experience: int = 0
    experience_to_next_level: int = 100
    base_movement_speed: float = 5.0
    movement_speed: float = 5.0
    base_attack_speed: float = 1.0  # attacks per second
    attack_speed: float = 1.0

    # AI-NOTE : 2025-01-05 무적 시스템 통합 관리
    # - 이유: 충돌 무적과 농구화 무적을 하나의 플래그로 관리하되 duration으로 구분
    # - 요구사항: 충돌 무적(0.5초), 농구화 무적(1.0초) 지원
    # - 히스토리: 두 무적 시스템이 timer를 공유하여 충돌 문제 발생 -> duration 기반으로 개선
    is_invulnerable: bool = False
    invulnerability_timer: float = 0.0
    invulnerability_cooldown: float = 100.0  # 농구화 무적 쿨다운
    invulnerability_duration: float = 1.0   # 현재 적용 중인 무적 지속시간
    collision_invuln_duration: float = 6.0  # 충돌 무적 기본 지속시간

    # for baseball bat synergy
    trigger_bat_swing: bool = False

    # for trap debuff
    slow_debuff_timer: float = 0.0
    slow_debuff_stacks: int = 0
