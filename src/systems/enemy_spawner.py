import time
import random
from typing import TYPE_CHECKING, Optional, List
from enum import IntEnum

from components.enums import EnemyType
from ..entities.enemy import Enemy

if TYPE_CHECKING:
    from core.entity_manager import EntityManager

# AI-NOTE : 2025-01-13 적 스포너 및 생성 시스템 구현
# - 이유: 적 캐릭터들을 화면 밖에서 지속적으로 생성하고 관리하는 게임플레이 요구사항
# - 요구사항: 화면 밖 생성, 최대 개체 수 관리, 생성 주기 조절, 적 타입별 비율 설정
# - 히스토리: 기존 단순한 1초마다 생성에서 복잡한 웨이브 기반 스포너로 발전

class SpawnWave(IntEnum):
    """스포너 웨이브 단계"""
    EARLY_GAME = 0      # 초반: 국어선생님 위주
    MID_GAME = 1        # 중반: 국어+수학선생님 혼합
    LATE_GAME = 2       # 후반: 모든 적 + 보스 등장
    BOSS_PHASE = 3      # 보스 페이즈: 보스 + 소수 졸병
    
    @property
    def display_name(self) -> str:
        return ["초반 웨이브", "중반 웨이브", "후반 웨이브", "보스 페이즈"][self.value]

