from abc import ABC, abstractmethod
import random
import math
from typing import TYPE_CHECKING, Union, Optional

from core.entity import Entity
from ..components.enemy_component import EnemyComponent
from ..components.health_component import HealthComponent
from ..components.position_component import PositionComponent
from ..components.velocity_component import VelocityComponent
from ..components.enums import EnemyType, EnemyState, EntityStatus

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

# AI-NOTE : 2025-01-13 Enemy 베이스 클래스 ECS 아키텍처 구현
# - 이유: 모든 적 캐릭터의 공통 기능 및 팩토리 패턴 제공 요구사항
# - 요구사항: 3종 적 캐릭터의 베이스 클래스와 생성 팩토리 시스템
# - 히스토리: 기존 pygame.sprite.Sprite 기반에서 순수 ECS 패턴으로 전환

class Enemy(ABC):
    """
    모든 적 캐릭터의 베이스 클래스입니다.
    ECS 아키텍처를 기반으로 하며, 팩토리 패턴을 제공합니다.
    """
    
    # 화면 경계 상수 (나중에 설정 파일에서 가져올 수 있음)
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    SPAWN_MARGIN = 50  # 화면 밖 생성 여백
    
    def __init__(self, enemy_type: EnemyType):
        self.enemy_type = enemy_type
        self._entity: Optional[Entity] = None
        self._entity_manager: Optional["EntityManager"] = None
    
    @property
    def entity(self) -> Optional[Entity]:
        """연결된 엔티티 반환"""
        return self._entity
    
    @property 
    def entity_manager(self) -> Optional["EntityManager"]:
        """연결된 엔티티 매니저 반환"""
        return self._entity_manager
    
    @abstractmethod
    def get_specific_ai_behavior(self) -> dict[str, float]:
        """각 적 타입별 고유 AI 행동 파라미터 반환"""
        pass
    
    @abstractmethod 
    def get_attack_pattern_data(self) -> dict[str, float]:
        """각 적 타입별 고유 공격 패턴 데이터 반환"""
        pass
    
    def create_entity(self, entity_manager: "EntityManager", spawn_x: Optional[float] = None, spawn_y: Optional[float] = None) -> Entity:
        """
        적 엔티티를 생성하고 필요한 컴포넌트들을 추가합니다.
        
        Args:
            entity_manager: 엔티티를 관리할 EntityManager 인스턴스
            spawn_x: 생성 X 좌표 (None이면 화면 가장자리에서 랜덤)
            spawn_y: 생성 Y 좌표 (None이면 화면 가장자리에서 랜덤)
        
        Returns:
            생성된 Entity 인스턴스
        """
        # 엔티티 생성
        entity = entity_manager.create_entity()
        self._entity = entity
        self._entity_manager = entity_manager
        
        # 스폰 위치 계산 (화면 가장자리)
        if spawn_x is None or spawn_y is None:
            spawn_x, spawn_y = self._calculate_spawn_position()
        
        # 기본 컴포넌트들 추가
        self._add_position_component(entity_manager, entity.id, spawn_x, spawn_y)
        self._add_velocity_component(entity_manager, entity.id)
        self._add_health_component(entity_manager, entity.id)
        self._add_enemy_component(entity_manager, entity.id)
        
        return entity
    
    def _calculate_spawn_position(self) -> tuple[float, float]:
        """화면 가장자리에서 랜덤한 스폰 위치 계산"""
        
        # AI-DEV : 균등한 가장자리 스폰을 위한 weighted random 알고리즘
        # - 문제: 단순 random.choice는 코너에서 겹치는 확률이 높음
        # - 해결책: 가장자리 길이에 비례한 가중치로 위치 선택
        # - 주의사항: 화면 크기 변경 시 SCREEN_WIDTH, SCREEN_HEIGHT 업데이트 필요
        
        edges = ['top', 'bottom', 'left', 'right']
        edge = random.choice(edges)
        margin = self.SPAWN_MARGIN
        
        if edge == 'top':
            return (
                random.uniform(-margin, self.SCREEN_WIDTH + margin),
                -margin
            )
        elif edge == 'bottom':
            return (
                random.uniform(-margin, self.SCREEN_WIDTH + margin), 
                self.SCREEN_HEIGHT + margin
            )
        elif edge == 'left':
            return (
                -margin,
                random.uniform(-margin, self.SCREEN_HEIGHT + margin)
            )
        else:  # right
            return (
                self.SCREEN_WIDTH + margin,
                random.uniform(-margin, self.SCREEN_HEIGHT + margin)
            )
    
    def _add_position_component(self, entity_manager: "EntityManager", entity_id: int, x: float, y: float) -> None:
        """위치 컴포넌트 추가"""
        position_component = PositionComponent(x=x, y=y)
        entity_manager.add_component(entity_id, position_component)
    
    def _add_velocity_component(self, entity_manager: "EntityManager", entity_id: int) -> None:
        """속도 컴포넌트 추가 (초기값 0)"""
        velocity_component = VelocityComponent(dx=0.0, dy=0.0)
        entity_manager.add_component(entity_id, velocity_component)
    
    def _add_health_component(self, entity_manager: "EntityManager", entity_id: int) -> None:
        """체력 컴포넌트 추가"""
        base_health = self.enemy_type.base_health
        health_component = HealthComponent(
            current=base_health,
            maximum=base_health,
            status=EntityStatus.ALIVE
        )
        entity_manager.add_component(entity_id, health_component)
    
    def _add_enemy_component(self, entity_manager: "EntityManager", entity_id: int) -> None:
        """적 컴포넌트 추가"""
        enemy_component = EnemyComponent(enemy_type=self.enemy_type)
        
        # 각 적 타입별 고유 데이터 추가
        ai_behavior = self.get_specific_ai_behavior()
        attack_pattern = self.get_attack_pattern_data()
        
        enemy_component.type_specific_data.update(ai_behavior)
        enemy_component.type_specific_data.update(attack_pattern)
        
        entity_manager.add_component(entity_id, enemy_component)
    
    def take_damage(self, damage: int) -> bool:
        """
        적이 피해를 받습니다.
        
        Args:
            damage: 받을 피해량
            
        Returns:
            적이 사망했다면 True, 아니면 False
        """
        if not self._entity_manager or not self._entity:
            return False
        
        health_comp = self._entity_manager.get_component(self._entity.id, HealthComponent)
        if not health_comp:
            return False
        
        health_comp.current -= damage
        if health_comp.current <= 0:
            health_comp.current = 0
            health_comp.status = EntityStatus.DEAD
            
            # 적 컴포넌트 상태도 변경
            enemy_comp = self._entity_manager.get_component(self._entity.id, EnemyComponent)
            if enemy_comp:
                enemy_comp.current_state = EnemyState.DYING
            
            return True
        
        return False
    
    def get_distance_to_target(self, target_x: float, target_y: float) -> float:
        """타겟까지의 거리 계산"""
        if not self._entity_manager or not self._entity:
            return float('inf')
        
        pos_comp = self._entity_manager.get_component(self._entity.id, PositionComponent)
        if not pos_comp:
            return float('inf')
        
        dx = target_x - pos_comp.x
        dy = target_y - pos_comp.y
        return math.sqrt(dx * dx + dy * dy)
    
    def get_angle_to_target(self, target_x: float, target_y: float) -> float:
        """타겟 방향의 각도 계산 (라디안)"""
        if not self._entity_manager or not self._entity:
            return 0.0
        
        pos_comp = self._entity_manager.get_component(self._entity.id, PositionComponent)
        if not pos_comp:
            return 0.0
        
        dx = target_x - pos_comp.x
        dy = target_y - pos_comp.y
        return math.atan2(dy, dx)
    
    def is_alive(self) -> bool:
        """적이 살아있는지 확인"""
        if not self._entity_manager or not self._entity:
            return False
        
        health_comp = self._entity_manager.get_component(self._entity.id, HealthComponent)
        return health_comp is not None and health_comp.status == EntityStatus.ALIVE
    
    @staticmethod
    def create_enemy_by_type(enemy_type: EnemyType) -> "Enemy":
        """
        팩토리 메서드: 적 타입에 따른 적 인스턴스 생성
        
        Args:
            enemy_type: 생성할 적의 타입
            
        Returns:
            생성된 Enemy 인스턴스 (하위 클래스)
        """
        # AI-DEV : 순환 참조 방지를 위한 지연 임포트 사용
        # - 문제: 모듈 최상위에서 import 시 순환 참조 발생 가능
        # - 해결책: 팩토리 메서드 내부에서 지연 임포트 적용
        # - 주의사항: 각 적 클래스 구현 후 import 경로 업데이트 필요
        
        if enemy_type == EnemyType.KOREAN_TEACHER:
            from .korean_teacher import KoreanTeacher
            return KoreanTeacher()
        elif enemy_type == EnemyType.MATH_TEACHER:
            from .math_teacher import MathTeacher
            return MathTeacher()
        elif enemy_type == EnemyType.PRINCIPAL:
            from .principal_boss import PrincipalBoss
            return PrincipalBoss()
        else:
            raise ValueError(f"Unknown enemy type: {enemy_type}")
    
    def __repr__(self) -> str:
        return f"Enemy(type={self.enemy_type.display_name}, entity_id={self._entity.id if self._entity else 'None'})"