import math as math_module
from ..components.enums import EnemyType, EnemyState
from ..components.enemy_component import EnemyComponent
from .enemy import Enemy

# AI-NOTE : 2025-01-13 수학선생님 캐릭터 구현
# - 이유: 빠른 이동과 직선 돌진 공격 패턴을 가진 적 캐릭터 요구사항
# - 요구사항: 빠른 이동으로 플레이어 방향으로 직선 돌진 공격 실행
# - 히스토리: 국어선생님 다음으로 구현, 이동 패턴 차별화 중점

class MathTeacher(Enemy):
    """
    수학선생님 적 캐릭터 클래스
    
    특징:
    - 빠른 이동 속도 (4.0)
    - 직선 돌진 공격 (플레이어 방향으로 3배속 돌진)
    - 낮은 체력 (30)
    - 돌진 후 3초 쿨다운 필요
    
    AI 패턴:
    1. 플레이어를 향해 빠르게 접근
    2. 일정 거리에서 돌진 준비 (0.5초)
    3. 플레이어 방향으로 1초간 고속 돌진
    4. 돌진 종료 후 3초 쿨다운
    5. 쿨다운 중에는 천천히 회피 움직임
    """
    
    def __init__(self):
        super().__init__(EnemyType.MATH_TEACHER)
    
    def get_specific_ai_behavior(self) -> dict[str, float]:
        """수학선생님 전용 AI 행동 파라미터"""
        
        # AI-DEV : 수학선생님 돌진 AI 튜닝을 위한 매개변수화
        # - 문제: 돌진 공격의 속도와 거리 조절이 게임 밸런스에 크게 영향
        # - 해결책: 세밀한 튜닝이 가능한 매개변수 분리로 런타임 조정 가능
        # - 주의사항: 돌진 속도가 너무 빠르면 플레이어가 회피 불가능
        
        return {
            # 기본 이동 관련
            "mt_normal_speed": 4.0,             # 일반 이동 속도 (픽셀/프레임)
            "mt_approach_distance": 150.0,       # 돌진 준비 거리 (픽셀)
            "mt_optimal_dash_distance": 120.0,   # 최적 돌진 시작 거리 (픽셀)
            
            # 돌진 공격 관련
            "mt_dash_speed_multiplier": 3.0,     # 돌진 시 속도 배수
            "mt_dash_preparation_time": 0.5,     # 돌진 준비 시간 (초)
            "mt_dash_duration": 1.0,             # 돌진 지속 시간 (초)
            "mt_dash_cooldown": 3.0,             # 돌진 후 쿨다운 (초)
            
            # 상태 전환 관련
            "mt_stunned_duration": 0.3,          # 돌진 종료 후 기절 시간 (초)
            "mt_retreat_speed_multiplier": 0.7,  # 쿨다운 중 이동 속도 배수
            
            # AI 판단 관련
            "mt_player_detection_range": 200.0,  # 플레이어 감지 거리 (픽셀)
            "mt_dash_min_distance": 80.0,        # 돌진 최소 거리 (픽셀)
            "mt_dash_max_distance": 180.0,       # 돌진 최대 거리 (픽셀)
        }
    
    def get_attack_pattern_data(self) -> dict[str, float]:
        """수학선생님 전용 공격 패턴 데이터"""
        return {
            # 돌진 공격 데미지 및 효과
            "mt_dash_damage": 10,               # 돌진 공격 데미지
            "mt_collision_width": 25.0,         # 돌진 충돌 판정 폭 (픽셀)
            "mt_collision_height": 25.0,        # 돌진 충돌 판정 높이 (픽셀)
            
            # 돌진 궤적 및 정확도
            "mt_dash_accuracy": 0.95,           # 돌진 정확도 (1.0 = 100% 정확)
            "mt_trajectory_deviation": 5.0,     # 궤적 편차 (도)
            
            # 시각적 효과
            "mt_dash_trail_duration": 0.8,      # 돌진 궤적 표시 시간 (초)
            "mt_preparation_scale": 1.1,        # 돌진 준비 시 크기 배율
            "mt_dash_scale": 1.3,               # 돌진 중 크기 배율
            
            # 연속 공격 제한
            "mt_max_consecutive_dashes": 3,     # 최대 연속 돌진 횟수
            "mt_forced_cooldown_after": 3,     # N회 돌진 후 강제 쿨다운
        }
    
    def calculate_dash_target(self, player_x: float, player_y: float) -> tuple[float, float]:
        """
        플레이어 위치를 예측하여 돌진 타겟 좌표 계산
        
        Args:
            player_x: 현재 플레이어 X 좌표
            player_y: 현재 플레이어 Y 좌표
            
        Returns:
            돌진할 타겟 좌표 (x, y)
        """
        if not self._entity_manager or not self._entity:
            return (player_x, player_y)
        
        from ..components.position_component import PositionComponent
        pos_comp = self._entity_manager.get_component(self._entity.id, PositionComponent)
        if not pos_comp:
            return (player_x, player_y)
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return (player_x, player_y)
        
        # 돌진 정확도 가져오기 (플레이어 예측 강도)
        accuracy = enemy_comp.type_specific_data.get("mt_dash_accuracy", 0.95)
        deviation = enemy_comp.type_specific_data.get("mt_trajectory_deviation", 5.0)
        
        # 기본적으로는 현재 플레이어 위치를 타겟으로 설정
        target_x, target_y = player_x, player_y
        
        # AI-DEV : 플레이어 움직임 예측 알고리즘
        # - 문제: 단순 직선 돌진은 플레이어가 쉽게 회피 가능
        # - 해결책: 플레이어의 이동 패턴을 간단히 예측하여 선행 타격
        # - 주의사항: 예측이 너무 정확하면 플레이어 불만, 너무 부정확하면 AI가 바보같음
        
        if accuracy > 0.5:  # 예측 수행 최소 임계값
            # 플레이어와의 거리 계산
            distance = self.get_distance_to_target(player_x, player_y)
            dash_time = enemy_comp.type_specific_data.get("mt_dash_duration", 1.0)
            
            # 돌진에 걸리는 시간 동안 플레이어가 이동할 거리 추정
            # (간단한 추정: 플레이어가 계속 같은 방향으로 이동한다고 가정)
            estimated_player_speed = 5.0  # 플레이어 평균 속도 추정
            predicted_distance = estimated_player_speed * dash_time * accuracy
            
            # 현재 플레이어가 이동하고 있는 방향 추정 (단순화)
            # 실제로는 이전 프레임들의 위치를 저장해서 속도 벡터를 계산해야 함
            angle = self.get_angle_to_target(player_x, player_y)
            
            # 약간의 랜덤 편차 추가 (AI가 너무 완벽하지 않게)
            import random
            angle_deviation = math_module.radians(random.uniform(-deviation, deviation))
            adjusted_angle = angle + angle_deviation
            
            # 예측 위치 계산
            target_x = player_x + math_module.cos(adjusted_angle) * predicted_distance
            target_y = player_y + math_module.sin(adjusted_angle) * predicted_distance
        
        return (target_x, target_y)
    
    def is_in_dash_range(self, player_x: float, player_y: float) -> bool:
        """플레이어가 돌진 공격 범위 내에 있는지 확인"""
        distance = self.get_distance_to_target(player_x, player_y)
        
        if not self._entity_manager or not self._entity:
            return False
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return False
        
        min_distance = enemy_comp.type_specific_data.get("mt_dash_min_distance", 80.0)
        max_distance = enemy_comp.type_specific_data.get("mt_dash_max_distance", 180.0)
        
        return min_distance <= distance <= max_distance
    
    def should_prepare_dash(self, player_x: float, player_y: float) -> bool:
        """돌진 준비를 시작해야 하는지 판단"""
        if not self.is_in_dash_range(player_x, player_y):
            return False
        
        if not self._entity_manager or not self._entity:
            return False
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return False
        
        # 돌진 쿨다운 확인
        if enemy_comp.attack_cooldown > 0.0:
            return False
        
        # 현재 상태가 돌진 가능한 상태인지 확인
        return enemy_comp.current_state in [EnemyState.CHASING, EnemyState.IDLE]
    
    def calculate_dash_velocity(self, target_x: float, target_y: float) -> tuple[float, float]:
        """돌진 방향의 속도 벡터 계산"""
        if not self._entity_manager or not self._entity:
            return (0.0, 0.0)
        
        from ..components.position_component import PositionComponent
        pos_comp = self._entity_manager.get_component(self._entity.id, PositionComponent)
        if not pos_comp:
            return (0.0, 0.0)
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return (0.0, 0.0)
        
        # 타겟 방향 벡터 계산
        dx = target_x - pos_comp.x
        dy = target_y - pos_comp.y
        distance = math_module.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return (0.0, 0.0)
        
        # 정규화된 방향 벡터
        norm_dx = dx / distance
        norm_dy = dy / distance
        
        # 돌진 속도 적용
        base_speed = self.enemy_type.base_speed
        dash_multiplier = enemy_comp.type_specific_data.get("mt_dash_speed_multiplier", 3.0)
        dash_speed = base_speed * dash_multiplier
        
        return (norm_dx * dash_speed, norm_dy * dash_speed)
    
    def __repr__(self) -> str:
        return f"MathTeacher(entity_id={self._entity.id if self._entity else 'None'})"