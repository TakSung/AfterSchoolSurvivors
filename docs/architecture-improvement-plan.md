# 방과후생존 게임 아키텍처 개선 계획서

> **작성일**: 2025-08-06  
> **작성자**: 시니어 Python 게임 아키텍트  
> **목적**: TaskMaster 태스크 최적화 및 현대적 게임 아키텍처 적용

---

## 🎯 현재 상황 분석

### 문제점 식별
현재 TaskMaster에서 생성된 "방과후생존" 게임 개발 태스크들을 분석한 결과, 다음과 같은 아키텍처적 개선점들이 발견되었습니다:

#### 1. 의존성 문서와 태스크 간 불일치
- **문제**: `docs/game-dependencies.md`에서 제안한 현대적 라이브러리 스택(NumPy, Numba, Pymunk 등)이 태스크에 반영되지 않음
- **영향**: 성능 최적화 기회 손실, 40+ FPS 목표 달성 어려움

#### 2. 성능 최적화 전략 부족
- **문제**: 수백 개 객체 동시 처리를 위한 구체적 아키텍처 패턴 미정의
- **영향**: 게임 후반부 프레임 드랍, 사용자 경험 저하

#### 3. 확장성 고려 부족
- **문제**: ECS, FSM 등 복잡한 시스템 관리를 위한 아키텍처 설계 없음
- **영향**: 코드 복잡도 증가, 유지보수성 저하

#### 4. 시스템 모듈화 부족
- **문제**: 시스템 간 의존성과 인터페이스가 명확하지 않음
- **영향**: 테스트 어려움, 병렬 개발 제약

---

## 🏗️ 아키텍처 패턴 적용 계획

### 1. ECS (Entity-Component-System) 프레임워크

#### 적용 근거
- ✅ **대용량 객체 관리**: 수백 개의 적/투사체 동시 처리 필요
- ✅ **컴포넌트 조합 다양성**: 아이템 시너지로 인한 복잡한 상태 조합
- ✅ **성능 최적화**: 데이터 지향 설계로 캐시 효율성 향상
- ✅ **시스템 분리**: 각 시스템의 독립적 개발 및 테스트 가능

#### 구현 전략
```python
# 핵심 ECS 구조 예시
@dataclass
class HealthComponent:
    current: int
    maximum: int
    regeneration_rate: float = 0.0

@dataclass
class MovementComponent:
    velocity: Vector2
    max_speed: float
    acceleration: float

@dataclass
class WeaponComponent:
    damage: int
    attack_speed: float
    range: float
    projectile_type: str

class MovementSystem:
    def update(self, entities_with_movement, delta_time):
        # 벡터화된 이동 처리로 성능 최적화
        for entity_id, (pos, movement) in entities_with_movement:
            # NumPy를 활용한 고속 벡터 연산
            pass

class CombatSystem:
    def update(self, entities_with_weapons, targets, delta_time):
        # 공간 분할을 통한 효율적 충돌 감지
        pass
```

### 2. FSM + Behavior Tree 기반 AI 시스템

#### 적용 근거
- ✅ **복합 AI 패턴**: 교장선생님 등 보스급 적의 복잡한 행동
- ✅ **상태 전이 관리**: 난이도에 따른 동적 AI 행동 변화
- ✅ **디버깅 가능성**: 명확한 상태 추적 및 AI 행동 예측

#### 구현 전략
```python
class AIStateMachine:
    """계층적 상태 머신 구현"""
    
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.state_stack = [initial_state]
        
    def push_state(self, new_state):
        """상태 스택 기반 계층적 상태 관리"""
        self.state_stack.append(new_state)
        self.current_state = new_state
        
    def pop_state(self):
        """이전 상태로 복귀"""
        if len(self.state_stack) > 1:
            self.state_stack.pop()
            self.current_state = self.state_stack[-1]

class PrincipalAI:
    """교장선생님 보스 AI"""
    states = {
        'patrol': PatrolState(),
        'chase': ChaseState(), 
        'attack': AttackState(),
        'rage': RageState(),  # 체력 50% 이하 시
        'retreat': RetreatState()
    }
```

### 3. Event-Driven Architecture

