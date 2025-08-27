# 단위 테스트 작성 규칙

## Meta-Principle
pytest 경고 없는 안정적인 테스트 코드 작성과 한국어 기반 ECS 게임 아키텍처 테스트 패턴 준수

## Constitutional Constraints
1. MUST: Helper/Mock 클래스는 `Test*` 접두사 사용 금지
2. MUST NOT: pytest가 수집할 수 있는 패턴으로 Helper 클래스 명명
3. IF-THEN: 테스트 Helper 클래스 작성 시 AI-DEV 주석으로 pytest 경고 방지 이유 명시

## Execution Procedure

### Step 1: 클래스 유형 판단
```python
def determine_class_type(class_purpose: str) -> str:
    if class_purpose == "test_class":
        return "Test*"  # 실제 테스트 클래스만 Test* 사용
    elif class_purpose in ["helper", "mock", "fake", "stub"]:
        return "Mock*"  # Helper 클래스는 Mock* 접두사 사용
    else:
        return "pytest 수집 대상 여부를 확인하세요"
```

### Step 2: 테스트 작성 패턴 적용
```python
def write_korean_test(test_name: str, scenario_type: str) -> str:
    return f"""def test_{test_name}_{scenario_type}_시나리오(self) -> None:
        \"\"\"N. {test_name} 검증 ({scenario_type} 시나리오)
        
        목적: 구체적인 테스트 목표
        테스트할 범위: 대상 메서드/기능
        커버하는 함수 및 데이터: 실제 호출 메서드
        기대되는 안정성: 보장되는 안정성
        \"\"\"
        # Given - 테스트 환경 설정
        
        # When - 테스트 실행
        
        # Then - 결과 검증
        assert result is not None, "한국어 검증 메시지\""""
```

### Step 3: AI-DEV 주석 추가
```python
def add_pytest_prevention_comment() -> str:
    return """# AI-DEV : pytest 컬렉션 경고 방지를 위한 Helper 클래스명 변경
# - 문제: Test*로 시작하는 Helper 클래스가 pytest에 의해 테스트 클래스로 수집됨
# - 해결책: Mock* 접두사로 Helper 클래스 명확화
# - 결과: PytestCollectionWarning 제거"""
```

## Few-Shot Examples

### Example 1: 올바른 Helper 클래스 작성
**Input**: 테스트용 Position 컴포넌트 Helper 클래스 필요
**Output**: 
```python
# AI-DEV : pytest 컬렉션 경고 방지를 위한 Helper 클래스명 변경
# - 문제: Test*로 시작하는 Helper 클래스가 pytest에 의해 테스트 클래스로 수집됨
# - 해결책: Mock* 접두사로 Helper 클래스 명확화
# - 결과: PytestCollectionWarning 제거
@dataclass
class MockPositionComponent(Component):
    """Mock position component for testing."""
    x: float = 0.0
    y: float = 0.0
```
**Reasoning**: Helper 클래스이므로 Mock* 접두사를 사용하고 AI-DEV 주석으로 이유 명시

### Example 2: 한국어 테스트 메서드 작성
**Input**: EntityManager의 엔티티 생성 기능 테스트
**Output**:
```python
def test_엔티티_생성_고유ID_할당_정상_동작_성공_시나리오(self) -> None:
    """1. 엔티티 생성 시 고유 ID 할당이 정상적으로 동작 (성공 시나리오)
    
    목적: EntityManager의 create_entity() 메서드가 고유 ID를 할당하는지 검증
    테스트할 범위: create_entity() 메서드와 entity.entity_id 속성
    커버하는 함수 및 데이터: Entity.create(), WeakValueDictionary 저장
    기대되는 안정성: 중복 없는 고유 ID 생성과 메모리 안전 관리 보장
    """
    # Given - 엔티티 매니저 초기화
    entity_manager = EntityManager()
    
    # When - 새로운 엔티티 생성
    created_entity = entity_manager.create_entity()
    
    # Then - 생성된 엔티티가 올바른 속성을 가져야 함
    assert created_entity.entity_id is not None, "생성된 엔티티는 고유 ID를 가져야 함"
    assert created_entity.active is True, "새로 생성된 엔티티는 활성 상태여야 함"
```
**Reasoning**: 한국어 테스트 명명법과 5단계 docstring을 사용한 ECS 패턴 테스트

