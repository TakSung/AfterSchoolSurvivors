from components.enums import EnemyType
from components.enemy_component import EnemyComponent
from .enemy import Enemy

# AI-NOTE : 2025-01-13 국어선생님 캐릭터 구현 
# - 이유: 느린 이동과 넓은 범위 공격 패턴을 가진 적 캐릭터 요구사항
# - 요구사항: 천천히 접근하며 부채꼴 모양의 넓은 범위 공격 실행
# - 히스토리: 3종 적 캐릭터 중 구현 복잡도가 가장 낮은 첫 번째 구현

class KoreanTeacher(Enemy):
    """
    국어선생님 적 캐릭터 클래스
    
    특징:
    - 느린 이동 속도 (2.0)
    - 넓은 범위 공격 (부채꼴 형태, 90도 각도)
    - 중간 체력 (50)
    - 공격 전 1.5초 준비 시간 필요
    
    AI 패턴:
    1. 플레이어를 향해 천천히 접근
    2. 일정 거리(80픽셀) 내에서 공격 준비
    3. 1.5초 후 부채꼴 범위 공격 실행
    4. 공격 후 잠시 대기 후 다시 접근
    """
    
    def __init__(self):
        super().__init__(EnemyType.KOREAN_TEACHER)
    
    def get_specific_ai_behavior(self) -> dict[str, float]:
        """국어선생님 전용 AI 행동 파라미터"""
        
        # AI-DEV : 국어선생님 AI 튜닝을 위한 매개변수화
        # - 문제: 하드코딩된 값들은 게임 밸런스 조정 시 코드 수정 필요
        # - 해결책: 설정 가능한 매개변수로 분리하여 런타임 조정 가능
        # - 주의사항: 매개변수명은 다른 적 타입과 충돌하지 않도록 접두사 사용
        
        return {
            # 이동 관련 매개변수  
            "kt_approach_speed": 100.0,           # 접근 속도 (픽셀/프레임)
            "kt_min_attack_distance": 600.0,     # 최소 공격 거리 (픽셀)
            "kt_max_attack_distance": 1000.0,    # 최대 공격 거리 (픽셀)  
            "kt_optimal_distance": 800.0,        # 최적 공격 거리 (픽셀)
            
            # 상태 전환 관련
            "kt_attack_preparation_time": 1.5,  # 공격 준비 시간 (초)
            "kt_post_attack_cooldown": 2.0,     # 공격 후 쿨다운 (초)
            "kt_chase_timeout": 5.0,            # 추적 포기 시간 (초)
            
            # AI 판단 관련
            "kt_player_proximity_threshold": 1200.0,  # 플레이어 감지 거리 (픽셀)
            "kt_retreat_threshold": 400.0,            # 후퇴 판단 거리 (픽셀)
        }
    
    def get_attack_pattern_data(self) -> dict[str, float]:
        """국어선생님 전용 공격 패턴 데이터"""
        return {
            # 공격 범위 및 형태
            "kt_attack_angle": 90.0,            # 공격 각도 (도) - 부채꼴
            "kt_attack_range": 80.0,            # 공격 범위 (픽셀)
            "kt_attack_damage": 15,             # 공격 데미지
            
            # 부채꼴 공격 세부 설정
            "kt_fan_segments": 5,               # 부채꼴 분할 수 (더 정밀한 공격)
            "kt_attack_duration": 0.5,          # 공격 지속 시간 (초)
            
            # 시각적 효과 관련
            "kt_charge_visual_scale": 1.2,      # 공격 준비 시 크기 배율
            "kt_attack_visual_flash": 0.3,      # 공격 시 번쩍임 효과 (초)
            
            # 공격 빈도 제한
            "kt_attack_cooldown_time": 3.0,     # 공격 간 최소 간격 (초)
            "kt_consecutive_attack_limit": 2,   # 연속 공격 최대 횟수
        }
    
    def calculate_optimal_position(self, player_x: float, player_y: float) -> tuple[float, float]:
        """
        플레이어 위치를 기반으로 최적 공격 위치 계산
        
        Args:
            player_x: 플레이어 X 좌표
            player_y: 플레이어 Y 좌표
            
        Returns:
            최적 공격 위치 (x, y)
        """
        if not self._entity_manager or not self._entity:
            return (0.0, 0.0)
        
        # 현재 위치 가져오기
        from components.position_component import PositionComponent
        pos_comp = self._entity_manager.get_component(self._entity.id, PositionComponent)
        if not pos_comp:
            return (0.0, 0.0)
        
        # 플레이어와의 거리 및 각도 계산
        distance = self.get_distance_to_target(player_x, player_y)
        angle = self.get_angle_to_target(player_x, player_y)
        
        # 최적 거리 가져오기
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            optimal_distance = 80.0  # 기본값
        else:
            optimal_distance = enemy_comp.type_specific_data.get("kt_optimal_distance", 80.0)
        
        # 최적 거리만큼 떨어진 위치 계산
        import math
        optimal_x = player_x - math.cos(angle) * optimal_distance
        optimal_y = player_y - math.sin(angle) * optimal_distance
        
        return (optimal_x, optimal_y)
    
    def is_in_attack_range(self, player_x: float, player_y: float) -> bool:
        """플레이어가 공격 범위 내에 있는지 확인"""
        distance = self.get_distance_to_target(player_x, player_y)
        
        if not self._entity_manager or not self._entity:
            return False
        
        from components.enemy_component import EnemyComponent
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return False
        
        min_distance = enemy_comp.type_specific_data.get("kt_min_attack_distance", 60.0)
        max_distance = enemy_comp.type_specific_data.get("kt_max_attack_distance", 100.0)
        
        return min_distance <= distance <= max_distance
    
    def should_prepare_attack(self, player_x: float, player_y: float) -> bool:
        """공격 준비를 시작해야 하는지 판단"""
        if not self.is_in_attack_range(player_x, player_y):
            return False
        
        # 쿨다운 확인
        if not self._entity_manager or not self._entity:
            return False
        
        enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
        if not enemy_comp:
            return False
        
        # 공격 쿨다운이 끝났는지 확인
        return enemy_comp.attack_cooldown <= 0.0
    
    def __repr__(self) -> str:
        return f"KoreanTeacher(entity_id={self._entity.id if self._entity else 'None'})"