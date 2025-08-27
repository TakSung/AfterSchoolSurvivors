# Code Convention Rules

This file contains detailed coding standards and conventions for the After School Survivors project based on refactor-PRD.md architecture.

## Executive Summary

Apply modern Python 3.13+ conventions with SharedEventQueue-based Producer-Consumer event architecture, interface-first design with factory patterns, and DTO-based communication for the refactored ECS system.

## Core Principles

1. **Type Safety First**: All functions require complete type hints using Python 3.13+ native syntax
2. **Interface-First Design**: ABC contracts define all system boundaries
3. **DTO Communication**: Type-safe data transfer between all layers
4. **Performance-Optimized Enums**: Multi-layer IntEnum pattern for game values
5. **Pure Function Priority**: Separate state mutation from calculation logic
6. **SharedEventQueue Architecture**: Direct Producer-Consumer event communication
7. **Factory Pattern Integration**: Interface-based manager and system creation

## 1. Type Hints & Modern Syntax

### Use Native Collections (Python 3.9+)
```python
# ✅ Correct - Native generics
def process_entities(entities: list[Entity]) -> dict[str, int]:
    return {}

# ❌ Avoid - typing module imports
from typing import List, Dict
def process_entities(entities: List[Entity]) -> Dict[str, int]:
    return {}
```

### Union Types with | Syntax (Python 3.10+)
```python
# ✅ Correct - Modern union syntax
def handle_input(value: int | float | None) -> str:
    return ""

# ❌ Avoid - typing.Union
from typing import Union
def handle_input(value: Union[int, float, None]) -> str:
    return ""
```

### Mandatory Type Hints
```python
# ✅ Correct - Complete typing
def calculate_damage_with_synergy(
    base_damage: int,
    synergy_multiplier: float,
    target_defense: int
) -> int:
    return int(base_damage * synergy_multiplier - target_defense)

# ❌ Avoid - Missing type hints
def calculate_damage_with_synergy(base_damage, synergy_multiplier, target_defense):
    return int(base_damage * synergy_multiplier - target_defense)
```

## 2. Multi-Layer Enum Performance Pattern

### Required Enum Usage Patterns
Use Enums for ALL predefined value variables with these suffixes:
- `*_type`: `weapon_type: WeaponType`, `projectile_type: ProjectileType`
- `*_status`: `player_status: PlayerStatus`, `game_status: GameStatus`  
- `*_state`: `entity_state: EntityState`, `game_state: GameState`
- `*_mode`: `difficulty_mode: DifficultyMode`, `render_mode: RenderMode`
- `*_phase`: `game_phase: GamePhase`, `battle_phase: BattlePhase`
- `*_priority`: `task_priority: Priority`, `render_priority: RenderPriority`

### Three-Layer Implementation Pattern

**Performance Layer - Integer codes for computation:**
```python
from enum import IntEnum

class WeaponType(IntEnum):
    BASIC = 0
    RAPID_FIRE = 1
    SPREAD_SHOT = 2
    LASER_BEAM = 3
    
    @property
    def display_name(self) -> str:
        """User-friendly display string"""
        return self._display_names[self]
    
    @property
    def damage_multiplier(self) -> float:
        """Performance computation using integer values"""
        return self._damage_multipliers[self.value]
    
    _display_names = {
        BASIC: "Basic Shot",
        RAPID_FIRE: "Rapid Fire",
        SPREAD_SHOT: "Spread Shot", 
        LASER_BEAM: "Laser Beam"
    }
    
    _damage_multipliers = [1.0, 0.7, 0.9, 1.5]  # Index-based lookup
```

**Usage Convention by Context:**
```python
# ✅ DTO/Business Logic - Use Enum directly
@dataclass
class WeaponComponent:
    weapon_type: WeaponType
    damage: int
    attack_speed: float

# ✅ Performance Critical - Use .value for computations  
def calculate_weapon_damage(weapon: WeaponComponent, base_damage: int) -> int:
    # Fast integer comparison and array lookup
    multiplier_index = weapon.weapon_type.value
    return int(base_damage * weapon.weapon_type._damage_multipliers[multiplier_index])

# ✅ UI/Display - Use .display_name for user interface
def render_weapon_info(weapon: WeaponComponent) -> str:
    return f"Weapon: {weapon.weapon_type.display_name}"
```

### Game-Specific Enum Examples

