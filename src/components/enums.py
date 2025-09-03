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

# AI-DEV : 성능 최적화를 위한 배열 인덱스 기반 조회
# - 문제: 딕셔너리 조회보다 배열 인덱스 조회가 더 빠름 (게임 성능 중요)
# - 해결책: enum.value를 인덱스로 사용하는 배열 구조 
# - 주의사항: enum 순서와 배열 인덱스가 일치해야 함

# 클래스 메서드들을 별도로 정의
def _get_display_name(enemy_type: EnemyType) -> str:
    _display_names = {
        EnemyType.KOREAN_TEACHER: "국어선생님",
        EnemyType.MATH_TEACHER: "수학선생님",
        EnemyType.PRINCIPAL: "교장선생님"
    }
    return _display_names[enemy_type]

def _get_base_speed(enemy_type: EnemyType) -> float:
    _base_speeds = [2.0, 4.0, 3.0]        # 국어선생님(느림), 수학선생님(빠름), 교장선생님(중간)
    return _base_speeds[enemy_type.value]

def _get_base_health(enemy_type: EnemyType) -> int:
    _base_healths = [50, 30, 150]         # 국어선생님(중간), 수학선생님(낮음), 교장선생님(높음)
    return _base_healths[enemy_type.value]

def _get_base_attack_power(enemy_type: EnemyType) -> int:
    _base_attack_powers = [15, 10, 25]    # 국어선생님(중간), 수학선생님(낮음), 교장선생님(높음)
    return _base_attack_powers[enemy_type.value]

def _get_base_experience_yield(enemy_type: EnemyType) -> int:
    _base_experience_yields = [10, 5, 50] # 국어선생님(중간), 수학선생님(낮음), 교장선생님(높음)
    return _base_experience_yields[enemy_type.value]

# 동적으로 프로퍼티 추가
EnemyType.display_name = property(lambda self: _get_display_name(self))
EnemyType.base_speed = property(lambda self: _get_base_speed(self))  
EnemyType.base_health = property(lambda self: _get_base_health(self))
EnemyType.base_attack_power = property(lambda self: _get_base_attack_power(self))
EnemyType.base_experience_yield = property(lambda self: _get_base_experience_yield(self))

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

class ItemType(IntEnum):
    EXPERIENCE_ORB = 0

    @property
    def display_name(self) -> str:
        return ["경험치 구슬"][self.value]