## pytest 경고 방지 핵심 규칙

### 🚨 클래스 네이밍 패턴 (Critical)

**pytest가 테스트로 인식하는 패턴**:
- 클래스명: `Test*` 
- 함수명: `test_*`
- 파일명: `test_*.py` 또는 `*_test.py`

**Helper 클래스가 피해야 할 패턴**:
- `Test`로 시작하는 클래스명 + `__init__` 메서드
- pytest가 수집할 수 있는 위치의 테스트 패턴

### ✅ 권장 Helper 클래스 접두사

```python
# 올바른 Helper 클래스 명명
class MockPositionComponent(Component):     # ✅ Mock: 모의 객체
class FakeMovementSystem(System):           # ✅ Fake: 가짜 구현
class DummyHealthComponent(Component):      # ✅ Dummy: 더미 데이터
class StubRenderSystem(System):             # ✅ Stub: 스텁 구현
class TestDataBuilder:                      # ✅ Builder 패턴
class ComponentFactory:                     # ✅ Factory 패턴
```

### ❌ 피해야 할 패턴

```python
# 잘못된 예 - pytest가 테스트 클래스로 오인
class TestPositionComponent(Component):     # ❌ pytest 수집 대상
class TestMovementSystem(System):           # ❌ pytest 수집 대상
class TestDataHelper:                       # ❌ pytest 수집 대상
```

## 파일 구조 권장사항

### Helper 클래스 분리 패턴
```python
# tests/helpers/components.py - Helper 클래스들만 분리
@dataclass
class MockPositionComponent(Component):
    x: float = 0.0
    y: float = 0.0

@dataclass
class MockHealthComponent(Component):
    current: int = 100
    maximum: int = 100

# tests/test_entity_manager.py - 실제 테스트
from tests.helpers.components import MockPositionComponent

class TestEntityManager:  # 실제 테스트 클래스만 Test* 사용
    def test_엔티티_생성_성공_시나리오(self):
        pass
```

## 한국어 테스트 명명 규칙

### 메서드 명명 패턴
```python
def test_{대상기능}_{상황설명}_{예상결과}_{시나리오타입}_시나리오(self) -> None:
    pass

# 예시들
def test_엔티티_생성_고유ID_할당_성공_시나리오(self) -> None:
def test_컴포넌트_추가_중복_추가_실패_시나리오(self) -> None:
def test_시스템_업데이트_대량_엔티티_처리_성능_시나리오(self) -> None:
```

### Docstring 5단계 구조 (필수)
```python
def test_example_시나리오(self) -> None:
    """N. 테스트 시나리오 명 (성공/실패/성능 시나리오)
    
    목적: 구체적인 테스트 목표 설명
    테스트할 범위: 대상 메서드나 기능의 범위
    커버하는 함수 및 데이터: 실제로 호출되는 메서드와 검증할 데이터
    기대되는 안정성: 테스트 통과 시 보장되는 안정성
    [실패 조건]: 실패 시나리오인 경우만 추가
    """
```

## ECS 아키텍처 특화 테스트 패턴

### Entity 테스트 패턴
```python
def test_엔티티_생명주기_관리_정상_동작_성공_시나리오(self) -> None:
    """엔티티 생성부터 삭제까지 생명주기 관리 검증"""
    # Given - 엔티티 매니저 초기화
    manager = EntityManager()
    
    # When - 엔티티 생성 및 삭제
    entity = manager.create_entity()
    entity_id = entity.entity_id
    manager.destroy_entity(entity)
    
    # Then - 생명주기가 올바르게 관리되어야 함
    assert entity.active is False, "삭제된 엔티티는 비활성 상태여야 함"
    assert manager.get_entity(entity_id) is None, "삭제된 엔티티는 조회되지 않아야 함"
```