```python
class PlayerStatus(IntEnum):
    ALIVE = 0
    INVULNERABLE = 1  
    DEAD = 2
    
    @property
    def display_name(self) -> str:
        return ["Alive", "Invulnerable", "Dead"][self.value]

class GameState(IntEnum):
    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    
    @property
    def display_name(self) -> str:
        return ["Menu", "Playing", "Paused", "Game Over"][self.value]

class DebuffType(IntEnum):
    SLOW = 0
    POISON = 1
    FREEZE = 2
    BURN = 3
    
    @property
    def display_name(self) -> str:
        return ["Slow", "Poison", "Freeze", "Burn"][self.value]
    
    @property
    def stack_limit(self) -> int:
        return [3, 5, 1, 4][self.value]  # Performance-optimized lookup
```

## 3. Naming Conventions

### Classes - PascalCase
```python
class PlayerMovementSystem: pass
class HealthComponent: pass  
class ICollisionDetector(ABC): pass  # Interface prefix
```

### Functions/Variables - snake_case
```python
def calculate_damage_with_synergy() -> int: pass
max_health = 100
current_weapon_type = WeaponType.BASIC
```

### Constants - UPPER_SNAKE_CASE  
```python
MAX_ENEMIES_COUNT = 50
DEFAULT_PLAYER_SPEED = 200.0
WEAPON_DAMAGE_MULTIPLIERS = [1.0, 0.7, 0.9, 1.5]
```

### Component Suffix Convention
```python
class HealthComponent: pass
class MovementComponent: pass
class WeaponComponent: pass
```

## 4. ECS Architecture Patterns

### Interface Definition with ABC
```python
from abc import ABC, abstractmethod

class ISystem(ABC):
    @abstractmethod
    def update(self, entities: list[Entity], delta_time: float) -> None: pass
    
    @abstractmethod  
    def initialize(self) -> None: pass
    
    @abstractmethod
    def cleanup(self) -> None: pass
```

### Component Structure with Enums
```python
@dataclass
class HealthComponent:
    current: int
    maximum: int
    status: PlayerStatus  # Enum for type safety
    regeneration_rate: float

@dataclass  
class WeaponComponent:
    weapon_type: WeaponType  # Multi-layer Enum
    damage: int
    attack_speed: float
    projectile_type: ProjectileType
```

### System Implementation Example
```python
class CollisionSystem(ISystem):
    def update(self, entities: list[Entity], delta_time: float) -> None:
        for entity in entities:
            if entity.has_component(CollisionComponent):
                # Use enum.value for performance-critical calculations
                collision_type_code = entity.collision_component.collision_type.value
                self._handle_collision_by_code(collision_type_code)
    
    def _handle_collision_by_code(self, type_code: int) -> None:
        # Fast integer-based logic
        pass
```

## 5. Data Structure Patterns

### Use dataclass with type hints
```python
@dataclass
class GameConfig:
    target_fps: int = 60
    max_enemies: int = 50
    difficulty_mode: DifficultyMode = DifficultyMode.NORMAL
    
@dataclass
class PlayerStats:
    health: int
    damage: int
    speed: float
    current_status: PlayerStatus
```

### JSON Serialization with Enums
```python
# ✅ Correct - Integer serialization for performance
def serialize_component(component: WeaponComponent) -> dict[str, any]:
    return {
        "weapon_type": component.weapon_type.value,  # Integer for size/speed
        "damage": component.damage,
        "attack_speed": component.attack_speed
    }

def deserialize_component(data: dict[str, any]) -> WeaponComponent:
    return WeaponComponent(
        weapon_type=WeaponType(data["weapon_type"]),  # Reconstruct from int
        damage=data["damage"], 
        attack_speed=data["attack_speed"]
    )
```

## 6. Performance Optimization Patterns

### Pure Functions for Calculations
```python
# ✅ Correct - Pure function with type hints
def calculate_movement_delta(
    current_pos: tuple[float, float],
    velocity: tuple[float, float], 
    delta_time: float
) -> tuple[float, float]:
    return (
        current_pos[0] + velocity[0] * delta_time,
        current_pos[1] + velocity[1] * delta_time
    )

# ✅ Use enum values for performance-critical paths  
def apply_debuff_effects(
    base_speed: float,
    debuff_types: list[DebuffType]
) -> float:
    speed_multiplier = 1.0
    for debuff in debuff_types:
        # Fast integer lookup instead of string comparison
        if debuff.value == DebuffType.SLOW.value:
            speed_multiplier *= 0.5
        elif debuff.value == DebuffType.FREEZE.value:
            speed_multiplier = 0.0
    return base_speed * speed_multiplier
```