#### 적용 근거
- ✅ **아이템 시너지**: 조건부 효과 처리를 위한 이벤트 시스템
- ✅ **시스템 분리**: 느슨한 결합으로 확장성 확보
- ✅ **트리거 시스템**: 레벨업, 함정 등 다양한 게임 이벤트 처리

#### 구현 전략
```python
class GameEventBus:
    """중앙 집중식 이벤트 관리"""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.event_queue = deque()
        
    def subscribe(self, event_type: str, callback: Callable):
        self.subscribers[event_type].append(callback)
        
    def publish(self, event_type: str, data: dict):
        self.event_queue.append((event_type, data))
        
    def process_events(self):
        """프레임당 이벤트 처리"""
        while self.event_queue:
            event_type, data = self.event_queue.popleft()
            for callback in self.subscribers[event_type]:
                callback(data)

class SynergyManager:
    """아이템 시너지 규칙 엔진"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.active_synergies = set()
        self.synergy_rules = self._load_synergy_rules()
        
        # 이벤트 구독
        event_bus.subscribe('item_acquired', self.check_synergies)
        event_bus.subscribe('item_removed', self.check_synergies)
```

---

## ⚡ 성능 최적화 전략

### 1. 핵심 성능 목표
- **목표 FPS**: 40+ FPS 안정적 유지
- **동시 객체**: 적 200개 + 투사체 300개 + 파티클 100개
- **메모리 사용량**: 최적화를 통한 GC 압력 최소화

### 2. 병목점 분석 및 해결책

#### 렌더링 최적화
```python
class OptimizedRenderer:
    """더티 렌더링 + 스프라이트 배칭"""
    
    def __init__(self):
        self.dirty_rects = []
        self.sprite_groups = {
            'static': pygame.sprite.Group(),
            'dynamic': pygame.sprite.Group(),
            'ui': pygame.sprite.Group()
        }
        
    def render_frame(self, screen):
        # 변경된 영역만 렌더링
        if self.dirty_rects:
            pygame.display.update(self.dirty_rects)
            self.dirty_rects.clear()
```

#### 공간 분할 기반 충돌 감지
```python
class QuadTree:
    """공간 분할을 통한 O(n log n) 충돌 감지"""
    
    def __init__(self, boundary, max_objects=10, max_levels=5):
        self.boundary = boundary
        self.max_objects = max_objects
        self.max_levels = max_levels
        self.objects = []
        self.nodes = [None] * 4
        
    def insert(self, game_object):
        """객체를 적절한 노드에 삽입"""
        pass
        
    def retrieve(self, return_objects, game_object):
        """충돌 가능한 객체들만 반환"""
        pass
```

#### Object Pooling 패턴
```python
class ObjectPool:
    """메모리 할당/해제 최소화"""
    
    def __init__(self, object_class, initial_size=100):
        self.object_class = object_class
        self.available = deque()
        self.in_use = set()
        
        # 초기 객체 풀 생성
        for _ in range(initial_size):
            obj = object_class()
            obj.active = False
            self.available.append(obj)
            
    def get_object(self):
        if self.available:
            obj = self.available.popleft()
            obj.active = True
            self.in_use.add(obj)
            return obj
        else:
            # 풀이 부족하면 새로 생성
            obj = self.object_class()
            obj.active = True
            self.in_use.add(obj)
            return obj
            
    def return_object(self, obj):
        if obj in self.in_use:
            obj.active = False
            obj.reset()  # 객체 상태 초기화
            self.in_use.remove(obj)
            self.available.append(obj)
```

### 3. NumPy + Numba 활용 최적화
```python
import numpy as np
from numba import jit, prange

@jit(nopython=True, parallel=True)
def calculate_distances_vectorized(positions1, positions2):
    """벡터화된 거리 계산 - 수백 배 성능 향상"""
    n1, n2 = len(positions1), len(positions2)
    distances = np.zeros((n1, n2))
    
    for i in prange(n1):
        for j in prange(n2):
            dx = positions1[i][0] - positions2[j][0]
            dy = positions1[i][1] - positions2[j][1]
            distances[i][j] = np.sqrt(dx*dx + dy*dy)
    
    return distances

@jit(nopython=True)
def update_movement_batch(positions, velocities, delta_time):
    """배치 이동 처리 - NumPy 배열 연산 활용"""
    positions += velocities * delta_time
    return positions
```

