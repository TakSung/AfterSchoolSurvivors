from enum import IntEnum

class EntityStatus(IntEnum):
    ALIVE = 0
    INVULNERABLE = 1
    DEAD = 2

    @property
    def display_name(self) -> str:
        return ["생존", "무적", "사망"][self.value]

# AI-NOTE : 2025-01-13 적 캐릭터 타입 시스템 도입
# - 이유: 3종의 서로 다른 적 캐릭터 구현을 위한 게임 기획 요구사항
# - 요구사항: 국어선생님(넓은 범위 공격), 수학선생님(빠른 돌진), 교장선생님(보스급)
# - 히스토리: 기존 단일 Enemy 클래스에서 타입별 차별화로 변경
class EnemyType(IntEnum):
    KOREAN_TEACHER = 0  # 국어선생님
    MATH_TEACHER = 1    # 수학선생님  
    PRINCIPAL = 2       # 교장선생님
    
    @property
    def display_name(self) -> str:
        return self._display_names[self]
    
    @property
    def base_speed(self) -> float:
        return self._base_speeds[self.value]
    
    @property
    def base_health(self) -> int:
        return self._base_healths[self.value]
    
    @property
    def base_attack_power(self) -> int:
        return self._base_attack_powers[self.value]
    
    _display_names = {
        KOREAN_TEACHER: "국어선생님",
        MATH_TEACHER: "수학선생님",
        PRINCIPAL: "교장선생님"
    }
    
    # AI-DEV : 성능 최적화를 위한 배열 인덱스 기반 조회
    # - 문제: 딕셔너리 조회보다 배열 인덱스 조회가 더 빠름 (게임 성능 중요)
    # - 해결책: enum.value를 인덱스로 사용하는 배열 구조 
    # - 주의사항: enum 순서와 배열 인덱스가 일치해야 함
    _base_speeds = [2.0, 4.0, 3.0]        # 국어선생님(느림), 수학선생님(빠름), 교장선생님(중간)
    _base_healths = [50, 30, 150]         # 국어선생님(중간), 수학선생님(낮음), 교장선생님(높음)
    _base_attack_powers = [15, 10, 25]    # 국어선생님(중간), 수학선생님(낮음), 교장선생님(높음)

class EnemyState(IntEnum):
    SPAWNING = 0     # 생성 중
    IDLE = 1         # 대기
    CHASING = 2      # 플레이어 추적
    ATTACKING = 3    # 공격 중
    STUNNED = 4      # 기절
    DYING = 5        # 사망 처리 중
    
    @property
    def display_name(self) -> str:
        return ["생성중", "대기", "추적", "공격", "기절", "사망"][self.value]