### Avoid String Comparisons in Game Loops
```python
# ❌ Avoid - String comparison in hot path
def update_entity_by_type(entity: Entity) -> None:
    if entity.type_name == "player":  # Slow string comparison
        update_player(entity)
    elif entity.type_name == "enemy":
        update_enemy(entity)

# ✅ Correct - Integer comparison with Enum
def update_entity_by_type(entity: Entity) -> None:
    if entity.entity_type.value == EntityType.PLAYER.value:  # Fast int comparison
        update_player(entity)
    elif entity.entity_type.value == EntityType.ENEMY.value:
        update_enemy(entity)
```

## 7. Testing Patterns

### pytest Structure with Enum Testing
```python
import pytest
from your_game.components import WeaponComponent, WeaponType

class TestWeaponComponent:
    def test_weapon_damage_calculation(self) -> None:
        weapon = WeaponComponent(
            weapon_type=WeaponType.RAPID_FIRE,
            damage=10,
            attack_speed=0.3
        )
        
        # Test all three layers
        assert weapon.weapon_type.value == 1  # Performance layer
        assert weapon.weapon_type.display_name == "Rapid Fire"  # Display layer
        assert weapon.weapon_type.damage_multiplier == 0.7  # Business layer
    
    @pytest.mark.parametrize("weapon_type,expected_multiplier", [
        (WeaponType.BASIC, 1.0),
        (WeaponType.RAPID_FIRE, 0.7),
        (WeaponType.SPREAD_SHOT, 0.9),
        (WeaponType.LASER_BEAM, 1.5),
    ])
    def test_damage_multipliers(
        self, weapon_type: WeaponType, expected_multiplier: float
    ) -> None:
        assert weapon_type.damage_multiplier == expected_multiplier
```

## 8. Tool Configuration

### Ruff Configuration (pyproject.toml)
```toml
[tool.ruff]
line-length = 79
target-version = "py313"
include = ["*.py", "src/**/*.py", "tests/**/*.py", "ai/**/*.py", "docs/**/*.py", "todo/**/*.py"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle (오류)
    "W",   # pycodestyle (경고)
    "F",   # Pyflakes (논리적 오류)
    "I",   # isort (import 정렬)
    "D",   # pydocstyle (Docstring 스타일)
    "ANN", # flake8-annotations (타입 힌트 강제)
    "B",   # flake8-bugbear (버그 유발 가능성 높은 코드)
    "C4",  # flake8-comprehensions (비효율적 comprehension)
    "T20", # flake8-print (print문 사용 감지)
    "S",   # flake8-bandit (보안 문제)
    "UP",  # pyupgrade (최신 파이썬 문법으로 업그레이드)
    "SIM", # flake8-simplify (코드 간소화)
    "RUF", # Ruff 전용 규칙
]
ignore = [
    "S101",  # 'assert' 문 사용 경고 제외
    "D400",  # docstring 첫 번째 줄 끝에 마침표 없는 경고 제외
]

[tool.ruff.format] 
quote-style = "single"  # 홑따옴표 사용
indent-style = "space"

[tool.ruff.lint.pydocstyle]
convention = "pep257"

[tool.ruff.lint.flake8-annotations]
mypy-init-return = true
suppress-none-returning = true
```

### Type Checking Integration (mypy.ini)
```ini
[mypy]
strict = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
disallow_untyped_calls = True
disallow_untyped_decorators = True
disallow_any_unimported = True
no_implicit_optional = True
warn_return_any = True
warn_no_return = True
warn_unused_ignores = True
strict_equality = True
```

### Development Workflow Commands
```bash
# Conda environment commands
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff check --fix .
/opt/homebrew/anaconda3/envs/as-game/bin/python -m ruff format .
/opt/homebrew/anaconda3/envs/as-game/bin/python -m mypy src/
/opt/homebrew/anaconda3/envs/as-game/bin/python -m pytest tests/ -v
```

## 9. Code Quality Checklist

Before committing, verify:

- [ ] All functions have complete type hints using Python 3.13+ syntax
- [ ] Predefined value variables use appropriate Enum types (*_type, *_status, etc.)
- [ ] Performance-critical code uses enum.value for integer comparisons
- [ ] UI code uses enum.display_name for user-facing strings
- [ ] ABC interfaces define system contracts
- [ ] Components use dataclass with type hints
- [ ] Pure functions separate from state mutation
- [ ] Tests cover all three Enum layers (value, business logic, display)
- [ ] Ruff passes without warnings
- [ ] mypy/pyright type checking passes

## 10. Common Patterns Summary

