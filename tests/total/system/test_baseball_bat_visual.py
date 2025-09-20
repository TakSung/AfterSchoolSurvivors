import pygame
import sys
import os
import math
from dataclasses import field

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

from core.entity_manager import EntityManager
from core.system import ISystem

# Components
from components.position_component import PositionComponent
from components.health_component import HealthComponent
from components.sprite_component import SpriteComponent
from components.player_component import PlayerComponent
from components.enemy_component import EnemyComponent
from components.attack_component import AttackComponent
from components.enums import EnemyType, EntityStatus

# Entities
from entities.weapons import BaseballBat

# Systems
from systems.player_attack_system import PlayerAttackSystem
from systems.collision_system import CollisionSystem
from systems.render_system import RenderSystem
from systems.movement_system import MovementSystem
from systems.enemy_movement_system import EnemyMovementSystem


class TestGame:
    """
    An integration test class to visually verify the baseball bat's functionality
    within the ECS architecture.
    """
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Integration Test for Baseball Bat")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)

        # ECS setup
        self.entity_manager = EntityManager()
        self.render_system = RenderSystem(self.screen)
        self.player_attack_system = PlayerAttackSystem()
        self.collision_system = CollisionSystem(self.screen_width, self.screen_height)
        self.movement_system = MovementSystem()
        self.enemy_movement_system = EnemyMovementSystem()

        self.player_id = -1
        self.bat_item = BaseballBat()

        self._setup_test_entities()

    def _setup_test_entities(self):
        """Creates the player and enemies for the test."""
        # --- Create Player ---
        player_entity = self.entity_manager.create_entity()
        self.player_id = player_entity.id
        
        player_pos = PositionComponent(x=self.screen_width / 2, y=self.screen_height / 2)
        player_health = HealthComponent(base_maximum=100, current=100, maximum=100)
        player_comp = PlayerComponent()
        
        # Player sprite
        player_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(player_surface, (0, 200, 0), (15, 15), 15)
        player_rect = player_surface.get_rect(center=(player_pos.x, player_pos.y))
        player_sprite = SpriteComponent(surface=player_surface, rect=player_rect)

        # Player attack component
        attack_comp = AttackComponent(
            damage=10, 
            attack_speed=1.0, 
            weapon_type="baseball_bat",
            angle=90
        )

        self.entity_manager.add_component(self.player_id, player_pos)
        self.entity_manager.add_component(self.player_id, player_health)
        self.entity_manager.add_component(self.player_id, player_comp)
        self.entity_manager.add_component(self.player_id, player_sprite)
        self.entity_manager.add_component(self.player_id, attack_comp)

        # --- Create Enemies ---
        positions = [
            (player_pos.x, player_pos.y - 100), # In front
            (player_pos.x, player_pos.y + 100), # Behind
            (player_pos.x - 150, player_pos.y), # Left
            (player_pos.x + 150, player_pos.y), # Right
        ]
        for i, (x, y) in enumerate(positions):
            enemy_entity = self.entity_manager.create_entity()
            enemy_pos = PositionComponent(x=x, y=y)
            enemy_health = HealthComponent(base_maximum=50, current=50, maximum=50)
            enemy_comp = EnemyComponent(enemy_type=EnemyType.KOREAN_TEACHER) # Dummy type
            
            enemy_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.rect(enemy_surface, (200, 0, 0), (0, 0, 20, 20))
            enemy_rect = enemy_surface.get_rect(center=(x, y))
            enemy_sprite = SpriteComponent(surface=enemy_surface, rect=enemy_rect)

            self.entity_manager.add_component(enemy_entity.id, enemy_pos)
            self.entity_manager.add_component(enemy_entity.id, enemy_health)
            self.entity_manager.add_component(enemy_entity.id, enemy_comp)
            self.entity_manager.add_component(enemy_entity.id, enemy_sprite)

    def handle_input(self, event):
        """Handles user input for leveling up the bat."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if self.bat_item.level < self.bat_item.max_level:
                    self.bat_item.level_up()
                    # Update player's attack component with new stats
                    attack_comp = self.entity_manager.get_component(self.player_id, AttackComponent)
                    effect = self.bat_item.get_effect()
                    attack_comp.angle = effect["angle"]
                    attack_comp.attack_speed = 1.0 + effect["attack_speed_increase"]
                    print(f"Baseball Bat leveled up to {self.bat_item.level}. Angle: {attack_comp.angle}, Speed Multi: {attack_comp.attack_speed}")

    def update(self):
        """Run all ECS systems."""
        delta_time = self.clock.get_time() / 1000.0
        self.player_attack_system.update(self.entity_manager, delta_time)
        self.movement_system.update(self.entity_manager, delta_time)
        self.enemy_movement_system.update(self.entity_manager, self.player_id)
        self.collision_system.update(self.entity_manager, delta_time)
        # Render system is called in the main loop's render phase

    def render(self):
        """Render the game and UI information."""
        delta_time = self.clock.get_time() / 1000.0
        self.render_system.update(self.entity_manager, delta_time)
        
        # --- Render UI based on requirements ---
        # 1. Bat Level
        level_text = f"Bat Level: {self.bat_item.level} (Press '1' to Level Up)"
        level_surface = self.font.render(level_text, True, (255, 255, 255))
        self.screen.blit(level_surface, (10, 10))

        # 2. Enemy Health Info
        enemy_entities = self.entity_manager.get_entities_with_components(EnemyComponent, HealthComponent)
        for i, enemy in enumerate(enemy_entities):
            health = self.entity_manager.get_component(enemy.id, HealthComponent)
            health_text = f"Enemy {i+1} Health: {health.current}/{health.maximum}"
            color = (255, 100, 100) if health.current > 0 else (100, 100, 100)
            health_surface = self.font.render(health_text, True, color)
            self.screen.blit(health_surface, (10, 40 + i * 30))
            
        # 3. Instructions
        instructions = [
            "--- VISUAL TEST ---",
            "Bat should swing automatically towards mouse.",
            "Swing arc should be visible.",
            "Enemies in arc should take damage.",
            "Leveling up should increase arc size and speed.",
            "ESC: Quit"
        ]
        for i, line in enumerate(instructions):
            inst_surface = self.font.render(line, True, (255, 215, 0))
            self.screen.blit(inst_surface, (self.screen_width - inst_surface.get_width() - 10, 10 + i * 30))

        pygame.display.flip()

    def run(self):
        """The main game loop for the test."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                self.handle_input(event)

            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

def main():
    if "pygame" not in sys.modules:
        print("Pygame is not installed or could not be imported. Please install it to run this visual test.")
        return
        
    test_game = TestGame()
    test_game.run()

if __name__ == "__main__":
    main()