### Component 테스트 패턴
```python
def test_컴포넌트_데이터_무결성_검증_성공_시나리오(self) -> None:
    """컴포넌트 데이터의 타입 안전성과 무결성 검증"""
    # Given - 컴포넌트 데이터 준비
    component = MockHealthComponent(current=80, maximum=100)
    
    # When - 데이터 접근 및 수정
    component.current -= 20
    
    # Then - 데이터 무결성이 유지되어야 함
    assert component.current == 60, "체력 감소가 정확히 적용되어야 함"
    assert component.current <= component.maximum, "현재 체력은 최대 체력을 초과할 수 없음"
```

### System 테스트 패턴
```python
def test_시스템_엔티티_처리_순서_보장_성공_시나리오(self) -> None:
    """시스템이 엔티티들을 올바른 순서로 처리하는지 검증"""
    # Given - 시스템과 다중 엔티티 준비
    system = MockMovementSystem()
    entities = [create_test_entity() for _ in range(5)]
    
    # When - 시스템 업데이트 실행
    system.update(entities, delta_time=0.016)  # 60 FPS
    
    # Then - 모든 엔티티가 처리되어야 함
    assert system.processed_count == 5, "모든 엔티티가 처리되어야 함"
```

## 메모리 관리 및 성능 테스트

### 메모리 누수 방지 테스트
```python
def test_대량_엔티티_생성_삭제_메모리_누수_없음_성능_시나리오(self) -> None:
    """40+ FPS 유지를 위한 메모리 누수 방지 검증"""
    # Given - 메모리 사용량 측정 준비
    manager = EntityManager()
    initial_count = len(manager)
    
    # When - 1000개 엔티티 생성 후 즉시 삭제
    entities = [manager.create_entity() for _ in range(1000)]
    for entity in entities:
        manager.destroy_entity(entity)
    
    # Then - 메모리가 정상적으로 정리되어야 함
    assert len(manager) == initial_count, "모든 엔티티가 정리되어야 함"
```

## Validation Metrics
- **경고 제거율**: 100% (모든 pytest 경고 제거)
- **한국어 명명 준수율**: 95% 이상
- **AI-DEV 주석 적용률**: Helper 클래스 100%
- **ECS 패턴 준수율**: 게임 아키텍처 관련 테스트 90% 이상

## Anti-Pattern Detection

**자주하는 실수들**:
- Helper 클래스에 Test* 접두사 사용
- 영어 테스트 메서드명 사용  
- Docstring 5단계 구조 누락
- Given-When-Then 구조 무시
- 한국어 검증 메시지 누락

**개선 방안**:
- Helper 클래스 작성 전 "이것이 pytest 수집 대상인가?" 자문
- 테스트 메서드명에 한국어와 "_시나리오" 접미사 필수 사용
- 모든 테스트에 5단계 docstring 구조 적용
- AI-DEV 주석으로 기술적 결정 사항 명확히 기록

## refactor-PRD.md Architecture Testing Patterns

### SharedEventQueue Testing Pattern
```python
def test_공유이벤트큐_프로듀서_컨슈머_직접연결_성공_시나리오(self) -> None:
    """1. SharedEventQueue를 통한 Producer-Consumer 직접 연결 검증 (성공 시나리오)
    
    목적: 기존 EventBus 대신 SharedEventQueue의 직접 연결 방식이 올바르게 동작하는지 검증
    테스트할 범위: SharedEventQueue의 produce, consume 메서드와 타입 안전성
    커버하는 함수 및 데이터: WeaponAttackEvent의 생성과 소비 과정
    기대되는 안정성: 중간 등록/전송 단계 제거로 성능 향상과 이벤트 손실 방지 보장
    """
    # Given - SharedEventQueue 직접 생성
    shared_queue = SharedEventQueue[MockWeaponAttackEvent]()
    
    # When - Producer와 Consumer가 동일한 큐 공유
    producer = shared_queue.get_producer()
    consumer = shared_queue.get_consumer()
    
    test_event = MockWeaponAttackEvent(weapon_id="weapon_001", damage=50)
    producer.produce(test_event)
    
    # Then - 직접 연결로 이벤트 전달 확인
    consumed_event = consumer.consume()
    assert consumed_event is not None, "직접 연결된 이벤트가 소비되어야 함"
    assert consumed_event.weapon_id == "weapon_001", "이벤트 데이터가 보존되어야 함"
```

