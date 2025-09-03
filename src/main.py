import pygame

from core.entity_manager import EntityManager
from components.player_component import PlayerComponent
from components.position_component import PositionComponent
from components.velocity_component import VelocityComponent
from components.health_component import HealthComponent
from components.sprite_component import SpriteComponent
from components.enums import EntityStatus
from systems.input_system import InputSystem
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem
from systems.collision_system import CollisionSystem
from systems.enemy_movement_system import EnemyMovementSystem
from systems.enemy_spawner_system import EnemySpawnerSystem
from systems.player_attack_system import PlayerAttackSystem
from systems.player_level_system import PlayerLevelSystem

def main():
    pygame.init()

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("After School Survivors")

    clock = pygame.time.Clock()
    FPS = 60

    # ECS setup
    entity_manager = EntityManager()

    # Create systems
    input_system = InputSystem()
    movement_system = MovementSystem()
    render_system = RenderSystem(screen)
    collision_system = CollisionSystem()
    enemy_movement_system = EnemyMovementSystem()
    enemy_spawner_system = EnemySpawnerSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    player_attack_system = PlayerAttackSystem()
    player_level_system = PlayerLevelSystem()

    # Create player entity
    player_entity = entity_manager.create_entity()
    entity_manager.add_component(player_entity.id, PositionComponent(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2))
    entity_manager.add_component(player_entity.id, VelocityComponent(dx=0, dy=0))
    entity_manager.add_component(player_entity.id, HealthComponent(current=100, maximum=100, status=EntityStatus.ALIVE))
    entity_manager.add_component(player_entity.id, PlayerComponent())
    try:
        player_surface = pygame.image.load("assets/player.svg").convert_alpha()
        player_surface = pygame.transform.scale(player_surface, (50, 50))
    except pygame.error:
        print("Player sprite 'assets/player.svg' not found. Using fallback triangle.")
        player_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(player_surface, (0, 255, 0), [(50, 25), (0, 0), (0, 50)])
    player_rect = player_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    entity_manager.add_component(player_entity.id, SpriteComponent(surface=player_surface, rect=player_rect))


    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Update systems
        input_system.update(entity_manager, delta_time)
        enemy_spawner_system.update(entity_manager, delta_time)
        enemy_movement_system.update(entity_manager, delta_time)
        player_attack_system.update(entity_manager, delta_time)
        movement_system.update(entity_manager, delta_time)
        collision_system.update(entity_manager, delta_time)
        player_level_system.update(entity_manager, delta_time)

        # Render
        render_system.update(entity_manager, delta_time)

        # Check for game over
        player_health = entity_manager.get_component(player_entity.id, HealthComponent)
        if player_health.status == EntityStatus.DEAD:
            print("Game Over!")
            running = False

    pygame.quit()

if __name__ == "__main__":
    main()