class EnemySpawner:
    """
    적 캐릭터 스포너 및 생성 관리 시스템
    
    주요 기능:
    - 화면 밖에서 적 생성
    - 최대 개체 수 제한 (성능 관리)
    - 시간에 따른 웨이브 시스템
    - 적 타입별 생성 비율 조절
    - 동적 생성 주기 변화
    
    성능 최적화:
    - 최대 50개 적 제한 (40+ FPS 목표)
    - 생성 위치 사전 계산된 풀 사용
    - 웨이브별 설정 캐싱
    """
    
    # 화면 및 성능 관련 상수
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    MAX_ENEMIES = 50            # 최대 적 수 (성능 한계)
    MIN_SPAWN_INTERVAL = 0.5    # 최소 생성 간격 (초)
    MAX_SPAWN_INTERVAL = 3.0    # 최대 생성 간격 (초)
    
    def __init__(self, entity_manager: "EntityManager"):
        self.entity_manager = entity_manager
        
        # 스포너 상태
        self.current_wave = SpawnWave.EARLY_GAME
        self.last_spawn_time = 0.0
        self.next_spawn_interval = 2.0  # 초기 생성 간격
        self.game_start_time = time.time()
        
        # 적 관리
        self.active_enemies: List[Enemy] = []
        self.total_spawned = 0
        
        # 웨이브별 설정 캐시
        self._wave_configs = self._initialize_wave_configs()
        
        # AI-DEV : 스폰 위치 사전 계산을 위한 위치 풀
        # - 문제: 매번 랜덤 위치 계산은 CPU 사용량 증가
        # - 해결책: 미리 계산된 스폰 위치 풀을 순환 사용
        # - 주의사항: 너무 적은 위치는 패턴이 예측 가능, 너무 많으면 메모리 사용량 증가
        self._spawn_positions = self._generate_spawn_positions(100)
        self._position_index = 0
        
        print(f"EnemySpawner 초기화 완료 - 최대 적 수: {self.MAX_ENEMIES}")
    
    def _initialize_wave_configs(self) -> dict[SpawnWave, dict]:
        """웨이브별 스포너 설정 초기화"""
        
        # AI-NOTE : 웨이브별 게임 밸런스 설정
        # - 이유: 시간에 따른 난이도 증가와 플레이어 성장 곡선 매칭
        # - 요구사항: 초반 쉬움 → 중반 도전적 → 후반 극한 난이도
        # - 히스토리: 단계별 테스트와 플레이어 피드백을 통한 밸런스 조정
        
        return {
            SpawnWave.EARLY_GAME: {
                "duration": 60.0,           # 60초간 지속
                "spawn_interval_range": (2.0, 3.0),  # 2-3초마다 생성
                "enemy_ratios": {
                    EnemyType.KOREAN_TEACHER: 0.8,  # 80% 국어선생님
                    EnemyType.MATH_TEACHER: 0.2,    # 20% 수학선생님
                    EnemyType.PRINCIPAL: 0.0         # 보스 없음
                },
                "max_enemies_multiplier": 0.6,      # 최대 개체 수의 60%
                "description": "국어선생님 위주의 초보자 친화적 웨이브"
            },
            SpawnWave.MID_GAME: {
                "duration": 120.0,          # 120초간 지속
                "spawn_interval_range": (1.5, 2.5),  # 1.5-2.5초마다 생성
                "enemy_ratios": {
                    EnemyType.KOREAN_TEACHER: 0.5,  # 50% 국어선생님
                    EnemyType.MATH_TEACHER: 0.5,    # 50% 수학선생님
                    EnemyType.PRINCIPAL: 0.0         # 보스 없음
                },
                "max_enemies_multiplier": 0.8,      # 최대 개체 수의 80%
                "description": "국어+수학선생님 균형 웨이브, 다양한 패턴 학습"
            },
            SpawnWave.LATE_GAME: {
                "duration": 180.0,          # 180초간 지속
                "spawn_interval_range": (0.8, 2.0),  # 0.8-2초마다 생성 (빠름)
                "enemy_ratios": {
                    EnemyType.KOREAN_TEACHER: 0.3,  # 30% 국어선생님
                    EnemyType.MATH_TEACHER: 0.6,    # 60% 수학선생님 (주력)
                    EnemyType.PRINCIPAL: 0.1         # 10% 교장선생님 등장!
                },
                "max_enemies_multiplier": 1.0,      # 최대 개체 수 100%
                "description": "고난이도 웨이브, 보스 캐릭터 첫 등장"
            },
            SpawnWave.BOSS_PHASE: {
                "duration": float('inf'),   # 무제한 (플레이어가 보스를 잡을 때까지)
                "spawn_interval_range": (3.0, 5.0),  # 3-5초마다 생성 (느림)
                "enemy_ratios": {
                    EnemyType.KOREAN_TEACHER: 0.2,  # 20% 국어선생님 (보조)
                    EnemyType.MATH_TEACHER: 0.3,    # 30% 수학선생님 (보조)
                    EnemyType.PRINCIPAL: 0.5         # 50% 교장선생님 (메인)
                },
                "max_enemies_multiplier": 0.7,      # 보스전이므로 적 수 제한
                "description": "교장선생님 중심의 최종 보스 웨이브"
            }
        }
    
    def _generate_spawn_positions(self, count: int) -> List[tuple[float, float]]:
        """스폰 위치 풀 생성"""
        positions = []
        margin = 50
        
        for _ in range(count):
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            
            if edge == 'top':
                pos = (
                    random.uniform(-margin, self.SCREEN_WIDTH + margin),
                    -margin
                )
            elif edge == 'bottom':
                pos = (
                    random.uniform(-margin, self.SCREEN_WIDTH + margin),
                    self.SCREEN_HEIGHT + margin
                )
            elif edge == 'left':
                pos = (
                    -margin,
                    random.uniform(-margin, self.SCREEN_HEIGHT + margin)
                )
            else:  # right
                pos = (
                    self.SCREEN_WIDTH + margin,
                    random.uniform(-margin, self.SCREEN_HEIGHT + margin)
                )
            
            positions.append(pos)
        
        return positions
    
    def get_next_spawn_position(self) -> tuple[float, float]:
        """다음 스폰 위치 반환 (풀에서 순환)"""
        position = self._spawn_positions[self._position_index]
        self._position_index = (self._position_index + 1) % len(self._spawn_positions)
        return position
    
    def update(self, delta_time: float) -> List[Enemy]:
        """
        스포너 업데이트 및 새로 생성된 적 반환
        
        Args:
            delta_time: 프레임 시간 간격 (초)
            
        Returns:
            이번 프레임에 생성된 적들의 리스트
        """
        current_time = time.time()
        spawned_enemies = []
        
        # 웨이브 업데이트
        self._update_wave(current_time)
        
        # 죽은 적들 제거
        self._cleanup_dead_enemies()
        
        # 스폰 조건 체크 및 실행
        if self._should_spawn_enemy(current_time):
            enemy = self._spawn_single_enemy(current_time)
            if enemy:
                spawned_enemies.append(enemy)
                self.active_enemies.append(enemy)
                self.total_spawned += 1
        
        return spawned_enemies
    
    def _update_wave(self, current_time: float) -> None:
        """현재 웨이브 상태 업데이트"""
        elapsed_time = current_time - self.game_start_time
        
        # AI-DEV : 웨이브 전환 로직의 단순화
        # - 문제: 복잡한 조건문은 버그 발생 가능성 증가
        # - 해결책: 단순한 시간 기반 전환으로 예측 가능한 동작 보장
        # - 주의사항: 나중에 동적 난이도 조절 시 이 로직 확장 필요
        
        if elapsed_time <= 60:
            new_wave = SpawnWave.EARLY_GAME
        elif elapsed_time <= 180:  # 60 + 120
            new_wave = SpawnWave.MID_GAME
        elif elapsed_time <= 360:  # 180 + 180
            new_wave = SpawnWave.LATE_GAME
        else:
            new_wave = SpawnWave.BOSS_PHASE
        
        if new_wave != self.current_wave:
            self._transition_to_wave(new_wave, current_time)
    
    def _transition_to_wave(self, new_wave: SpawnWave, current_time: float) -> None:
        """새로운 웨이브로 전환"""
        old_wave = self.current_wave
        self.current_wave = new_wave
        
        print(f"웨이브 전환: {old_wave.display_name} → {new_wave.display_name}")
        print(f"총 스폰된 적: {self.total_spawned}개")
        
        # 스폰 간격 재계산
        config = self._wave_configs[new_wave]
        min_interval, max_interval = config["spawn_interval_range"]
        self.next_spawn_interval = random.uniform(min_interval, max_interval)
    
    def _cleanup_dead_enemies(self) -> None:
        """죽은 적들을 active_enemies 리스트에서 제거"""
        alive_enemies = []
        removed_count = 0
        
        for enemy in self.active_enemies:
            if enemy.is_alive():
                alive_enemies.append(enemy)
            else:
                removed_count += 1
        
        self.active_enemies = alive_enemies
        
        if removed_count > 0:
            print(f"죽은 적 {removed_count}개 정리 완료, 현재 활성 적: {len(self.active_enemies)}개")
    
    def _should_spawn_enemy(self, current_time: float) -> bool:
        """적을 생성할지 판단"""
        # 시간 간격 체크
        if current_time - self.last_spawn_time < self.next_spawn_interval:
            return False
        
        # 최대 적 수 체크
        config = self._wave_configs[self.current_wave]
        max_enemies = int(self.MAX_ENEMIES * config["max_enemies_multiplier"])
        
        if len(self.active_enemies) >= max_enemies:
            return False
        
        return True
    
    def _spawn_single_enemy(self, current_time: float) -> Optional[Enemy]:
        """단일 적 생성"""
        try:
            # 적 타입 선택 (가중 랜덤)
            enemy_type = self._select_enemy_type()
            
            # 적 인스턴스 생성
            enemy = Enemy.create_enemy_by_type(enemy_type)
            
            # 스폰 위치 선택
            spawn_x, spawn_y = self.get_next_spawn_position()
            
            # ECS 엔티티 생성
            entity = enemy.create_entity(self.entity_manager, spawn_x, spawn_y)
            
            # 스폰 시간 및 간격 업데이트
            self.last_spawn_time = current_time
            self._update_spawn_interval()
            
            print(f"적 생성: {enemy_type.display_name} at ({spawn_x:.1f}, {spawn_y:.1f})")
            return enemy
            
        except Exception as e:
            print(f"적 생성 실패: {e}")
            return None
    
    def _select_enemy_type(self) -> EnemyType:
        """현재 웨이브 설정에 따른 적 타입 선택"""
        config = self._wave_configs[self.current_wave]
        ratios = config["enemy_ratios"]
        
        # AI-DEV : 가중 랜덤 선택 알고리즘
        # - 문제: random.choices()는 Python 3.6+만 지원, 호환성 이슈
        # - 해결책: 수동 가중 랜덤 구현으로 모든 Python 버전 호환
        # - 주의사항: 비율 합계가 1.0이 되도록 설정에서 보장 필요
        
        enemy_types = []
        weights = []
        
        for enemy_type, ratio in ratios.items():
            if ratio > 0:  # 0인 적 타입은 제외
                enemy_types.append(enemy_type)
                weights.append(ratio)
        
        if not enemy_types:
            # 모든 비율이 0인 경우 기본값
            return EnemyType.KOREAN_TEACHER
        
        # 가중 랜덤 선택
        total_weight = sum(weights)
        random_value = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for enemy_type, weight in zip(enemy_types, weights):
            cumulative_weight += weight
            if random_value <= cumulative_weight:
                return enemy_type
        
        # 예외 상황 (부동소수점 오차 등)
        return enemy_types[-1]
    
    def _update_spawn_interval(self) -> None:
        """다음 스폰 간격 업데이트"""
        config = self._wave_configs[self.current_wave]
        min_interval, max_interval = config["spawn_interval_range"]
        self.next_spawn_interval = random.uniform(min_interval, max_interval)
    
    def get_stats(self) -> dict[str, any]:
        """스포너 통계 반환"""
        return {
            "current_wave": self.current_wave.display_name,
            "active_enemies": len(self.active_enemies),
            "total_spawned": self.total_spawned,
            "next_spawn_in": max(0, self.next_spawn_interval - (time.time() - self.last_spawn_time)),
            "enemy_types": [enemy.enemy_type.display_name for enemy in self.active_enemies]
        }
    
    def force_spawn_boss(self) -> Optional[Enemy]:
        """보스 강제 스폰 (테스트/이벤트용)"""
        boss_enemy = Enemy.create_enemy_by_type(EnemyType.PRINCIPAL)
        spawn_x, spawn_y = self.get_next_spawn_position()
        
        try:
            entity = boss_enemy.create_entity(self.entity_manager, spawn_x, spawn_y)
            self.active_enemies.append(boss_enemy)
            self.total_spawned += 1
            print(f"보스 강제 스폰: 교장선생님 at ({spawn_x:.1f}, {spawn_y:.1f})")
            return boss_enemy
        except Exception as e:
            print(f"보스 강제 스폰 실패: {e}")
            return None
    
    def clear_all_enemies(self) -> int:
        """모든 적 제거 (디버그/이벤트용)"""
        removed_count = len(self.active_enemies)
        
        # 모든 적의 엔티티를 비활성화
        for enemy in self.active_enemies:
            if enemy.entity:
                enemy.entity.active = False
        
        self.active_enemies.clear()
        print(f"모든 적 제거: {removed_count}개")
        return removed_count
    
    def __repr__(self) -> str:
        return (f"EnemySpawner(wave={self.current_wave.display_name}, "
                f"active={len(self.active_enemies)}, spawned={self.total_spawned})")