### TDD 6단계 프로세스 Testing
```python
def test_TDD_6단계_프로세스_인터페이스_우선_개발_성공_시나리오(self) -> None:
    """2. TDD 6단계 프로세스의 인터페이스 우선 개발 방식 검증 (성공 시나리오)
    
    목적: Phase 4에서 적용되는 TDD 6단계 프로세스가 올바르게 동작하는지 검증
    테스트할 범위: 1)인터페이스 구현 → 2)기존 테스트 분석 → 3)사용자 인터뷰 → 4)테스트 구현 → 5)리팩토링 → 6)품질 검증
    커버하는 함수 및 데이터: IWeaponSystem 인터페이스와 구현체 간 계약 준수
    기대되는 안정성: 인터페이스 우선 개발로 구현체 교체 가능성과 테스트 격리 보장
    """
    # Given - 인터페이스 우선 정의 (1단계)
    weapon_system_interface: IWeaponSystem = MockWeaponSystem()
    
    # When - 인터페이스 계약 기반 테스트 (4단계)
    result = weapon_system_interface.initialize()
    system_name = weapon_system_interface.get_system_name()
    priority = weapon_system_interface.get_priority()
    
    # Then - 인터페이스 계약 준수 확인 (6단계)
    assert isinstance(result, bool), "initialize() 반환값은 bool 타입이어야 함"
    assert isinstance(system_name, str), "get_system_name() 반환값은 str 타입이어야 함"
    assert isinstance(priority, int), "get_priority() 반환값은 int 타입이어야 함"
```

### Phase-Based Refactoring Testing
```python
def test_영향도_기반_리팩토링_순서_의존성_위반_감지_실패_시나리오(self) -> None:
    """3. 영향도 기반 리팩토링 순서에서 의존성 위반 감지 (실패 시나리오)
    
    목적: Entity → Component → System → Manager/Event/Strategy 순서 위반 시 적절한 오류 발생
    테스트할 범위: Phase별 의존성 규칙과 금지된 패턴 감지
    커버하는 함수 및 데이터: Manager가 System 직접 호출, EntityManager 특수 생성 로직
    기대되는 안정성: 아키텍처 규칙 위반 시 명확한 오류 메시지와 함께 실패
    실패 조건: Manager → System 직접 호출, EntityManager 순수 CRUD 위반
    """
    # Given - 금지된 의존성 패턴들
    enemy_manager = MockEnemyManager()
    weapon_system = MockWeaponSystem()
    
    # When & Then - 의존성 위반 시 예외 발생 확인
    with pytest.raises(ArchitectureViolationError):
        # Manager가 System 직접 호출 시도 (금지됨)
        enemy_manager.call_system_directly(weapon_system)
    
    with pytest.raises(PureCRUDViolationError):
        # EntityManager가 특수 생성 로직 시도 (금지됨)
        entity_manager = MockEntityManager()
        entity_manager.create_specialized_enemy()  # 순수 CRUD 위반
```

## v0.4 Architecture Testing Patterns (Legacy)

### Interface Contract Testing
```python
def test_매니저_인터페이스_계약_준수_성공_시나리오(self) -> None:
    """1. 매니저 클래스가 인터페이스 계약을 올바르게 구현 (성공 시나리오)
    
    목적: IEnemyManager 인터페이스의 모든 메서드가 올바르게 구현되었는지 검증
    테스트할 범위: EnemyManager 클래스의 create_enemy, update_enemy_stats 메서드
    커버하는 함수 및 데이터: 인터페이스 메서드 시그니처와 반환 타입 검증
    기대되는 안정성: 인터페이스 계약 위반 없이 안전한 매니저 교체 보장
    """
    # Given - 매니저 구현체 생성
    entity_manager = MockEntityManager()
    enemy_manager: IEnemyManager = EnemyManager(entity_manager)
    
    # When - DTO를 사용한 적 생성
    enemy_dto = MockEnemyCreateDTO(
        spawn_position=(100.0, 100.0),
        enemy_type=EnemyType.BASIC,
        difficulty_scale=1.0,
        base_health=50,
        base_speed=100.0
    )
    
    # Then - 인터페이스 계약 준수 확인
    enemy_id = enemy_manager.create_enemy(enemy_dto)
    assert isinstance(enemy_id, str), "적 ID는 문자열 타입이어야 함"
    assert len(enemy_id) > 0, "적 ID는 빈 문자열이 아니어야 함"
```