---

## 🔄 현대적 라이브러리 스택 통합

### 1. docs/game-dependencies.md 기반 구현
현재 의존성 문서에서 제안된 라이브러리들을 실제 아키텍처에 통합:

#### 핵심 게임 엔진
```python
# requirements.txt 개선
pygame>=2.6.0              # 메인 게임 엔진
numpy>=2.2.4               # 수학 연산 최적화  
pymunk>=6.8.1              # 2D 물리 엔진
numba>=0.60.0              # JIT 컴파일 성능 향상

# UI 시스템
pygame-menu>=4.5.4         # 게임 메뉴 시스템
pygame-gui>=0.6.14         # 게임 내 UI 위젯

# 데이터 관리
pydantic>=2.0.0            # 설정 및 데이터 검증

# 개발 도구  
ruff>=0.6.0                # 초고속 린팅
pytest>=8.0.0              # 모던 테스팅
memory-profiler            # 성능 분석
```

#### 통합 아키텍처 구조
```python
class GameArchitecture:
    """통합 게임 아키텍처"""
    
    def __init__(self):
        # 핵심 시스템 초기화
        self.ecs_world = ECSWorld()
        self.event_bus = GameEventBus()
        self.physics_space = pymunk.Space()
        self.resource_manager = ResourceManager()
        
        # 성능 최적화 컴포넌트
        self.object_pools = {
            'projectile': ObjectPool(Projectile, 300),
            'enemy': ObjectPool(Enemy, 200),
            'particle': ObjectPool(Particle, 100)
        }
        
        # 공간 분할 시스템
        self.spatial_hash = QuadTree(pygame.Rect(0, 0, 800, 600))
        
        # UI 시스템
        self.ui_manager = pygame_gui.UIManager((800, 600))
        self.menu_system = MenuSystem()
```

### 2. Pydantic 기반 게임 설정 시스템
```python
from pydantic import BaseModel, Field
from typing import Dict, List

class GameConfig(BaseModel):
    """타입 안전 게임 설정"""
    
    # 성능 설정
    target_fps: int = Field(60, ge=30, le=120)
    max_enemies: int = Field(200, ge=50, le=500)
    max_projectiles: int = Field(300, ge=100, le=1000)
    
    # 게임플레이 설정
    difficulty_scaling: float = Field(1.0, ge=0.5, le=2.0)
    player_base_speed: float = Field(100.0, ge=50.0, le=200.0)
    
    # 아이템 설정
    item_spawn_rates: Dict[str, float] = {
        'soccer_ball': 0.3,
        'basketball': 0.25,
        'baseball_bat': 0.2,
        'soccer_shoes': 0.15,
        'basketball_shoes': 0.15,
        'red_ginseng': 0.1,
        'milk': 0.1
    }

class PlayerStats(BaseModel):
    """플레이어 스탯 검증"""
    health: int = Field(100, ge=1, le=1000)
    speed: float = Field(100.0, ge=10.0, le=500.0)
    attack_damage: int = Field(10, ge=1, le=100)
    attack_speed: float = Field(1.0, ge=0.1, le=5.0)
```

---

## 📋 TaskMaster 태스크 개선안

### 1. 기존 태스크 업데이트

#### Task 1: 프로젝트 환경 설정 개선
**현재 문제**: 기본적인 Pygame 설정만 포함  
**개선안**: 현대적 라이브러리 스택 통합

```markdown
# 개선된 Task 1 서브태스크
1.1 Python 3.13+ 가상환경 설정
1.2 현대적 의존성 스택 설치 (NumPy, Numba, Pymunk 포함)
1.3 Pydantic 기반 설정 시스템 구현  
1.4 Ruff + pytest 개발 환경 설정
1.5 기본 성능 프로파일링 도구 설정
1.6 Pygame + NumPy 통합 테스트
```

