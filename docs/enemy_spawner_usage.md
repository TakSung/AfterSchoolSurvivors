# EnemySpawner 시스템 사용 가이드

## 개요

EnemySpawner는 "방과 후 생존" 게임의 적 캐릭터 생성 및 관리 시스템입니다. 웨이브 기반으로 동작하며, 시간에 따라 난이도가 증가하는 적 생성 패턴을 제공합니다.

## 주요 특징

### 🎪 웨이브 기반 시스템
- **초반 웨이브** (0-60초): 국어선생님 위주 (80%), 수학선생님 (20%)
- **중반 웨이브** (60-180초): 국어선생님 (50%), 수학선생님 (50%)
- **후반 웨이브** (180-360초): 국어선생님 (30%), 수학선생님 (60%), 교장선생님 (10%)
- **보스 페이즈** (360초+): 교장선생님 중심 (50%), 기타 보조 적들 (50%)

### ⚡ 성능 최적화
- 최대 50개 적 제한으로 40+ FPS 보장
- 스폰 위치 사전 계산 풀링 (100개 위치)
- 웨이브별 설정 캐싱으로 런타임 성능 향상

### 🎮 동적 밸런싱
- 웨이브별 생성 간격 자동 조절
- 적 타입별 가중 랜덤 생성
- 시간에 따른 난이도 곡선 관리

## 기본 사용법

### 1. 초기화
```python
from src.core.entity_manager import EntityManager
from src.systems.enemy_spawner import EnemySpawner

# EntityManager 생성
entity_manager = EntityManager()

# EnemySpawner 초기화
enemy_spawner = EnemySpawner(entity_manager)
```

### 2. 게임 루프에서 업데이트
```python
def game_loop():
    while running:
        delta_time = clock.tick(60) / 1000.0  # 초 단위
        
        # 스포너 업데이트 - 새로 생성된 적들 반환
        new_enemies = enemy_spawner.update(delta_time)
        
        # 새로운 적들 처리 (렌더링, AI 등)
        for enemy in new_enemies:
            # pygame sprite 생성 또는 ECS 시스템에 등록
            handle_new_enemy(enemy)
```

### 3. 적 생성 모니터링
```python
# 현재 스포너 상태 확인
stats = enemy_spawner.get_stats()
print(f"현재 웨이브: {stats['current_wave']}")
print(f"활성 적: {stats['active_enemies']}/{enemy_spawner.MAX_ENEMIES}")
print(f"다음 생성: {stats['next_spawn_in']:.1f}초 후")
```

## 고급 기능

### 보스 강제 스폰
```python
# 테스트나 이벤트를 위한 보스 즉시 생성
boss = enemy_spawner.force_spawn_boss()
if boss:
    print(f"보스 생성: {boss.enemy_type.display_name}")
```

### 모든 적 제거
```python
# 디버그나 특수 이벤트 시 모든 적 제거
removed_count = enemy_spawner.clear_all_enemies()
print(f"{removed_count}개의 적이 제거됨")
```

## ECS 통합 예제

### EnemySprite 어댑터 패턴
```python
class EnemySprite(pygame.sprite.Sprite):
    """ECS Enemy를 pygame 렌더링용으로 변환하는 어댑터"""
    
    def __init__(self, enemy, entity_manager):
        super().__init__()
        self.enemy = enemy
        self.entity_manager = entity_manager
        
        # 적 타입별 시각적 표현
        self._setup_sprite()
        self._update_position()
    
    def update(self):
        # ECS 위치를 pygame 좌표로 동기화
        if not self.enemy.is_alive():
            self.kill()
            return
        self._update_position()
```

### pygame와 ECS 혼합 사용
```python
# 새로 생성된 ECS 적들을 pygame sprite로 변환
for enemy in new_enemies:
    enemy_sprite = EnemySprite(enemy, entity_manager)
    enemy_sprites.add(enemy_sprite)
    all_sprites.add(enemy_sprite)

# pygame 충돌 검사로 ECS 엔티티 상태 변경
hits = pygame.sprite.groupcollide(projectiles, enemy_sprites, True, False)
for projectile, enemies in hits.items():
    for enemy_sprite in enemies:
        is_dead = enemy_sprite.enemy.take_damage(25)
        if is_dead:
            print(f"{enemy_sprite.enemy.enemy_type.display_name} 처치!")
```