### DTO Validation Testing
```python
def test_DTO_데이터_유효성_검증_실패_시나리오(self) -> None:
    """2. DTO 데이터 유효성 검증이 올바르게 동작 (실패 시나리오)
    
    목적: EnemyCreateDTO의 validate() 메서드가 잘못된 데이터를 올바르게 감지
    테스트할 범위: validate() 메서드의 모든 검증 규칙
    커버하는 함수 및 데이터: base_health, base_speed, difficulty_scale 검증
    기대되는 안정성: 잘못된 데이터로 인한 게임 오류 방지
    실패 조건: 음수 체력, 음수 속도, 음수 난이도 배율 입력 시
    """
    # Given - 잘못된 데이터를 가진 DTO
    invalid_dto = EnemyCreateDTO(
        spawn_position=(0.0, 0.0),
        enemy_type=EnemyType.BASIC,
        difficulty_scale=-1.0,  # 잘못된 음수 값
        base_health=-10,        # 잘못된 음수 값
        base_speed=-5.0         # 잘못된 음수 값
    )
    
    # When - 유효성 검증 실행
    is_valid = invalid_dto.validate()
    
    # Then - 검증 실패 확인
    assert is_valid is False, "잘못된 데이터는 검증에 실패해야 함"
```

### Event System Testing
```python
def test_이벤트_터널_매니저_프로듀서_컨슈머_연결_성공_시나리오(self) -> None:
    """3. 이벤트 터널 매니저의 Producer-Consumer 연결 검증 (성공 시나리오)
    
    목적: EventTunnelManager가 Producer와 Consumer를 올바르게 연결하는지 검증
    테스트할 범위: get_producer, get_consumer 메서드와 SharedEventQueue
    커버하는 함수 및 데이터: EnemyDeathEvent의 생성과 소비 과정
    기대되는 안정성: 이벤트 손실 없이 안전한 이벤트 전달 보장
    """
    # Given - 이벤트 터널 매니저 초기화
    tunnel_manager = EventTunnelManager()
    
    # When - Producer와 Consumer 획득
    producer = tunnel_manager.get_producer(MockEnemyDeathEvent)
    consumer = tunnel_manager.get_consumer(MockEnemyDeathEvent)
    
    test_event = MockEnemyDeathEvent(entity_id="enemy_001", position=(50.0, 75.0))
    producer.produce(test_event)
    
    # Then - 이벤트가 올바르게 전달되어야 함
    consumed_event = consumer.consume()
    assert consumed_event is not None, "생성된 이벤트가 소비되어야 함"
    assert consumed_event.entity_id == "enemy_001", "이벤트 데이터가 보존되어야 함"
```

### System Priority Testing
```python
def test_시스템_우선순위_실행_순서_보장_성공_시나리오(self) -> None:
    """4. SystemOrchestrator의 시스템 우선순위 기반 실행 순서 보장 (성공 시나리오)
    
    목적: 시스템들이 설정된 우선순위에 따라 올바른 순서로 실행되는지 검증
    테스트할 범위: SystemOrchestrator의 update_all_systems 메서드
    커버하는 함수 및 데이터: SystemPriority enum과 실행 순서 추적
    기대되는 안정성: 게임 로직의 일관된 실행 순서 보장
    """
    # Given - 다른 우선순위를 가진 시스템들
    orchestrator = SystemOrchestrator()
    
    high_priority_system = MockSystem("HighPriority", SystemPriority.HIGH)
    critical_priority_system = MockSystem("Critical", SystemPriority.CRITICAL)
    normal_priority_system = MockSystem("Normal", SystemPriority.NORMAL)
    
    # 의도적으로 순서 섞어서 등록
    orchestrator.register_system(normal_priority_system)
    orchestrator.register_system(critical_priority_system)
    orchestrator.register_system(high_priority_system)
    
    # When - 모든 시스템 업데이트
    execution_log = []
    orchestrator.update_all_systems(0.016, execution_log)
    
    # Then - 우선순위 순서대로 실행되어야 함
    assert execution_log[0] == "Critical", "CRITICAL 우선순위가 먼저 실행되어야 함"
    assert execution_log[1] == "HighPriority", "HIGH 우선순위가 두 번째로 실행되어야 함"
    assert execution_log[2] == "Normal", "NORMAL 우선순위가 마지막에 실행되어야 함"
```

