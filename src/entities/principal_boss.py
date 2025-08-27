import math as math_module
import random
from enum import IntEnum
from components.enums import EnemyType, EnemyState
from components.enemy_component import EnemyComponent
from .enemy import Enemy

# AI-NOTE : 2025-01-13 교장선생님 보스 캐릭터 구현
# - 이유: 복합 공격 패턴과 페이즈 시스템을 가진 보스급 적 캐릭터 요구사항
# - 요구사항: 높은 체력(150), 원형 탄막, 추적 미사일, 순간이동 등 다양한 공격 패턴
# - 히스토리: 3종 적 캐릭터 중 가장 복잡한 AI를 가진 최종 보스 구현

class BossPhase(IntEnum):
    """보스 페이즈 열거형"""
    PHASE_1 = 1  # 체력 100% - 70%: 기본 패턴
    PHASE_2 = 2  # 체력 70% - 30%: 강화 패턴
    PHASE_3 = 3  # 체력 30% - 0%: 광폭 패턴
    
    @property
    def display_name(self) -> str:
        return ["", "1단계", "2단계", "3단계"][self.value]

class BossAttackPattern(IntEnum):
    """보스 공격 패턴 열거형"""
    CIRCULAR_BULLETS = 0    # 원형 탄막
    HOMING_MISSILES = 1     # 추적 미사일
    TELEPORT_STRIKE = 2     # 순간이동 공격
    LASER_BEAM = 3          # 레이저 빔
    SUMMON_MINIONS = 4      # 졸병 소환
    
    @property
    def display_name(self) -> str:
        return ["원형탄막", "추적미사일", "순간이동공격", "레이저빔", "졸병소환"][self.value]

