# AI-NOTE : 2025-09-03 'interview-gui-test'를 통해 생성된 시각적 통합 테스트
# - 목적: PlayerAttackSystem, CollisionSystem, PlayerLevelSystem의 상호작용을 시각적으로 검증
# - 요구사항: 플레이어가 자동으로 적을 공격하고, 경험치를 얻어 레벨업하는 전체 과정을 테스트
# - 제어 기능:
#   - 마우스 클릭: 적 생성
#   - 'R' 키: 테스트 리셋
#   - 'K' 키: 모든 적 제거
#   - 'X' 키: 경험치 10 추가

import math

# Add src to path to import components and systems
import os
import random
import sys

import pygame

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../src'))

from components.enemy_component import EnemyComponent
from components.enums import EnemyType, EntityStatus
from components.health_component import HealthComponent

# Components
from components.player_component import PlayerComponent
from components.position_component import PositionComponent
from components.sprite_component import SpriteComponent
from components.velocity_component import VelocityComponent
from core.entity import Entity
from core.entity_manager import EntityManager
from systems.collision_system import CollisionSystem
from systems.movement_system import MovementSystem

# Systems
from systems.player_attack_system import PlayerAttackSystem
from systems.player_level_system import PlayerLevelSystem
from systems.render_system import RenderSystem

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
PLAYER_SIZE = 32
ENEMY_SIZE = 32
PROJECTILE_SIZE = (10, 10)
EXP_ORB_SIZE = 10

# Colors
COLOR_PLAYER = (0, 255, 0)  # Green
COLOR_ENEMY = (255, 0, 0)  # Red
COLOR_PROJECTILE = (255, 255, 0)  # Yellow
COLOR_EXP_ORB = (0, 0, 255)  # Blue