### Strategy Pattern Testing
```python
def test_전략_패턴_런타임_교체_동작_성공_시나리오(self) -> None:
    """5. 전략 패턴의 런타임 전략 교체가 올바르게 동작 (성공 시나리오)
    
    목적: WeaponSystem에서 IAttackStrategy를 런타임에 교체할 수 있는지 검증
    테스트할 범위: set_attack_strategy 메서드와 전략 실행
    커버하는 함수 및 데이터: DirectAttackStrategy, AreaAttackStrategy 교체
    기대되는 안정성: 전략 변경 시에도 안전한 공격 동작 보장
    """
    # Given - 무기 시스템과 전략들
    weapon_system = MockWeaponSystem()
    direct_strategy = MockDirectAttackStrategy()
    area_strategy = MockAreaAttackStrategy()
    
    # When - 전략 교체 및 실행
    weapon_system.set_attack_strategy(direct_strategy)
    direct_result = weapon_system.execute_attack("weapon_001", ["enemy_001"])
    
    weapon_system.set_attack_strategy(area_strategy)
    area_result = weapon_system.execute_attack("weapon_001", ["enemy_001", "enemy_002"])
    
    # Then - 각 전략에 맞는 결과 확인
    assert direct_result.strategy_name == "Direct", "Direct 전략이 실행되어야 함"
    assert area_result.strategy_name == "Area", "Area 전략이 실행되어야 함"
    assert len(area_result.targets) > len(direct_result.targets), "Area 전략이 더 많은 대상을 처리해야 함"
```

## Testing Commands (Conda Environment - as-game)

### Core Testing Commands
```bash
# 전체 테스트 실행
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/ -v

# 특정 테스트 파일
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_entity_manager.py -v

# 특정 테스트 클래스
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_entity_manager.py::TestEntityManager -v

# 특정 테스트 메서드
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_entity_manager.py::TestEntityManager::test_엔티티_생성_성공_시나리오 -v

# 커버리지와 함께 실행
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/ --cov=src --cov-report=term-missing -v

# 코드 품질 검증 (ruff + mypy)
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff check --fix .
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff format .
/opt/homebrew/anaconda3/envs/as-game/bin/python -m mypy src/
```

### Architecture Pattern Testing
```bash
# Manager interface tests
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_*_manager.py -v

# System tests
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_*_system.py -v

# DTO validation tests
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_dto_validation.py -v

# Event system tests
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/test_event_*.py -v
```

## TDD Support for Interface-Based Development

### Interface-First TDD Workflow
1. **인터페이스 정의**: ABC로 계약 정의
2. **테스트 작성**: 인터페이스 계약 기반 테스트
3. **Mock 구현**: 테스트용 Mock 구현체
4. **실제 구현**: 인터페이스를 만족하는 실제 구현
5. **통합 테스트**: 실제 구현체와 Mock 교체 테스트

### Interface Contract Test Template
```python
def test_인터페이스_계약_준수_검증_성공_시나리오(self) -> None:
    """인터페이스 계약을 모든 구현체가 준수하는지 검증"""
    # Given - 모든 구현체들
    implementations = [
        ConcreteImplementationA(),
        ConcreteImplementationB(),
        MockImplementation()
    ]
    
    # When & Then - 각 구현체가 계약 준수
    for impl in implementations:
        assert hasattr(impl, 'required_method'), "필수 메서드가 존재해야 함"
        result = impl.required_method(test_data)
        assert isinstance(result, expected_type), "반환 타입이 계약과 일치해야 함"
```