### Quick Reference - Enum Usage
```python
# Declaration
class StatusType(IntEnum):
    ACTIVE = 0
    INACTIVE = 1
    
    @property
    def display_name(self) -> str:
        return ["Active", "Inactive"][self.value]

# Usage contexts
status: StatusType = StatusType.ACTIVE           # Business logic
performance_code: int = status.value             # Hot path computation  
user_text: str = status.display_name            # UI display
```

### Quick Reference - Component Pattern
```python
@dataclass
class ComponentName:
    typed_field: int
    enum_field: EnumType
    optional_field: str | None = None
```

## 11. Interface-First Design Principles (v0.4 Architecture)

### Manager Interface Pattern
```python
from abc import ABC, abstractmethod

class IEnemyManager(ABC):
    @abstractmethod
    def create_enemy(self, dto: EnemyCreateDTO) -> str:
        """Create enemy and return entity ID."""
        pass
    
    @abstractmethod
    def update_enemy_stats(self, dto: EnemyUpdateDTO) -> bool:
        """Update enemy statistics."""
        pass
    
    @abstractmethod
    def get_alive_enemies(self) -> list[str]:
        """Get list of alive enemy IDs."""
        pass
```

### System Interface Pattern
```python
class ISystem(ABC):
    @abstractmethod
    def initialize(self) -> bool:
        """System initialization. Returns success status."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """System update with delta time."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """System cleanup and shutdown."""
        pass
    
    @abstractmethod
    def get_system_name(self) -> str:
        """System identification name."""
        pass
    
    @abstractmethod
    def get_priority(self) -> int:
        """System update priority (lower = earlier)."""
        pass

class IEventAwareSystem(ISystem):
    @abstractmethod
    def register_event_handlers(self, tunnel_manager: 'IEventTunnelManager') -> None:
        """Register event handlers with tunnel manager."""
        pass
    
    @abstractmethod
    def unregister_event_handlers(self) -> None:
        """Unregister event handlers."""
        pass
```

## 12. DTO Pattern for Type-Safe Communication

### DTO Structure with Validation
```python
@dataclass
class EnemyCreateDTO:
    spawn_position: tuple[float, float]
    enemy_type: EnemyType
    difficulty_scale: float
    base_health: int
    base_speed: float
    
    def validate(self) -> bool:
        """Validate DTO data integrity."""
        return (
            self.base_health > 0 
            and self.base_speed > 0 
            and self.difficulty_scale >= 0
            and len(self.spawn_position) == 2
        )

@dataclass
class WeaponUpgradeDTO:
    weapon_entity_id: str
    upgrade_type: WeaponUpgradeType
    bonus_multiplier: float
    synergy_items: list[ItemType] = field(default_factory=list)
    
    def validate(self) -> bool:
        return (
            len(self.weapon_entity_id) > 0
            and self.bonus_multiplier >= 0
        )
```

### Manager Implementation with DTOs
```python
class EnemyManager(IEnemyManager):
    def __init__(self, entity_manager: IEntityManager) -> None:
        self._entity_manager = entity_manager
    
    def create_enemy(self, dto: EnemyCreateDTO) -> str:
        if not dto.validate():
            raise ValueError("Invalid EnemyCreateDTO data")
        
        entity = self._entity_manager.create_entity()
        
        # Add components using DTO data
        position_comp = PositionComponent(dto.spawn_position[0], dto.spawn_position[1])
        enemy_comp = EnemyComponent(
            enemy_type=dto.enemy_type,
            difficulty_scale=dto.difficulty_scale
        )
        health_comp = HealthComponent(
            current=dto.base_health,
            maximum=dto.base_health
        )
        
        self._entity_manager.add_component(entity, position_comp)
        self._entity_manager.add_component(entity, enemy_comp)
        self._entity_manager.add_component(entity, health_comp)
        
        return entity.entity_id
```

## 13. AI Comment System

### # AI-NOTE : Business Logic & Requirements

**Usage**: Business logic, user requirements, domain rules

**Format**:
```python
# AI-NOTE : [Date] Business logic description
# - Reason: Why implemented this way
# - Requirements: Which requirements reflected
# - History: Differences from previous version
```

**Example**:
```python
# AI-NOTE : 2025-01-26 Producer-Consumer event system introduction
# - Reason: Replace EventBus with direct SharedEventQueue for performance
# - Requirements: Type-safe event handling without intermediate registration
# - History: Migrated from observer pattern to tunnel-based architecture
class WeaponSystem(IEventAwareSystem):
    def update(self, delta_time: float) -> None:
        # Direct producer access for events
        producer = self._tunnel_manager.get_producer(WeaponAttackEvent)
        producer.produce(WeaponAttackEvent(weapon_id, target_id))
```