class VisualIntegrationTest:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Visual Integration Test: Player Systems')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        self.entity_manager = EntityManager()
        self.player_attack_system = PlayerAttackSystem()
        self.collision_system = CollisionSystem()
        self.player_level_system = PlayerLevelSystem()
        self.movement_system = MovementSystem()
        self.render_system = RenderSystem(self.screen)

        self.player_entity: Entity | None = None
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 2000  # ms

    def create_sprite(
        self,
        shape: str,
        color: tuple[int, int, int],
        size: int | tuple[int, int],
    ) -> pygame.Surface:
        """Creates a surface for a sprite based on shape and color."""
        if isinstance(size, int):
            size = (size, size)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        if shape == 'circle':
            pygame.draw.circle(
                surface, color, (size[0] // 2, size[1] // 2), size[0] // 2
            )
        elif shape == 'rect':
            surface.fill(color)
        return surface

    def reset_game(self):
        """Resets the test to its initial state."""
        print('--- RESETTING TEST ---')
        # self.entity_manager.clear()

        # Create Player
        self.player_entity = self.entity_manager.create_entity()
        player_id = self.player_entity.id
        self.entity_manager.add_component(player_id, PlayerComponent())
        self.entity_manager.add_component(
            player_id,
            PositionComponent(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2),
        )
        self.entity_manager.add_component(
            player_id,
            HealthComponent(
                current=100, maximum=100, status=EntityStatus.ALIVE
            ),
        )
        self.entity_manager.add_component(
            player_id, VelocityComponent(dx=0, dy=0)
        )

        player_sprite_surface = self.create_sprite(
            'circle', COLOR_PLAYER, PLAYER_SIZE
        )
        player_rect = player_sprite_surface.get_rect(
            center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        )
        self.entity_manager.add_component(
            player_id,
            SpriteComponent(surface=player_sprite_surface, rect=player_rect),
        )

        # Spawn initial enemies
        for _ in range(5):
            self.create_enemy()

    def create_enemy(self, position: tuple[int, int] | None = None):
        """Creates an enemy entity."""
        enemy = self.entity_manager.create_entity()
        enemy_id = enemy.id

        if position is None:
            # Spawn from a random edge
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top':
                x, y = random.randint(0, SCREEN_WIDTH), 0
            elif edge == 'bottom':
                x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT
            elif edge == 'left':
                x, y = 0, random.randint(0, SCREEN_HEIGHT)
            else:  # right
                x, y = SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)
        else:
            x, y = position

        self.entity_manager.add_component(
            enemy_id, EnemyComponent(enemy_type=EnemyType.KOREAN_TEACHER)
        )
        self.entity_manager.add_component(
            enemy_id, PositionComponent(x=x, y=y)
        )
        self.entity_manager.add_component(
            enemy_id,
            HealthComponent(current=50, maximum=50, status=EntityStatus.ALIVE),
        )

        # Velocity towards player
        if self.player_entity:
            player_pos = self.entity_manager.get_component(
                self.player_entity.id, PositionComponent
            )
            if player_pos:
                dx = player_pos.x - x
                dy = player_pos.y - y
                dist = math.hypot(dx, dy)
                speed = random.uniform(50, 100)
                vel_x = (dx / dist) * speed if dist > 0 else 0
                vel_y = (dy / dist) * speed if dist > 0 else 0
                self.entity_manager.add_component(
                    enemy_id, VelocityComponent(dx=vel_x, dy=vel_y)
                )

        enemy_sprite_surface = self.create_sprite(
            'rect', COLOR_ENEMY, ENEMY_SIZE
        )
        enemy_rect = enemy_sprite_surface.get_rect(center=(x, y))
        self.entity_manager.add_component(
            enemy_id,
            SpriteComponent(surface=enemy_sprite_surface, rect=enemy_rect),
        )

    def run(self):
        """Main test loop."""
        self.reset_game()
        running = True
        last_time = pygame.time.get_ticks()
        PLAYER_SPEED = 200

        while running:
            now = pygame.time.get_ticks()
            delta_time = (now - last_time) / 1000.0
            last_time = now

            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                player_vel = (
                    self.entity_manager.get_component(
                        self.player_entity.id, VelocityComponent
                    )
                    if self.player_entity
                    else None
                )

                if event.type == pygame.KEYDOWN:
                    # Player Movement
                    if player_vel:
                        if event.key == pygame.K_LEFT:
                            player_vel.dx = -PLAYER_SPEED
                        elif event.key == pygame.K_RIGHT:
                            player_vel.dx = PLAYER_SPEED
                        elif event.key == pygame.K_UP:
                            player_vel.dy = -PLAYER_SPEED
                        elif event.key == pygame.K_DOWN:
                            player_vel.dy = PLAYER_SPEED

                    # Test Controls
                    if event.key == pygame.K_r:
                        self.reset_game()
                    if event.key == pygame.K_k:
                        print('--- Clearing all enemies ---')
                        for (
                            entity
                        ) in self.entity_manager.get_entities_with_components(
                            EnemyComponent
                        ):
                            self.entity_manager.destroy_entity(entity.id)
                    if event.key == pygame.K_x:
                        if self.player_entity:
                            player_comp = self.entity_manager.get_component(
                                self.player_entity.id, PlayerComponent
                            )
                            if player_comp:
                                player_comp.experience += 10
                                print(
                                    f'--- Added 10 EXP. Total EXP: {player_comp.experience} ---'
                                )

                if event.type == pygame.KEYUP:
                    if player_vel:
                        if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                            player_vel.dx = 0
                        if event.key in [pygame.K_UP, pygame.K_DOWN]:
                            player_vel.dy = 0

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.create_enemy(event.pos)

            # --- Automatic Enemy Spawning ---
            self.enemy_spawn_timer += delta_time * 1000
            if self.enemy_spawn_timer > self.enemy_spawn_interval:
                self.enemy_spawn_timer = 0
                self.create_enemy()

            # --- System Updates ---
            self.player_attack_system.update(self.entity_manager, delta_time)
            self.movement_system.update(self.entity_manager, delta_time)
            self.collision_system.update(self.entity_manager, delta_time)
            self.player_level_system.update(self.entity_manager, delta_time)

            # --- Rendering ---
            self.render_system.update(self.entity_manager, delta_time)

            self.draw_ui()
            pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def draw_ui(self):
        """Draws additional UI for test controls."""
        controls = [
            'Controls:',
            '  Arrow Keys: Move Player',
            '  Mouse Click: Spawn Enemy',
            "  'R': Reset Test",
            "  'K': Kill All Enemies",
            "  'X': Add 10 EXP",
        ]
        for i, line in enumerate(controls):
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, 10 + i * 25))


if __name__ == '__main__':
    test = VisualIntegrationTest()
    test.run()