## 프로젝트별 추가 규칙 (AfterSchoolSurvivors refactor-PRD.md)

### Component Required Testing Integration
```python
# AI-NOTE : 2025-08-27 Component 서브클래스 필수 테스트 검증 요구사항 적용
# - 이유: src/core/component.py에 정의된 5개 핵심 함수 테스트 필수
# - 요구사항: 모든 Component 서브클래스는 REQUIRED_TEST_FUNCTIONS 준수
# - 히스토리: ECS 아키텍처의 데이터 무결성과 시스템 안정성 보장을 위한 강화

def test_component_validation_success_scenarios(self) -> None:
    """유효한 모든 필드 조합에서 True 반환 검증 (필수 테스트)"""
    # Component.REQUIRED_TEST_FUNCTIONS[0] 준수
    pass

def test_component_validation_failure_scenarios(self) -> None: 
    """필수 필드 누락/잘못된 타입에서 False 반환 검증 (필수 테스트)"""
    # Component.REQUIRED_TEST_FUNCTIONS[1] 준수
    pass

def test_component_serialization_roundtrip(self) -> None:
    """component_type 필드가 정확한 클래스명으로 설정되는지 검증 (필수 테스트)"""
    # Component.REQUIRED_TEST_FUNCTIONS[2] 준수
    pass

def test_component_deserialization_error_handling(self) -> None:
    """잘못된 타입의 필드값에서 적절한 예외 발생 검증 (필수 테스트)"""
    # Component.REQUIRED_TEST_FUNCTIONS[3] 준수
    pass

def test_component_utility_methods_consistency(self) -> None:
    """copy()와 shallow_copy()가 독립적인 인스턴스 생성하는지 검증 (필수 테스트)"""
    # Component.REQUIRED_TEST_FUNCTIONS[4] 준수
    pass
```

### SharedEventQueue-based Producer-Consumer Architecture Testing
- SharedEventQueue의 직접 연결 방식과 타입 안전성 검증
- EventTunnelManager 제거 후 Producer/Consumer 직접 통신 테스트
- 중간 등록/전송 단계 제거로 인한 성능 향상 확인
- Producer와 Consumer 간 SharedEventQueue 공유 검증

### Manager Interface Hierarchy Testing  
- 특화된 Manager 인터페이스(IEnemyManager, IWeaponManager 등) 계약 검증
- DTO 기반 타입 안전한 데이터 전송 테스트
- 정적 팩토리 메서드를 통한 구현체 숨김 검증
- 의존성 주입을 통한 Manager 교체 가능성 확인

### Strategy Pattern System Testing
- 런타임 전략 교체 기능 검증
- IAttackStrategy, ISpawnStrategy 등 전략 인터페이스 테스트
- System 내부에 Strategy를 포함하는 구조 검증
- Manager + Strategy + EventProducer 조합 동작 테스트
- 전략 변경 시 시스템 안정성 확인

### Forbidden Dependency Testing (refactor-PRD.md)
```python
def test_아키텍처_의존성_규칙_위반_감지_실패_시나리오(self) -> None:
    """refactor-PRD.md의 아키텍처 의존성 규칙 위반 시 적절한 오류 발생 확인"""
    # 금지된 의존성 패턴들을 테스트로 검증
    # Manager → System 직접 호출 감지 (Phase 4 규칙)
    # EntityManager 순수 CRUD 위반 감지 (특수 생성/관리 로직 금지)
    # System이 EntityManager 직접 접근 감지 (Manager를 통한 접근 강제)
    # 영향도 기반 순서 위반 감지 (Entity → Component → System → Manager)
    pass

def test_순수_EntityManager_CRUD_위반_감지_실패_시나리오(self) -> None:
    """순수 EntityManager CRUD 규칙 위반 시 오류 발생 확인"""
    # EntityManager는 순수 CRUD 기능만 제공
    # 특수 생성/관리 로직은 별도 Manager에서 처리
    # 다른 Manager가 EntityManager를 활용하는 구조 검증
    pass
```