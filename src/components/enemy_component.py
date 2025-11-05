from dataclasses import dataclass, field
from components.enums import EnemyType, EnemyState
from core.component import Component

# AI-NOTE : 2025-01-13 적 캐릭터 컴포넌트 시스템 구현
# - 이유: ECS 아키텍처에 따른 적 캐릭터 데이터 분리 설계
# - 요구사항: 적 타입별 고유 데이터와 상태 관리 시스템
# - 히스토리: 기존 pygame.sprite.Sprite 기반에서 ECS 컴포넌트 기반으로 전환

@dataclass
class EnemyComponent(Component):
    enemy_type: EnemyType
    speed: float = 2.0
    current_state: EnemyState = EnemyState.SPAWNING
    target_entity_id: int | None = None  # 추적할 타겟 엔티티 ID (보통 플레이어)
    attack_cooldown: float = 0.0  # 공격 쿨다운 남은 시간 (초)
    state_timer: float = 0.0      # 현재 상태 지속 시간 (초)
    spawn_delay: float = 0.5      # 생성 지연 시간 (초)
    
    # AI-DEV : 적 AI 동작을 위한 추가 데이터 필드
    # - 문제: 각 적 타입별로 다른 행동 패턴 구현 필요
    # - 해결책: 타입별 전용 데이터를 저장할 수 있는 딕셔너리 필드 추가
    # - 주의사항: 타입 안전성을 위해 특정 키 값들은 문서화 필요
    type_specific_data: dict[str, float] = field(default_factory=dict)

    # AI-NOTE : 2025-01-05 충돌 시 임시 무적 시스템 도입
    # - 이유: 프레임 단위 연속 데미지로 인한 즉사 방지 요구사항
    # - 요구사항: 무기에 맞았을 때 0.3초 무적 시간 부여로 다중 피격 방지
    # - 히스토리: 기존에는 매 프레임 데미지 적용으로 적이 즉사하는 문제 존재
    is_invulnerable: bool = False           # 무적 상태 여부
    invulnerability_timer: float = 0.0      # 무적 타이머 (초)
    invulnerability_duration: float = 0.3   # 무적 지속시간 (0.3초)
    
    def __post_init__(self) -> None:
        """적 타입에 따른 초기 데이터 설정"""
        if self.enemy_type == EnemyType.KOREAN_TEACHER:
            # 국어선생님: 넓은 범위 공격 설정
            self.type_specific_data.update({
                "attack_range": 80.0,      # 공격 범위 (픽셀)
                "attack_angle": 90.0,      # 공격 각도 (도)  
                "charge_time": 1.5         # 공격 준비 시간 (초)
            })
        elif self.enemy_type == EnemyType.MATH_TEACHER:
            # 수학선생님: 빠른 돌진 공격 설정
            self.type_specific_data.update({
                "dash_speed_multiplier": 3.0,  # 돌진 시 속도 배수
                "dash_duration": 1.0,          # 돌진 지속 시간 (초)
                "dash_cooldown": 3.0           # 돌진 쿨다운 시간 (초)
            })
        elif self.enemy_type == EnemyType.PRINCIPAL:
            # 교장선생님: 보스급 복합 공격 설정
            self.type_specific_data.update({
                "phase": 1,                    # 보스 페이즈 (1-3)
                "bullet_pattern_timer": 0.0,   # 탄막 패턴 타이머 (초)
                "teleport_cooldown": 0.0,      # 순간이동 쿨다운 (초)
                "special_attack_counter": 0    # 특수 공격 카운터
            })