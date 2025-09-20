import pytest
import time
from unittest.mock import Mock
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../src'))
from src.core.entity_manager import EntityManager
from src.systems.enemy_spawner import EnemySpawner, SpawnWave
from src.components.enums import EnemyType

# AI-DEV : pytest 컬렉션 경고 방지를 위한 Helper 클래스명 변경
# - 문제: Test*로 시작하는 Helper 클래스가 pytest에 의해 테스트 클래스로 수집됨
# - 해결책: Mock* 접두사로 Helper 클래스 명확화
# - 결과: PytestCollectionWarning 제거

class MockEntityManager:
    """테스트용 EntityManager 모의 객체"""
    def __init__(self):
        self.entities = {}
        self.next_id = 1
    
    def create_entity(self):
        from src.core.entity import Entity
        entity = Entity()
        entity.id = self.next_id
        self.next_id += 1
        self.entities[entity.id] = {}
        return entity
    
    def add_component(self, entity_id, component):
        if entity_id not in self.entities:
            self.entities[entity_id] = {}
        self.entities[entity_id][type(component)] = component
    
    def get_component(self, entity_id, component_type):
        return self.entities.get(entity_id, {}).get(component_type)

class TestEnemySpawner:
    def test_스포너_초기화_정상_동작_성공_시나리오(self) -> None:
        """1. 스포너 초기화 시 모든 기본 설정이 정상적으로 동작 (성공 시나리오)
        
        목적: EnemySpawner 클래스의 초기화가 올바르게 수행되는지 검증
        테스트할 범위: __init__ 메서드와 기본 속성 설정
        커버하는 함수 및 데이터: _initialize_wave_configs, _generate_spawn_positions
        기대되는 안정성: 스포너 인스턴스 생성 시 모든 기본값이 올바르게 설정됨
        """
        # Given - EntityManager 모의 객체 준비
        entity_manager = MockEntityManager()
        
        # When - EnemySpawner 초기화
        spawner = EnemySpawner(entity_manager)
        
        # Then - 초기화가 올바르게 완료되어야 함
        assert spawner.entity_manager is entity_manager, "EntityManager가 올바르게 설정되어야 함"
        assert spawner.current_wave == SpawnWave.EARLY_GAME, "초기 웨이브는 EARLY_GAME이어야 함"
        assert spawner.MAX_ENEMIES == 50, "최대 적 수는 50이어야 함"
        assert len(spawner.active_enemies) == 0, "초기 활성 적 수는 0이어야 함"
        assert len(spawner._spawn_positions) == 100, "스폰 위치 풀은 100개여야 함"

    def test_웨이브_전환_시간_기반_정확성_성공_시나리오(self) -> None:
        """2. 시간 기반 웨이브 전환이 정확한 타이밍에 발생 (성공 시나리오)
        
        목적: 게임 진행 시간에 따른 웨이브 전환 로직 정확성 검증
        테스트할 범위: _update_wave 메서드와 웨이브 전환 조건
        커버하는 함수 및 데이터: _transition_to_wave, current_wave 상태 변경
        기대되는 안정성: 정확한 시간에 올바른 웨이브로 전환됨
        """
        # Given - 스포너 초기화 및 시작 시간 조작
        entity_manager = MockEntityManager()
        spawner = EnemySpawner(entity_manager)
        
        # 시간 조작을 위해 game_start_time 변경
        base_time = time.time()
        spawner.game_start_time = base_time
        
        # When & Then - 각 시간대별 웨이브 확인
        
        # 30초 경과 (EARLY_GAME 유지)
        spawner._update_wave(base_time + 30)
        assert spawner.current_wave == SpawnWave.EARLY_GAME, "30초 시점은 초반 웨이브여야 함"
        
        # 90초 경과 (MID_GAME 전환)
        spawner._update_wave(base_time + 90)
        assert spawner.current_wave == SpawnWave.MID_GAME, "90초 시점은 중반 웨이브여야 함"
        
        # 250초 경과 (LATE_GAME 전환)
        spawner._update_wave(base_time + 250)
        assert spawner.current_wave == SpawnWave.LATE_GAME, "250초 시점은 후반 웨이브여야 함"
        
        # 400초 경과 (BOSS_PHASE 전환)
        spawner._update_wave(base_time + 400)
        assert spawner.current_wave == SpawnWave.BOSS_PHASE, "400초 시점은 보스 페이즈여야 함"

    def test_적_타입_선택_가중_랜덤_분포_성공_시나리오(self) -> None:
        """3. 적 타입 선택 시 가중 랜덤 분포가 올바르게 동작 (성공 시나리오)
        
        목적: 웨이브별 적 타입 비율 설정에 따른 랜덤 선택 정확성 검증
        테스트할 범위: _select_enemy_type 메서드와 가중 랜덤 알고리즘
        커버하는 함수 및 데이터: 웨이브별 enemy_ratios 설정과 선택 로직
        기대되는 안정성: 설정된 비율에 근사한 적 타입 분포 생성
        """
        # Given - 중반 웨이브 스포너 설정
        entity_manager = MockEntityManager()
        spawner = EnemySpawner(entity_manager)
        spawner.current_wave = SpawnWave.MID_GAME
        
        # When - 100번 적 타입 선택 실행
        selected_types = []
        for _ in range(100):
            enemy_type = spawner._select_enemy_type()
            selected_types.append(enemy_type)
        
        # Then - 선택 분포가 설정된 비율에 근접해야 함
        korean_count = selected_types.count(EnemyType.KOREAN_TEACHER)
        math_count = selected_types.count(EnemyType.MATH_TEACHER)
        principal_count = selected_types.count(EnemyType.PRINCIPAL)
        
        # 중반 웨이브 설정: 국어 50%, 수학 50%, 보스 0%
        assert 30 <= korean_count <= 70, f"국어선생님 비율이 적절해야 함 (실제: {korean_count}%)"
        assert 30 <= math_count <= 70, f"수학선생님 비율이 적절해야 함 (실제: {math_count}%)"
        assert principal_count == 0, f"중반 웨이브에서는 보스가 나오지 않아야 함 (실제: {principal_count})"

    def test_최대_적_수_제한_성능_보장_성공_시나리오(self) -> None:
        """4. 최대 적 수 제한이 성능 보장을 위해 정확히 동작 (성공 시나리오)
        
        목적: MAX_ENEMIES 제한이 성능 목표(40+ FPS) 달성을 위해 올바르게 작동하는지 검증
        테스트할 범위: _should_spawn_enemy 메서드의 개체 수 제한 로직
        커버하는 함수 및 데이터: active_enemies 리스트 크기와 웨이브별 multiplier
        기대되는 안정성: 설정된 최대 개체 수를 절대 초과하지 않음
        """
        # Given - 스포너 및 다수의 모의 적 준비
        entity_manager = MockEntityManager()
        spawner = EnemySpawner(entity_manager)
        spawner.current_wave = SpawnWave.LATE_GAME  # 최대 개체 수 100% 사용
        
        # 모의 적들을 최대 수까지 추가
        from src.entities.enemy import Enemy
        for i in range(spawner.MAX_ENEMIES):
            mock_enemy = Mock(spec=Enemy)
            mock_enemy.is_alive.return_value = True
            spawner.active_enemies.append(mock_enemy)
        
        # When - 추가 스폰 가능 여부 확인
        current_time = time.time()
        spawner.last_spawn_time = current_time - 10  # 충분한 시간 경과
        
        should_spawn = spawner._should_spawn_enemy(current_time)
        
        # Then - 최대 수에 도달했으므로 스폰하지 않아야 함
        assert should_spawn is False, "최대 적 수에 도달했을 때는 추가 스폰하지 않아야 함"
        assert len(spawner.active_enemies) == spawner.MAX_ENEMIES, "활성 적 수가 최대 수와 일치해야 함"

    def test_죽은_적_정리_메모리_누수_방지_성공_시나리오(self) -> None:
        """5. 죽은 적들의 정리가 메모리 누수 방지를 위해 정확히 동작 (성공 시나리오)
        
        목적: _cleanup_dead_enemies 메서드가 메모리 누수 없이 죽은 적들을 정리하는지 검증
        테스트할 범위: active_enemies 리스트에서 죽은 적 제거 로직
        커버하는 함수 및 데이터: Enemy.is_alive() 상태 확인과 리스트 정리
        기대되는 안정성: 죽은 적들이 완전히 제거되어 메모리 누수 방지
        """
        # Given - 살아있는 적과 죽은 적이 혼재된 상황
        entity_manager = MockEntityManager()
        spawner = EnemySpawner(entity_manager)
        
        # 모의 적들 생성 (일부는 살아있고 일부는 죽음)
        from src.entities.enemy import Enemy
        alive_enemies = []
        dead_enemies = []
        
        for i in range(3):
            alive_enemy = Mock(spec=Enemy)
            alive_enemy.is_alive.return_value = True
            alive_enemies.append(alive_enemy)
            spawner.active_enemies.append(alive_enemy)
        
        for i in range(2):
            dead_enemy = Mock(spec=Enemy) 
            dead_enemy.is_alive.return_value = False
            dead_enemies.append(dead_enemy)
            spawner.active_enemies.append(dead_enemy)
        
        initial_count = len(spawner.active_enemies)
        
        # When - 죽은 적 정리 실행
        spawner._cleanup_dead_enemies()
        
        # Then - 살아있는 적만 남아야 함
        assert len(spawner.active_enemies) == 3, "살아있는 적 3개만 남아야 함"
        assert initial_count == 5, "초기에는 5개 적이 있었어야 함"
        
        # 모든 남은 적이 살아있는지 확인
        for enemy in spawner.active_enemies:
            assert enemy.is_alive() is True, "정리 후 남은 모든 적은 살아있어야 함"

    def test_보스_강제_스폰_디버그_기능_성공_시나리오(self) -> None:
        """6. 보스 강제 스폰 기능이 디버그/테스트 목적으로 정확히 동작 (성공 시나리오)
        
        목적: force_spawn_boss 메서드가 테스트 및 디버그 상황에서 올바르게 작동하는지 검증
        테스트할 범위: 강제 보스 스폰 로직과 적 리스트 관리
        커버하는 함수 및 데이터: EnemyType.PRINCIPAL 생성과 active_enemies 추가
        기대되는 안정성: 언제든지 보스를 안정적으로 강제 생성 가능
        """
        # Given - 정상 초기화된 스포너
        entity_manager = MockEntityManager()
        spawner = EnemySpawner(entity_manager)
        
        initial_count = len(spawner.active_enemies)
        initial_spawned = spawner.total_spawned
        
        # When - 보스 강제 스폰 실행
        boss_enemy = spawner.force_spawn_boss()
        
        # Then - 보스가 정상적으로 생성되어야 함
        assert boss_enemy is not None, "보스가 성공적으로 생성되어야 함"
        assert boss_enemy.enemy_type == EnemyType.PRINCIPAL, "생성된 적이 교장선생님이어야 함"
        assert len(spawner.active_enemies) == initial_count + 1, "활성 적 수가 1 증가해야 함"
        assert spawner.total_spawned == initial_spawned + 1, "총 스폰 수가 1 증가해야 함"

    def test_모든_적_제거_정리_기능_성공_시나리오(self) -> None:
        """7. 모든 적 제거 기능이 정리 목적으로 정확히 동작 (성공 시나리오)
        
        목적: clear_all_enemies 메서드가 디버그/이벤트 상황에서 모든 적을 제거하는지 검증
        테스트할 범위: 전체 적 제거 로직과 엔티티 비활성화
        커버하는 함수 및 데이터: active_enemies 리스트 초기화와 엔티티 active 상태 변경
        기대되는 안정성: 모든 활성 적이 완전히 제거되어 깨끗한 상태 복구
        """
        # Given - 여러 적이 활성화된 상황
        entity_manager = MockEntityManager()
        spawner = EnemySpawner(entity_manager)
        
        # 모의 적들 추가
        from src.entities.enemy import Enemy
        mock_entities = []
        for i in range(5):
            mock_enemy = Mock(spec=Enemy)
            mock_entity = Mock()
            mock_entity.active = True
            mock_enemy.entity = mock_entity
            spawner.active_enemies.append(mock_enemy)
            mock_entities.append(mock_entity)
        
        initial_count = len(spawner.active_enemies)
        
        # When - 모든 적 제거 실행
        removed_count = spawner.clear_all_enemies()
        
        # Then - 모든 적이 제거되고 엔티티가 비활성화되어야 함
        assert removed_count == initial_count, f"제거된 적 수가 초기 적 수와 일치해야 함 (제거: {removed_count}, 초기: {initial_count})"
        assert len(spawner.active_enemies) == 0, "모든 활성 적이 제거되어야 함"
        
        # 모든 엔티티가 비활성화되었는지 확인
        for entity in mock_entities:
            assert entity.active is False, "제거된 적의 엔티티는 비활성 상태여야 함"

    def test_스폰_위치_풀링_성능_최적화_성공_시나리오(self) -> None:
        """8. 스폰 위치 풀링이 성능 최적화를 위해 정확히 동작 (성공 시나리오)
        
        목적: 미리 계산된 스폰 위치 풀이 성능 최적화 목적으로 올바르게 작동하는지 검증
        테스트할 범위: get_next_spawn_position 메서드와 위치 풀 순환 로직
        커버하는 함수 및 데이터: _spawn_positions 리스트와 _position_index 순환
        기대되는 안정성: 위치 풀이 효율적으로 순환되며 예측 가능한 패턴 방지
        """
        # Given - 작은 크기의 위치 풀을 가진 스포너 (테스트용)
        entity_manager = MockEntityManager()
        spawner = EnemySpawner(entity_manager)
        
        # 테스트를 위해 작은 위치 풀 생성 (3개)
        spawner._spawn_positions = [(100, 100), (200, 200), (300, 300)]
        spawner._position_index = 0
        
        # When - 위치 풀보다 많은 횟수의 위치 요청
        positions = []
        for i in range(7):  # 3개 풀을 2회 이상 순환
            pos = spawner.get_next_spawn_position()
            positions.append(pos)
        
        # Then - 위치 풀이 순환되면서 올바르게 동작해야 함
        expected_positions = [
            (100, 100), (200, 200), (300, 300),  # 첫 번째 순환
            (100, 100), (200, 200), (300, 300),  # 두 번째 순환
            (100, 100)  # 세 번째 순환 시작
        ]
        
        assert positions == expected_positions, "위치 풀이 올바른 순서로 순환되어야 함"
        assert spawner._position_index == 1, "인덱스가 올바르게 순환되어야 함"