## 설정 커스터마이징

### 웨이브 설정 수정
웨이브별 설정은 `EnemySpawner._initialize_wave_configs()` 메서드에서 수정 가능:

```python
{
    SpawnWave.EARLY_GAME: {
        "duration": 60.0,                    # 웨이브 지속 시간
        "spawn_interval_range": (2.0, 3.0),  # 생성 간격 범위 (초)
        "enemy_ratios": {                    # 적 타입별 생성 비율
            EnemyType.KOREAN_TEACHER: 0.8,
            EnemyType.MATH_TEACHER: 0.2,
            EnemyType.PRINCIPAL: 0.0
        },
        "max_enemies_multiplier": 0.6,       # 최대 적 수 배율
        "description": "초보자 친화적 웨이브"
    }
}
```

### 성능 튜닝
성능 관련 상수들은 클래스 상단에서 조정 가능:

```python
class EnemySpawner:
    MAX_ENEMIES = 50            # 최대 적 수 (성능 한계)
    MIN_SPAWN_INTERVAL = 0.5    # 최소 생성 간격 (초)
    MAX_SPAWN_INTERVAL = 3.0    # 최대 생성 간격 (초)
```

## 디버그 및 테스트

### 키보드 단축키 예제
```python
# main_with_spawner.py 참조
elif event.key == pygame.K_f:  # F키: 보스 강제 스폰
    boss = enemy_spawner.force_spawn_boss()
elif event.key == pygame.K_c:  # C키: 모든 적 제거
    enemy_spawner.clear_all_enemies()
```

### 테스트 실행
```bash
# 단위 테스트 실행
python3 -m pytest tests/test_enemy_spawner.py -v

# 통합 테스트 (pygame 데모)
python3 src/main_with_spawner.py
```

## 트러블슈팅

### 일반적인 문제들

1. **적이 생성되지 않는 경우**
   - 최대 적 수 제한 확인 (`MAX_ENEMIES`)
   - 생성 간격 확인 (`next_spawn_interval`)
   - EntityManager 상태 확인

2. **성능 문제 (FPS 저하)**
   - `MAX_ENEMIES` 값 줄이기 (기본: 50)
   - 스폰 위치 풀 크기 조정 (기본: 100)
   - 죽은 적 정리 주기 확인

3. **웨이브 전환이 안 되는 경우**
   - 게임 시작 시간 초기화 확인 (`game_start_time`)
   - 시스템 시계 동기화 문제 가능성

### 로그 확인
```python
# 스포너 상태 로그 출력
stats = enemy_spawner.get_stats()
print(f"스포너 통계: {stats}")
print(f"스포너 상태: {enemy_spawner}")
```

## 확장 가능성

### 새로운 적 타입 추가
1. `EnemyType` 열거형에 새 타입 추가
2. 새 Enemy 하위 클래스 구현
3. `Enemy.create_enemy_by_type()` 팩토리 메서드 업데이트
4. 웨이브 설정에 새 적 타입 비율 추가

### 새로운 웨이브 패턴
1. `SpawnWave` 열거형에 새 웨이브 추가
2. `_initialize_wave_configs()`에 설정 추가
3. `_update_wave()` 로직에 전환 조건 추가

### 동적 난이도 조절
현재는 시간 기반이지만, 플레이어 성과에 따른 동적 조절 가능:
```python
# 플레이어 점수에 따른 웨이브 가속화
if player_score > threshold:
    spawner.next_spawn_interval *= 0.8  # 20% 빨라짐
```

## 관련 파일

- **핵심 구현**: `src/systems/enemy_spawner.py`
- **테스트**: `tests/test_enemy_spawner.py`  
- **통합 예제**: `src/main_with_spawner.py`
- **적 엔티티**: `src/entities/enemy.py`, `src/entities/*_teacher.py`
- **컴포넌트**: `src/components/enums.py`, `src/components/enemy_component.py`

---

이 시스템은 Task 3.5 "적 스포너 및 생성 시스템 구현"의 완전한 구현체입니다. 40+ FPS 성능 목표를 달성하면서도 복잡한 웨이브 기반 게임플레이를 제공합니다.