### # AI-DEV : Technical Development Notes

**Usage**: Technical solutions, performance optimization, bug fixes, architecture decisions

**Format**:
```python
# AI-DEV : [Technical reason] Implementation description
# - Problem: What technical issue existed
# - Solution: How it was solved
# - Caution: Maintenance considerations
```

**Example**:
```python
# AI-DEV : Interface segregation for manager dependencies
# - Problem: Manager classes had circular dependencies and unclear contracts
# - Solution: Separate interfaces per domain (IEnemyManager, IWeaponManager)
# - Caution: DTO validation must be consistent across all manager implementations
class WeaponSystem(IEventAwareSystem):
    def __init__(
        self,
        weapon_manager: IWeaponManager,
        projectile_manager: IProjectileManager
    ) -> None:
        self._weapon_manager = weapon_manager
        self._projectile_manager = projectile_manager
```

## 14. v0.4 Architecture Forbidden Patterns

### Dependency Violations (Forbidden)
```python
# ❌ FORBIDDEN - Manager calling System directly
class EnemyManager(IEnemyManager):
    def update_ai(self) -> None:
        # Never call systems from managers
        enemy_system.update_enemy_ai()  # VIOLATION

# ❌ FORBIDDEN - System calling other System directly  
class WeaponSystem(IEventAwareSystem):
    def update(self, delta_time: float) -> None:
        # Never call other systems directly
        projectile_system.spawn_projectile()  # VIOLATION

# ❌ FORBIDDEN - Core ECS accessing Manager directly
class EntityManager:
    def create_specialized_entity(self) -> Entity:
        # Core ECS should never know about managers
        enemy_manager.create_enemy()  # VIOLATION
```

### Correct Architecture Patterns
```python
# ✅ CORRECT - System using Manager interface
class WeaponSystem(IEventAwareSystem):
    def __init__(self, weapon_manager: IWeaponManager) -> None:
        self._weapon_manager = weapon_manager  # Interface dependency
    
    def update(self, delta_time: float) -> None:
        # Use manager through interface
        weapon_dto = WeaponCreateDTO(...)
        weapon_id = self._weapon_manager.create_weapon(weapon_dto)

# ✅ CORRECT - Manager using Core ECS only
class EnemyManager(IEnemyManager):
    def __init__(self, entity_manager: IEntityManager) -> None:
        self._entity_manager = entity_manager  # Only core ECS dependency
    
    def create_enemy(self, dto: EnemyCreateDTO) -> str:
        entity = self._entity_manager.create_entity()
        return entity.entity_id

# ✅ CORRECT - Event-based System communication
class WeaponSystem(IEventAwareSystem):
    def update(self, delta_time: float) -> None:
        # Communicate via events, not direct calls
        producer = self._tunnel_manager.get_producer(WeaponAttackEvent)
        producer.produce(WeaponAttackEvent(weapon_id, damage))
```

## 15. Naming Conventions (Updated)

- **Classes**: `PascalCase` (PlayerMovementSystem, HealthComponent, ICollisionDetector)
- **Interfaces**: `I` prefix + `PascalCase` (IEnemyManager, ISystem, IEventAwareSystem)
- **Functions/Variables**: `snake_case` (calculate_damage_with_synergy, max_health)
- **Constants**: `UPPER_SNAKE_CASE` (MAX_ENEMIES_COUNT, DEFAULT_PLAYER_SPEED)
- **Component Suffix**: Always end with "Component" (HealthComponent, WeaponComponent)
- **Manager Suffix**: Always end with "Manager" (EnemyManager, WeaponManager)
- **DTO Suffix**: Always end with "DTO" (EnemyCreateDTO, WeaponUpgradeDTO)
- **System Suffix**: Always end with "System" (WeaponSystem, ProjectileSystem)

## 16. Code Quality Checklist (Updated for v0.4)

Before committing, verify:
- [ ] All functions have complete type hints using Python 3.13+ syntax
- [ ] All managers implement interface contracts (I* interfaces)
- [ ] DTO classes include validate() methods
- [ ] System classes inherit from ISystem or IEventAwareSystem
- [ ] No forbidden dependency violations (Manager→System, ECS→Manager)
- [ ] Game values use appropriate IntEnum types (*_type, *_status, *_state, *_mode)
- [ ] Performance-critical code uses enum.value for integer comparisons
- [ ] UI code uses enum.display_name for Korean text display
- [ ] Components use @dataclass with type hints
- [ ] Pure functions separate from state mutation
- [ ] AI comment system appropriately applied (AI-NOTE, AI-DEV)
- [ ] `ruff check .` and `ruff format .` pass without errors
- [ ] Interface segregation maintained (single responsibility per interface)