#### Task 3: 적 캐릭터 시스템 개선  
**현재 문제**: 단순한 클래스 기반 설계  
**개선안**: FSM + ECS 기반 AI 시스템

```markdown
# 개선된 Task 3 서브태스크  
3.1 ECS 기반 Enemy Component 설계
3.2 FSM 기반 AI 상태 시스템 구현
3.3 국어선생님 AI - 패트롤/추격/공격 상태
3.4 수학선생님 AI - 돌진 패턴 FSM
3.5 교장선생님 보스 AI - 복합 상태 머신
3.6 AI 행동 트리 구현 (Behavior Tree)
3.7 적 스포닝 시스템 (Object Pooling 적용)
3.8 Pymunk 기반 정밀 충돌 감지
```

#### Task 10: 성능 최적화 구체화
**현재 문제**: 추상적인 성능 개선 내용  
**개선안**: 구체적인 최적화 기법 적용

```markdown
# 개선된 Task 10 서브태스크
10.1 NumPy + Numba 기반 수학 연산 최적화
10.2 QuadTree 공간 분할 충돌 감지 구현
10.3 Object Pooling 패턴 전면 적용
10.4 더티 렌더링 시스템 구현  
10.5 스프라이트 배칭 최적화
10.6 메모리 프로파일링 및 GC 최적화
10.7 프레임 레이트 안정화 (40+ FPS 달성)
10.8 성능 벤치마크 테스트 구축
```

### 2. 신규 태스크 추가

#### Task 1.5: ECS 프레임워크 구현 (신규)
```markdown
# Task 1.5: ECS 아키텍처 프레임워크
우선순위: High
의존성: Task 1

서브태스크:
1.5.1 Entity Manager 클래스 구현
1.5.2 Component Registry 시스템 구현  
1.5.3 System Orchestrator 구현
1.5.4 기본 Component 타입 정의 (Health, Movement, Weapon)
1.5.5 기본 System 구현 (Movement, Combat, Rendering)
1.5.6 ECS 성능 테스트 및 최적화
1.5.7 ECS 디버깅 도구 구현
```

#### Task 11: 아키텍처 통합 및 리팩토링 (신규)
```markdown
# Task 11: 시스템 통합 및 아키텍처 검증
우선순위: Medium  
의존성: Task 1.5, Task 3, Task 5, Task 6

서브태스크:
11.1 Event-Driven 아키텍처 전면 적용
11.2 시스템 간 인터페이스 표준화
11.3 모듈 의존성 그래프 최적화
11.4 통합 테스트 스위트 구축
11.5 성능 벤치마크 달성 검증 (40+ FPS)
11.6 메모리 사용량 최적화 검증
11.7 아키텍처 문서 업데이트
11.8 코드 품질 검증 (Ruff + pytest)
```

#### Task 12: AI 시스템 고도화 (신규)
```markdown
# Task 12: 고급 AI 및 게임플레이 시스템
우선순위: Low
의존성: Task 11

서브태스크:
12.1 Behavior Tree 라이브러리 통합
12.2 교장선생님 복합 AI 패턴 구현
12.3 적응형 난이도 시스템 구현  
12.4 플레이어 행동 분석 시스템
12.5 동적 밸런싱 시스템
12.6 AI 디버깅 및 비주얼라이제이션 도구
```

---

## 🚀 구현 로드맵

### Phase 1: 기반 아키텍처 구축 (Week 1-2)
1. **Task 1 업데이트**: 현대적 라이브러리 스택 통합
2. **Task 1.5**: ECS 프레임워크 구현  
3. **기본 성능 테스트**: 40 FPS 목표 달성 검증

### Phase 2: 핵심 게임 시스템 (Week 3-4) 
1. **Task 2 업데이트**: ECS 기반 플레이어 시스템
2. **Task 3 업데이트**: FSM 기반 AI 시스템
3. **Task 4-6**: 게임플레이 기본 기능 구현

### Phase 3: 고급 기능 및 최적화 (Week 5-6)
1. **Task 7-9**: 게임 완성도 향상
2. **Task 10 업데이트**: 구체적 성능 최적화  
3. **Task 11**: 시스템 통합 및 검증