class PrincipalBoss(Enemy):
    """
    교장선생님 보스 캐릭터 클래스
    
    특징:
    - 높은 체력 (150)
    - 3단계 페이즈 시스템 (체력에 따라 패턴 변화)
    - 5가지 공격 패턴 (원형 탄막, 추적 미사일, 순간이동, 레이저, 소환)
    - 중간 이동 속도 (3.0)
    - 높은 공격력 (25)
    
    AI 패턴:
    페이즈 1 (100%-70%): 
      - 원형 탄막 (3초 간격)
      - 추적 미사일 (5초 간격)
      
    페이즈 2 (70%-30%):
      - 순간이동 공격 추가 (4초 간격)
      - 레이저 빔 추가 (6초 간격)
      - 공격 속도 1.2배 증가
      
    페이즈 3 (30%-0%):
      - 졸병 소환 추가 (8초 간격)
      - 모든 공격 속도 1.5배 증가
      - 체력 회복 (10초마다 5%)
    """
    
    def __init__(self):
        super().__init__(EnemyType.PRINCIPAL)
        self._current_phase = BossPhase.PHASE_1
        self._last_pattern_times: dict[BossAttackPattern, float] = {}
        self._pattern_queue: list[BossAttackPattern] = []
    
    def get_specific_ai_behavior(self) -> dict[str, float]:
        """교장선생님 전용 AI 행동 파라미터"""
        
        # AI-DEV : 보스 AI 복잡도 관리를 위한 상태머신 기반 매개변수화
        # - 문제: 여러 공격 패턴과 페이즈가 복합적으로 작용하여 코드 복잡도 증가
        # - 해결책: 페이즈별, 패턴별로 독립적인 매개변수 관리로 튜닝 용이성 확보
        # - 주의사항: 매개변수가 많아질수록 밸런싱 난이도 상승, 체계적 관리 필요
        
        return {
            # 기본 행동 매개변수
            "pb_base_speed": 3.0,               # 기본 이동 속도
            "pb_phase_transition_delay": 2.0,   # 페이즈 전환 시 지연 시간 (초)
            "pb_invulnerable_during_special": 1.0,  # 특수 공격 중 무적 시간 (초)
            
            # 페이즈별 속도 배율
            "pb_phase1_speed_mult": 1.0,        # 페이즈 1 속도 배율
            "pb_phase2_speed_mult": 1.2,        # 페이즈 2 속도 배율  
            "pb_phase3_speed_mult": 1.5,        # 페이즈 3 속도 배율
            
            # 이동 패턴 관련
            "pb_orbit_radius": 200.0,           # 플레이어 주위 궤도 반지름
            "pb_orbit_speed": 0.5,              # 궤도 회전 속도 (rad/sec)
            "pb_random_movement_range": 100.0,  # 랜덤 이동 범위
            
            # 공격 준비 관련
            "pb_attack_telegraph_time": 1.0,    # 공격 예고 시간 (초)
            "pb_attack_recovery_time": 0.8,     # 공격 후 회복 시간 (초)
            
            # 페이즈 3 특수 능력
            "pb_health_regen_interval": 10.0,   # 체력 회복 간격 (초)
            "pb_health_regen_percent": 0.05,    # 체력 회복 비율 (5%)
        }
    
    def get_attack_pattern_data(self) -> dict[str, float]:
        """교장선생님 전용 공격 패턴 데이터"""
        return {
            # 원형 탄막 패턴
            "pb_circular_cooldown": 3.0,        # 원형 탄막 쿨다운 (초)
            "pb_circular_bullet_count": 12,     # 원형 탄막 총알 수
            "pb_circular_bullet_speed": 8.0,    # 원형 탄막 속도
            "pb_circular_damage": 15,           # 원형 탄막 데미지
            
            # 추적 미사일 패턴  
            "pb_homing_cooldown": 5.0,          # 추적 미사일 쿨다운 (초)
            "pb_homing_missile_count": 3,       # 추적 미사일 수
            "pb_homing_speed": 6.0,             # 추적 미사일 속도
            "pb_homing_turn_rate": 2.0,         # 추적 미사일 회전율 (rad/sec)
            "pb_homing_damage": 20,             # 추적 미사일 데미지
            
            # 순간이동 공격 패턴
            "pb_teleport_cooldown": 4.0,        # 순간이동 쿨다운 (초)
            "pb_teleport_range": 300.0,         # 순간이동 범위 (픽셀)
            "pb_teleport_attack_radius": 50.0,  # 순간이동 공격 범위 (픽셀)
            "pb_teleport_damage": 30,           # 순간이동 공격 데미지
            
            # 레이저 빔 패턴
            "pb_laser_cooldown": 6.0,           # 레이저 빔 쿨다운 (초)
            "pb_laser_charge_time": 2.0,        # 레이저 충전 시간 (초)
            "pb_laser_duration": 1.5,           # 레이저 지속 시간 (초)
            "pb_laser_width": 20.0,             # 레이저 폭 (픽셀)
            "pb_laser_damage_per_sec": 40,      # 레이저 초당 데미지
            
            # 졸병 소환 패턴
            "pb_summon_cooldown": 8.0,          # 졸병 소환 쿨다운 (초)  
            "pb_summon_count": 2,               # 한 번에 소환할 졸병 수
            "pb_summon_range": 150.0,           # 소환 범위 (픽셀)
            "pb_minion_health": 20,             # 소환된 졸병 체력
        }
    
    def get_current_phase(self) -> BossPhase:
        """현재 보스 페이즈 반환"""
        if not self._entity_manager or not self._entity:
            return BossPhase.PHASE_1
        
        from components.health_component import HealthComponent
        health_comp = self._entity_manager.get_component(self._entity.id, HealthComponent)
        if not health_comp:
            return BossPhase.PHASE_1
        
        health_percentage = health_comp.current / health_comp.maximum
        
        if health_percentage > 0.7:
            return BossPhase.PHASE_1
        elif health_percentage > 0.3:
            return BossPhase.PHASE_2
        else:
            return BossPhase.PHASE_3
    
    def update_phase(self) -> bool:
        """페이즈 업데이트 및 변경 여부 반환"""
        new_phase = self.get_current_phase()
        if new_phase != self._current_phase:
            self._current_phase = new_phase
            self._on_phase_change(new_phase)
            return True
        return False
    
    def _on_phase_change(self, new_phase: BossPhase) -> None:
        """페이즈 변경 시 호출되는 이벤트 처리"""
        if not self._entity_manager or not self._entity:
            return
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return
        
        # 페이즈 데이터 업데이트
        enemy_comp.type_specific_data["phase"] = new_phase.value
        
        # 페이즈 전환 시 일시적 무적 상태
        enemy_comp.state_timer = enemy_comp.type_specific_data.get("pb_phase_transition_delay", 2.0)
        
        # 패턴 큐 초기화
        self._pattern_queue.clear()
        self._update_available_patterns(new_phase)
        
    def _update_available_patterns(self, phase: BossPhase) -> None:
        """페이즈에 따른 사용 가능한 공격 패턴 업데이트"""
        self._pattern_queue.clear()
        
        if phase == BossPhase.PHASE_1:
            self._pattern_queue.extend([
                BossAttackPattern.CIRCULAR_BULLETS,
                BossAttackPattern.HOMING_MISSILES
            ])
        elif phase == BossPhase.PHASE_2:
            self._pattern_queue.extend([
                BossAttackPattern.CIRCULAR_BULLETS,
                BossAttackPattern.HOMING_MISSILES,
                BossAttackPattern.TELEPORT_STRIKE,
                BossAttackPattern.LASER_BEAM
            ])
        else:  # PHASE_3
            self._pattern_queue.extend([
                BossAttackPattern.CIRCULAR_BULLETS,
                BossAttackPattern.HOMING_MISSILES,
                BossAttackPattern.TELEPORT_STRIKE,
                BossAttackPattern.LASER_BEAM,
                BossAttackPattern.SUMMON_MINIONS
            ])
    
    def get_next_attack_pattern(self, current_time: float) -> BossAttackPattern | None:
        """다음 공격 패턴 결정"""
        if not self._pattern_queue:
            self._update_available_patterns(self._current_phase)
        
        # AI-DEV : 보스 공격 패턴 선택 알고리즘
        # - 문제: 단순 랜덤 선택은 예측 가능하거나 불규칙적일 수 있음
        # - 해결책: 쿨다운 기반 우선순위와 가중 랜덤을 조합한 하이브리드 선택
        # - 주의사항: 너무 복잡하면 디버깅 어려움, 적절한 복잡도 유지 필요
        
        available_patterns = []
        
        # 쿨다운이 끝난 패턴들만 필터링
        for pattern in self._pattern_queue:
            last_used = self._last_pattern_times.get(pattern, 0.0)
            cooldown = self._get_pattern_cooldown(pattern)
            
            if current_time - last_used >= cooldown:
                available_patterns.append(pattern)
        
        if not available_patterns:
            return None
        
        # 가중 랜덤 선택 (최근에 사용하지 않은 패턴에 더 높은 가중치)
        weights = []
        for pattern in available_patterns:
            last_used = self._last_pattern_times.get(pattern, 0.0)
            time_since_last = current_time - last_used
            
            # 시간이 많이 지날수록 높은 가중치
            weight = 1.0 + (time_since_last / 10.0)  # 10초마다 가중치 +1
            weights.append(weight)
        
        # 가중 랜덤 선택
        selected_pattern = random.choices(available_patterns, weights=weights)[0]
        self._last_pattern_times[selected_pattern] = current_time
        
        return selected_pattern
    
    def _get_pattern_cooldown(self, pattern: BossAttackPattern) -> float:
        """패턴별 쿨다운 시간 반환"""
        if not self._entity_manager or not self._entity:
            return 1.0
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return 1.0
        
        cooldown_map = {
            BossAttackPattern.CIRCULAR_BULLETS: "pb_circular_cooldown",
            BossAttackPattern.HOMING_MISSILES: "pb_homing_cooldown", 
            BossAttackPattern.TELEPORT_STRIKE: "pb_teleport_cooldown",
            BossAttackPattern.LASER_BEAM: "pb_laser_cooldown",
            BossAttackPattern.SUMMON_MINIONS: "pb_summon_cooldown"
        }
        
        key = cooldown_map.get(pattern, "pb_circular_cooldown")
        base_cooldown = enemy_comp.type_specific_data.get(key, 3.0)
        
        # 페이즈에 따른 쿨다운 배율 적용
        phase_multipliers = {
            BossPhase.PHASE_1: 1.0,
            BossPhase.PHASE_2: 0.8,  # 20% 빨라짐
            BossPhase.PHASE_3: 0.6   # 40% 빨라짐
        }
        
        multiplier = phase_multipliers.get(self._current_phase, 1.0)
        return base_cooldown * multiplier
    
    def calculate_orbital_position(self, player_x: float, player_y: float, time: float) -> tuple[float, float]:
        """플레이어 주위 궤도 운동 위치 계산"""
        if not self._entity_manager or not self._entity:
            return (player_x, player_y)
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return (player_x, player_y)
        
        radius = enemy_comp.type_specific_data.get("pb_orbit_radius", 200.0)
        orbit_speed = enemy_comp.type_specific_data.get("pb_orbit_speed", 0.5)
        
        # 궤도 각도 계산 (시간 기반)
        angle = time * orbit_speed
        
        # 궤도 위치 계산
        orbit_x = player_x + math_module.cos(angle) * radius
        orbit_y = player_y + math_module.sin(angle) * radius
        
        return (orbit_x, orbit_y)
    
    def should_regenerate_health(self, current_time: float) -> bool:
        """체력 회복을 해야 하는지 판단 (페이즈 3 전용)"""
        if self._current_phase != BossPhase.PHASE_3:
            return False
        
        if not self._entity_manager or not self._entity:
            return False
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return False
        
        last_regen_time = enemy_comp.type_specific_data.get("last_health_regen", 0.0)
        regen_interval = enemy_comp.type_specific_data.get("pb_health_regen_interval", 10.0)
        
        return current_time - last_regen_time >= regen_interval
    
    def regenerate_health(self, current_time: float) -> None:
        """체력 회복 실행"""
        if not self._entity_manager or not self._entity:
            return
        
        from components.health_component import HealthComponent
        health_comp = self._entity_manager.get_component(self._entity.id, HealthComponent)
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        
        if not health_comp or not enemy_comp:
            return
        
        regen_percent = enemy_comp.type_specific_data.get("pb_health_regen_percent", 0.05)
        regen_amount = int(health_comp.maximum * regen_percent)
        
        health_comp.current = min(health_comp.current + regen_amount, health_comp.maximum)
        enemy_comp.type_specific_data["last_health_regen"] = current_time
    
    def __repr__(self) -> str:
        return f"PrincipalBoss(phase={self._current_phase.display_name}, entity_id={self._entity.id if self._entity else 'None'})"