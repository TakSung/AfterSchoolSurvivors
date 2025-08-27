
import pygame
import random
import sys
import os
import math

# Add the src directory to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

from core.entity_manager import EntityManager
from components.player_component import PlayerComponent
from components.position_component import PositionComponent
from components.velocity_component import VelocityComponent
from components.enemy_component import EnemyComponent
from components.enums import EnemyType
from systems.enemy_movement_system import EnemyMovementSystem

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

def main():
    """Main function to run the Pygame test for EnemyMovementSystem."""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Enemy Movement System Test")
    clock = pygame.time.Clock()

    # --- ECS Setup ---
    entity_manager = EntityManager()
    enemy_movement_system = EnemyMovementSystem()

    # --- Entity Creation ---
    # Create Player Entity
    player_entity = entity_manager.create_entity()
    entity_manager.add_component(player_entity.id, PlayerComponent())
    player_pos = PositionComponent(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2)
    entity_manager.add_component(player_entity.id, player_pos)
    entity_manager.add_component(player_entity.id, VelocityComponent(dx=0, dy=0))

    # Create Enemy Entities
    for _ in range(5):
        enemy_entity = entity_manager.create_entity()
        entity_manager.add_component(enemy_entity.id, EnemyComponent(enemy_type=EnemyType.KOREAN_TEACHER, speed=random.uniform(1.5, 2.5)))
        enemy_pos = PositionComponent(x=random.randint(0, SCREEN_WIDTH), y=random.randint(0, SCREEN_HEIGHT))
        entity_manager.add_component(enemy_entity.id, enemy_pos)
        entity_manager.add_component(enemy_entity.id, VelocityComponent(dx=0, dy=0))

    # --- Game Loop Variables ---
    running = True
    player_target_pos = (player_pos.x, player_pos.y)
    player_move_timer = 0
    PLAYER_MOVE_INTERVAL = 10000  # 10 seconds in milliseconds

    # --- Main Game Loop ---
    while running:
        delta_time = clock.tick(60) / 1000.0

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- Player Position Update ---
        player_move_timer += clock.get_time()
        if player_move_timer > PLAYER_MOVE_INTERVAL:
            player_move_timer = 0
            player_target_pos = (random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 100))
            player_pos.x, player_pos.y = player_target_pos
            print(f"Player teleported to: {player_target_pos}")

        # --- ECS System Update ---
        enemy_movement_system.update(entity_manager, delta_time)

        # --- Physics Update (apply velocities) ---
        for entity in entity_manager.get_entities_with_components(PositionComponent, VelocityComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            vel = entity_manager.get_component(entity.id, VelocityComponent)
            if pos and vel:
                pos.x += vel.dx * 100 * delta_time # Multiply by a factor to make speed visible
                pos.y += vel.dy * 100 * delta_time

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw Player
        player_draw_pos = (int(player_pos.x), int(player_pos.y))
        pygame.draw.circle(screen, GREEN, player_draw_pos, 15)

        # Draw Enemies
        for entity in entity_manager.get_entities_with_components(EnemyComponent, PositionComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            if pos:
                enemy_draw_pos = (int(pos.x), int(pos.y))
                pygame.draw.circle(screen, RED, enemy_draw_pos, 10)
                # Draw line to player
                pygame.draw.line(screen, WHITE, enemy_draw_pos, player_draw_pos, 1)


        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