## 17. System Factory Pattern Integration

### ISystemFactory Pattern
Central factory interface for creating all system instances:
```python
from abc import ABC, abstractmethod

class ISystemFactory(ABC):
    @abstractmethod
    def create_weapon_system(self, config: SystemConfig) -> IWeaponSystem:
        """Create weapon system based on configuration."""
        pass
    
    @abstractmethod
    def create_projectile_system(self, config: SystemConfig) -> IProjectileSystem:
        """Create projectile system based on configuration."""
        pass

class SystemFactory(ISystemFactory):
    def create_weapon_system(self, config: SystemConfig) -> IWeaponSystem:
        if config.performance_mode == "high":
            return BasicWeaponSystem(
                config.weapon_manager,
                config.attack_strategy
            )
        elif config.feature_rich_mode:
            return AdvancedWeaponSystem(
                config.weapon_manager,
                config.attack_strategy,
                config.effect_manager
            )
```

### SystemConfig Pattern
```python
@dataclass
class SystemConfig:
    weapon_manager: IWeaponManager
    attack_strategy: IAttackStrategy
    performance_mode: str = "balanced"  # "high", "balanced", "feature_rich"
    feature_rich_mode: bool = False
    effect_manager: IEffectManager | None = None
    
    def validate(self) -> bool:
        return (
            self.weapon_manager is not None
            and self.attack_strategy is not None
            and self.performance_mode in ["high", "balanced", "feature_rich"]
        )
```

## 18. Factory Pattern for Manager Creation

### IManagerFactory Pattern
Central factory interface for creating all manager instances:
```python
from abc import ABC, abstractmethod

class IManagerFactory(ABC):
    @abstractmethod
    def create_enemy_manager(self, config: ManagerConfig) -> IEnemyManager:
        """Create enemy manager based on configuration."""
        pass
    
    @abstractmethod
    def create_weapon_manager(self, config: ManagerConfig) -> IWeaponManager:
        """Create weapon manager based on configuration."""
        pass

class ManagerFactory(IManagerFactory):
    def create_enemy_manager(self, config: ManagerConfig) -> IEnemyManager:
        if config.performance_mode == "high":
            return BasicEnemyManager(config.entity_manager)
        elif config.ai_enabled:
            return AdvancedEnemyManager(config.entity_manager)
        else:
            return BasicEnemyManager(config.entity_manager)
```

### Specialized Factory Interfaces
Domain-specific factories for fine-grained control:
```python
class IEnemyFactory(ABC):
    @abstractmethod
    def create_basic_manager(self, entity_manager: IEntityManager) -> IEnemyManager:
        """Create basic enemy manager (high performance)."""
        pass
    
    @abstractmethod
    def create_advanced_manager(self, entity_manager: IEntityManager) -> IEnemyManager:
        """Create advanced enemy manager (AI features)."""
        pass

class BasicEnemyFactory(IEnemyFactory):
    def create_basic_manager(self, entity_manager: IEntityManager) -> IEnemyManager:
        return BasicEnemyManager(entity_manager)
    
    def create_advanced_manager(self, entity_manager: IEntityManager) -> IEnemyManager:
        return AdvancedEnemyManager(entity_manager)
```

### Factory Configuration Pattern
```python
@dataclass
class ManagerConfig:
    entity_manager: IEntityManager
    performance_mode: str = "balanced"  # "high", "balanced", "feature_rich"
    ai_enabled: bool = False
    difficulty_level: int = 1
    
    def validate(self) -> bool:
        return (
            self.entity_manager is not None
            and self.performance_mode in ["high", "balanced", "feature_rich"]
            and self.difficulty_level > 0
        )
```

### Factory Usage in Systems
```python
# AI-NOTE : 2025-01-26 Factory pattern for manager flexibility
# - Reason: Allow runtime manager implementation selection based on configuration
# - Requirements: Support multiple manager implementations (Basic, Advanced, Physics)
# - History: Replaced direct manager instantiation with factory-based creation
class WeaponSystem(IEventAwareSystem):
    def __init__(self, manager_factory: IManagerFactory, config: ManagerConfig) -> None:
        self._manager_factory = manager_factory
        
        # Factory creates appropriate implementation
        self._weapon_manager = manager_factory.create_weapon_manager(config)
        self._projectile_manager = manager_factory.create_projectile_manager(config)
    
    def reconfigure(self, new_config: ManagerConfig) -> None:
        """Runtime reconfiguration with different manager implementations."""
        self._weapon_manager = self._manager_factory.create_weapon_manager(new_config)
        self._projectile_manager = self._manager_factory.create_projectile_manager(new_config)
```

