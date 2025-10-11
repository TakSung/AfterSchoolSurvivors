import pygame
import sys
import os
import math
import random
from dataclasses import dataclass, field

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

from core.entity_manager import EntityManager
from components.player_component import PlayerComponent
from components.position_component import PositionComponent
from components.velocity_component import VelocityComponent
from components.sprite_component import SpriteComponent
from components.attack_component import AttackComponent
from components.inventory_component import InventoryComponent
from components.health_component import HealthComponent
from components.hitbox_component import HitboxComponent
from components.enemy_component import EnemyComponent
from components.enums import ItemID, EnemyType
from entities.weapons import BaseballBat
from entities.enemy import Enemy
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem
from systems.item_system import ItemSystem
from systems.player_attack_system import PlayerAttackSystem
from systems.collision_system import CollisionSystem
from systems.enemy_movement_system import EnemyMovementSystem
from utils.coordinates import to_pygame_angle


def main():
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Baseball Bat Integration Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    # --- ECS Setup ---
    entity_manager = EntityManager()
    
    # --- Systems ---
    item_system = ItemSystem(entity_manager)
    attack_system = PlayerAttackSystem()
    collision_system = CollisionSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    movement_system = MovementSystem()
    enemy_movement_system = EnemyMovementSystem()
    render_system = RenderSystem(screen)

    # --- Player Entity ---
    player_entity = entity_manager.create_entity()
    entity_manager.add_component(player_entity.id, PlayerComponent())
    entity_manager.add_component(player_entity.id, PositionComponent(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2))
    entity_manager.add_component(player_entity.id, AttackComponent(base_damage=10, base_attack_speed=1.0))
    
    player_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(player_surface, (0, 255, 0), (15, 15), 15)
    player_rect = player_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    entity_manager.add_component(player_entity.id, SpriteComponent(surface=player_surface, rect=player_rect))
    
    inventory_component = InventoryComponent()
    baseball_bat_item = BaseballBat(level=1)
    inventory_component.add_item(baseball_bat_item)
    entity_manager.add_component(player_entity.id, inventory_component)

    # --- Enemy Entities ---
    for _ in range(10):
        enemy_obj = Enemy.create_enemy_by_type(EnemyType.KOREAN_TEACHER)
        enemy_entity = enemy_obj.create_entity(entity_manager)
        
        enemy_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(enemy_surface, (255, 0, 0), (12, 12), 12)
        pos = entity_manager.get_component(enemy_entity.id, PositionComponent)
        enemy_rect = enemy_surface.get_rect(center=(pos.x, pos.y))
        entity_manager.add_component(enemy_entity.id, SpriteComponent(surface=enemy_surface, rect=enemy_rect))

    running = True
    while running:
        delta_time = clock.tick(60) / 500.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_5:
                    new_level = event.key - pygame.K_0
                    baseball_bat_item.level = new_level
                    print(f"Set Baseball Bat to Level {new_level}")

        # --- System Updates ---
        item_system.update(delta_time)
        enemy_movement_system.update(entity_manager, delta_time)
        attack_system.update(entity_manager, delta_time)
        movement_system.update(entity_manager, delta_time)
        collision_system.update(entity_manager, delta_time)
        
        # --- Rendering ---
        screen.fill((30, 30, 30)) # Dark grey background
        render_system.update(entity_manager, delta_time)

        # --- Debug Visuals ---
        # Draw Hitbox
        for hitbox_entity in entity_manager.get_entities_with_components(HitboxComponent):
            hitbox = entity_manager.get_component(hitbox_entity.id, HitboxComponent)
            pos = entity_manager.get_component(hitbox_entity.id, PositionComponent)
            
            # Visualize the fan-shaped hitbox
            arc_rect = pygame.Rect(pos.x - hitbox.width, pos.y - hitbox.width, hitbox.width * 2, hitbox.width * 2)
            visual_angle_deg = to_pygame_angle(hitbox.angle)
            start_angle_rad = math.radians(visual_angle_deg - hitbox.height / 2)
            end_angle_rad = math.radians(visual_angle_deg + hitbox.height / 2)
            
            pygame.draw.arc(screen, (255, 255, 0), arc_rect, start_angle_rad, end_angle_rad, 2)

        # Draw Health Bars
        for enemy in entity_manager.get_entities_with_components(EnemyComponent, HealthComponent, PositionComponent):
            health = entity_manager.get_component(enemy.id, HealthComponent)
            pos = entity_manager.get_component(enemy.id, PositionComponent)
            
            max_health = health.maximum
            current_health = health.current
            
            bar_width = 30
            bar_height = 5
            health_pct = current_health / max_health
            
            background_rect = pygame.Rect(pos.x - bar_width / 2, pos.y - 25, bar_width, bar_height)
            health_rect = pygame.Rect(pos.x - bar_width / 2, pos.y - 25, bar_width * health_pct, bar_height)
            
            pygame.draw.rect(screen, (100, 0, 0), background_rect)
            pygame.draw.rect(screen, (0, 200, 0), health_rect)

        # --- UI Text ---
        player_attack_comp = entity_manager.get_component(player_entity.id, AttackComponent)
        level_text = font.render(f"Bat Level: {baseball_bat_item.level} (Keys 1-5)", True, (255, 255, 255))
        speed_text = font.render(f"Attack Speed: {player_attack_comp.attack_speed:.2f}", True, (255, 255, 255))
        angle_text = font.render(f"Attack Angle: {player_attack_comp.angle}", True, (255, 255, 255))
        
        screen.blit(level_text, (10, 10))
        screen.blit(speed_text, (10, 40))
        screen.blit(angle_text, (10, 70))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