### Phase 4: 완성도 및 확장성 (Week 7-8)
1. **Task 12**: 고급 AI 시스템
2. **최종 성능 최적화**: 목표 FPS 안정화
3. **확장성 검증**: 새 기능 추가 용이성 테스트

---

## 📊 성공 지표 및 검증 방법

### 1. 성능 지표
- **프레임레이트**: 40+ FPS 안정적 유지 (적 200개 + 투사체 300개)
- **메모리 사용량**: 150MB 이하 유지
- **로딩 시간**: 게임 시작 3초 이내

### 2. 코드 품질 지표  
- **테스트 커버리지**: 80% 이상
- **Ruff 린팅**: 0 에러, 0 경고
- **타입 힌트 커버리지**: 90% 이상

### 3. 아키텍처 품질 지표
- **모듈 결합도**: 낮은 결합도 (의존성 그래프 분석)
- **확장성**: 새 적/아이템 추가 30분 이내
- **유지보수성**: 기능 수정 시 영향 범위 최소화

### 4. 게임플레이 지표
- **반응성**: 입력 지연 50ms 이하  
- **안정성**: 10분 플레이 중 크래시 0회
- **밸런싱**: 플레이 테스트 기반 난이도 곡선 검증

---

## 📚 참고 아키텍처 패턴

### 1. 유사 프로젝트 분석
- **Vampire Survivors**: ECS + Object Pooling 패턴
- **Risk of Rain**: 이벤트 기반 아이템 시너지 시스템
- **Enter the Gungeon**: FSM 기반 보스 AI 패턴

### 2. Python 게임 개발 베스트 프랙티스
- **성능**: NumPy + Numba 조합 활용
- **아키텍처**: pygame + pymunk 통합 패턴  
- **테스팅**: pytest 기반 게임 로직 테스트

### 3. 확장성 고려 설계
- **데이터 드리븐**: JSON/YAML 기반 게임 설정
- **플러그인 시스템**: 새 기능 동적 로딩
- **모드 지원**: 다양한 게임 모드 확장 가능

---

## ✅ 체크리스트 및 다음 단계

### 즉시 실행 필요 사항
- [ ] TaskMaster에서 Task 1, 3, 10 업데이트  
- [ ] 새로운 Task 1.5, 11, 12 추가
- [ ] requirements.txt를 현대적 라이브러리 스택으로 개선
- [ ] 기본 ECS 프레임워크 프로토타입 구현

### 검증 필요 사항  
- [ ] 40+ FPS 성능 목표 달성 가능성 검증
- [ ] NumPy + Numba 조합 효과 측정
- [ ] Pymunk 물리 엔진 통합 테스트
- [ ] 메모리 사용량 프로파일링

### 장기 계획
- [ ] 아키텍처 패턴별 성능 벤치마크 구축
- [ ] 확장성 테스트를 위한 새 기능 추가 시뮬레이션  
- [ ] 팀 개발을 위한 모듈 인터페이스 표준화
- [ ] CI/CD 파이프라인 구축 (성능 회귀 방지)

---

## 📞 결론 및 권장사항

이 아키텍처 개선 계획을 통해 "방과후생존" 게임은 다음과 같은 이점을 얻을 수 있습니다:

1. **성능 목표 달성**: 40+ FPS 안정적 유지를 통한 원활한 게임플레이
2. **확장성 확보**: ECS + Event-Driven 아키텍처로 새 기능 추가 용이
3. **개발 생산성**: 현대적 도구 스택으로 개발 및 디버깅 효율성 향상  
4. **코드 품질**: 타입 안전성과 테스트 커버리지를 통한 안정성 확보

**다음 단계로는 TaskMaster에서 제안된 태스크 업데이트를 진행하고, 핵심 아키텍처 컴포넌트부터 단계적으로 구현하는 것을 권장합니다.**

---

> **노트**: 이 문서는 방과후생존 게임의 기술적 우수성과 사용자 경험 향상을 위한 종합적 가이드라인입니다. 구현 과정에서 발생하는 기술적 이슈나 성능 문제에 대한 추가 컨설팅이 필요한 경우 언제든 아키텍트에게 문의하시기 바랍니다.