### Manager Implementation Selection Strategy

#### Performance-Based Selection
```python
class PerformanceManagerFactory(IManagerFactory):
    def create_projectile_manager(self, config: ManagerConfig) -> IProjectileManager:
        # AI-DEV : Performance-based manager selection
        # - Problem: Different gameplay scenarios need different performance characteristics
        # - Solution: Factory selects implementation based on performance requirements
        # - Caution: Ensure feature parity across implementations for seamless switching
        if config.performance_mode == "high":
            return SimpleProjectileManager(config.entity_manager)  # Fast, basic physics
        elif config.performance_mode == "feature_rich":
            return PhysicsProjectileManager(config.entity_manager)  # Full physics simulation
        else:
            return SimpleProjectileManager(config.entity_manager)  # Default to performance
```

#### Feature-Based Selection  
```python
class FeatureManagerFactory(IManagerFactory):
    def create_enemy_manager(self, config: ManagerConfig) -> IEnemyManager:
        if config.ai_enabled and config.difficulty_level >= 3:
            return AdvancedEnemyManager(config.entity_manager)  # AI-driven behavior
        else:
            return BasicEnemyManager(config.entity_manager)     # Simple state machine
```

### Factory Testing Pattern
```python
def test_팩토리_매니저_생성_구현체_선택_성공_시나리오(self) -> None:
    """팩토리가 설정에 따라 올바른 매니저 구현체를 선택하는지 검증"""
    # Given - 서로 다른 설정들
    high_performance_config = ManagerConfig(
        entity_manager=mock_entity_manager,
        performance_mode="high"
    )
    feature_rich_config = ManagerConfig(
        entity_manager=mock_entity_manager,
        performance_mode="feature_rich",
        ai_enabled=True
    )
    
    factory = ManagerFactory()
    
    # When - 팩토리를 통한 매니저 생성
    basic_manager = factory.create_enemy_manager(high_performance_config)
    advanced_manager = factory.create_enemy_manager(feature_rich_config)
    
    # Then - 올바른 구현체 선택 확인
    assert isinstance(basic_manager, BasicEnemyManager), "고성능 설정 시 BasicEnemyManager 선택"
    assert isinstance(advanced_manager, AdvancedEnemyManager), "기능 풍부 설정 시 AdvancedEnemyManager 선택"
```

## 19. Naming Conventions (Updated for Factory Pattern)

- **Factory Interfaces**: `I` prefix + domain + `Factory` (IEnemyFactory, IManagerFactory)
- **Factory Implementations**: Domain + `Factory` (BasicEnemyFactory, AdvancedWeaponFactory)
- **Configuration Classes**: Domain + `Config` (ManagerConfig, SystemConfig)
- **Implementation Classes**: Adjective + Domain + `Manager` (BasicEnemyManager, AdvancedWeaponManager)

## 20. Refactor-PRD.md Specific Architecture Rules

### Phase-Based Development Constraints
```python
# AI-NOTE : 2025-08-27 영향도 기반 리팩토링 순서 적용
# - 이유: Entity → Component → System → Manager/Event/Strategy 순서로 연쇄 변경 최소화
# - 요구사항: refactor-PRD.md의 4단계 Phase 적용
# - 히스토리: 기존 무작정 리팩토링에서 영향도 분석 기반 체계적 접근으로 변경

# Phase 1: Entity 리팩토링 (최우선 - 65개 참조)
class Entity:
    def __init__(self) -> None:
        # 순수 Entity 기능만 유지
        pass

# Phase 2: Component 리팩토링 (두 번째 - 109개 참조) 
class Component(ABC):
    @abstractmethod
    def validate(self) -> bool:
        # 컴포넌트별 검증 로직 필수
        pass

# Phase 3: System 기본 리팩토링 (세 번째 - 26개 참조)
class ISystem(ABC):
    @abstractmethod
    def update(self, delta_time: float) -> None:
        # AI-NOTE : entity_manager 파라미터 제거됨 (Phase 4A에서 적용)
        pass

# Phase 4: Manager/Event/Strategy (네 번째 - 20개 참조)
class IEnemyManager(ABC):
    @abstractmethod
    def create_enemy(self, dto: EnemyCreateDTO) -> str:
        # DTO 기반 타입 안전한 데이터 전송
        pass
```

