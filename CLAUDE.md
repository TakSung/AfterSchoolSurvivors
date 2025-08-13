# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment Setup

### Prerequisites
- Python 3.13+
- Conda for environment management

### Environment Setup
```bash
# Clone and set up environment
git clone https://github.com/TakSung/AfterSchoolSurvivors.git
cd AfterSchoolSurvivors
conda create -y -n as-game python=3.13
conda activate as-game

# Install core dependencies
conda install conda-forge::pygame
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

## Development Commands

### Code Quality and Testing
```bash
# Lint and format code (primary tool)
ruff check --fix .
ruff format .

# Type checking
mypy src/

# Run tests
pytest

# Memory profiling (for performance optimization)
python -m memory_profiler src/main.py
```

### Running the Game
```bash
# Run main game
python src/main.py

# With memory profiling
python -m memory_profiler src/main.py
```

## Project Architecture

### Game Concept
"방과 후 생존" (After School Survivors) - A 10-minute hyper-casual roguelike game where players survive waves of teachers using automatic movement and combat.

### Current Architecture
- **Single file implementation**: All game logic currently in `src/main.py`
- **Pygame-based**: Uses pygame for rendering, input, and game loop
- **Simple player system**: Mouse-following movement with auto-rotation
- **Target performance**: 40+ FPS for smooth gameplay

### Planned ECS Architecture (From PRD)
The codebase is intended to evolve toward an Entity-Component-System (ECS) pattern:

- **Entities**: Player, Enemies (Korean Teacher, Math Teacher, Principal), Items, Traps
- **Components**: Position, Health, Movement, Weapon, Collision, Render
- **Systems**: Movement, Combat, Collision Detection, Rendering, Item Management

### Performance Targets
- Maintain 40+ FPS during gameplay
- Handle large numbers of entities efficiently
- Memory-conscious entity lifecycle management

## Code Conventions

### Core Principles
1. **Type Safety**: All functions require type hints using Python 3.13+ native syntax
2. **Performance-First Enums**: Use IntEnum with multi-layer patterns (value for computation, display_name for UI)
3. **ECS Architecture**: Separate components from systems, prefer pure functions
4. **Korean Language Support**: Test methods and game content in Korean

### Enum Patterns
Use enums for all state variables with specific suffixes:
```python
# Performance-optimized pattern
class WeaponType(IntEnum):
    BASIC = 0
    RAPID_FIRE = 1
    
    @property
    def display_name(self) -> str:
        return ["Basic Shot", "Rapid Fire"][self.value]
    
    @property 
    def damage_multiplier(self) -> float:
        return [1.0, 0.7][self.value]
```

### Component Structure
```python
@dataclass
class WeaponComponent:
    weapon_type: WeaponType
    damage: int
    attack_speed: float
```

### Testing Conventions
- Use Korean test method names: `test_엔티티_생성_성공_시나리오`
- Helper classes use `Mock*` prefix (never `Test*` to avoid pytest warnings)
- 5-step docstring structure for all tests
- Include AI-DEV comments for technical decisions

## Ruff Configuration
The project uses Ruff for linting and formatting with these key settings:
- Line length: 79 characters
- Target version: Python 3.13
- Quote style: Single quotes
- Comprehensive rule set including security (S), type annotations (ANN), and performance (UP)

## Game Development Guidelines

### Item System (Planned)
- 7 total items: 3 weapons (Soccer Ball, Basketball, Baseball Bat), 4 abilities (Soccer Shoes, Basketball Shoes, Red Ginseng, Milk)
- Synergy combinations for enhanced effects
- Maximum 6 item slots, up to level 5 per item

### Enemy Types (Planned)
- Korean Teacher: Slow movement, wide area attacks
- Math Teacher: Fast movement, linear charge attacks  
- Principal: Boss-level, periodic appearances

### Performance Requirements
- Target 60 FPS with 50+ entities
- Memory leak prevention for entity creation/destruction
- Optimized collision detection for game objects

## AI Development Rules

### Code Writing
- Follow `ai/rules/code-convention-rule.md` for Python conventions
- Implement ECS patterns for game architecture
- Use performance-optimized enums for game state management

### Testing
- Follow `ai/rules/unit-test-rule.md` for pytest conventions
- Write Korean test names with scenario suffixes
- Include memory and performance tests for game systems

### Comments and Documentation
- Follow `ai/rules/AI_COMMENT_GUIDELINES.md`
- Use AI-DEV comments for technical decision documentation
- Korean language support for game content and UI

## File Structure
```
src/                    # Source code
  main.py              # Main game entry point
ai/                    # AI development rules and commands
  rules/               # Development conventions
  commands/            # AI task templates
docs/                  # Game design documents
  PRD.md              # Product Requirements Document
tests/                 # Test files (when created)
requirements.txt       # Python dependencies
pyproject.toml        # Build and tool configuration
```