### TDD 6단계 프로세스 (Phase 4 적용)
```python
# AI-DEV : Phase 4에서 TDD 6단계 프로세스 강제 적용
# - 문제: 복잡한 이벤트 시스템과 Strategy 패턴 구현 시 오류 발생 위험
# - 해결책: 1)인터페이스 구현 → 2)기존 테스트 분석 → 3)사용자 인터뷰 → 4)테스트 구현 → 5)리팩토링 → 6)품질 검증
# - 주의사항: AI는 테스트 케이스 수정 금지, 반드시 사용자 승인 필요

class WeaponSystem(IEventAwareSystem):
    """TDD 6단계 적용된 시스템 구현 예시"""
    
    def __init__(self, strategy: IAttackStrategy) -> None:
        # 1단계: 인터페이스 먼저 정의됨
        self._strategy = strategy
    
    def update(self, delta_time: float) -> None:
        # 5단계: 테스트 기반으로 리팩토링 진행
        pass
```

### Forbidden Dependencies (refactor-PRD.md)
```python
# ❌ FORBIDDEN - Phase별 의존성 위반
class EnemyManager(IEnemyManager):
    def update_ai(self) -> None:
        # Phase 4에서 Manager가 System 직접 호출 금지
        weapon_system.attack()  # VIOLATION

# ❌ FORBIDDEN - 순수 EntityManager 위반
class EntityManager:
    def create_specialized_enemy(self) -> Entity:
        # 순수 CRUD만 허용, 특수 생성 로직 금지
        enemy_component = EnemyComponent()  # VIOLATION

# ✅ CORRECT - SharedEventQueue 기반 통신
class WeaponSystem(IEventAwareSystem):
    def update(self, delta_time: float) -> None:
        # SharedEventQueue 직접 연결 방식
        producer = self._tunnel_manager.get_producer(WeaponAttackEvent)
        producer.produce(WeaponAttackEvent(weapon_id, target_id))
```

## 21. Code Quality Checklist (Updated for Factory Pattern)

Before committing, verify:
- [ ] All functions have complete type hints using Python 3.13+ syntax
- [ ] All managers implement interface contracts (I* interfaces)
- [ ] All managers are created through factory interfaces (no direct instantiation)
- [ ] Factory interfaces provide implementation selection logic
- [ ] Configuration classes include validate() methods
- [ ] DTO classes include validate() methods
- [ ] System classes inherit from ISystem or IEventAwareSystem
- [ ] No forbidden dependency violations (Manager→System, ECS→Manager)
- [ ] Game values use appropriate IntEnum types (*_type, *_status, *_state, *_mode)
- [ ] Performance-critical code uses enum.value for integer comparisons
- [ ] UI code uses enum.display_name for Korean text display
- [ ] Components use @dataclass with type hints
- [ ] Pure functions separate from state mutation
- [ ] AI comment system appropriately applied (AI-NOTE, AI-DEV)
- [ ] Factory pattern used for manager creation with appropriate configuration
- [ ] `ruff check .` and `ruff format .` pass without errors
- [ ] Interface segregation maintained (single responsibility per interface)

This convention ensures type-safe, performant, and maintainable game code optimized for the refactor-PRD.md SharedEventQueue-based Producer-Consumer architecture with interface-first design and factory pattern integration.

## 22. Component Testing Requirements (Core Integration)

### Required Test Functions for All Components
```python
# AI-NOTE : 2025-08-27 Component 서브클래스 필수 테스트 검증 요구사항
# - 이유: ECS 아키텍처의 데이터 무결성과 시스템 안정성 보장
# - 요구사항: src/core/component.py에 정의된 5개 핵심 함수 테스트 필수
# - 히스토리: 기본 구현만으로는 각 컴포넌트별 특수 규칙 검증 불가능

REQUIRED_TEST_FUNCTIONS = [
    'test_component_validation_success_scenarios',
    'test_component_validation_failure_scenarios', 
    'test_component_serialization_roundtrip',
    'test_component_deserialization_error_handling',
    'test_component_utility_methods_consistency'
]
```

### Component Testing Pattern
```python
class TestHealthComponent:
    def test_component_validation_success_scenarios(self) -> None:
        """유효한 모든 필드 조합에서 True 반환 검증"""
        component = HealthComponent(current=100, maximum=100)
        assert component.validate() is True
    
    def test_component_serialization_roundtrip(self) -> None:
        """component_type 필드가 정확한 클래스명으로 설정되는지 검증"""
        component = HealthComponent(current=80, maximum=100)
        serialized = component.serialize()
        assert serialized['component_type'] == 'HealthComponent'
```