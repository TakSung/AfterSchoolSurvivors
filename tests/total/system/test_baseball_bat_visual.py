
import pygame
import sys
import os
import math
from dataclasses import dataclass

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

from core.entity_manager import EntityManager
from components.position_component import PositionComponent
from components.health_component import HealthComponent
from components.sprite_component import SpriteComponent
from entities.weapons import BaseballBat

# --- Test-specific Components and Systems ---

@dataclass
class MockEnemy:
    """A simple data class for a mock enemy."""
    id: int
    health: HealthComponent
    pos: PositionComponent

@dataclass
class MockBaseballBat:
    """A mock for the baseball bat item."""
    level: int = 0

    def level_up(self):
        self.level += 1

class TestGame:
    """A class to manage the test setup and game loop."""
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Visual Test for Baseball Bat")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)

        self.entity_manager = EntityManager()
        self.player_pos = PositionComponent(x=self.screen_width / 2, y=self.screen_height / 2)
        self.bat = MockBaseballBat()
        self.enemies: list[MockEnemy] = []
        self.damage_texts: list[tuple[str, tuple[int, int], float]] = []

        self._setup_test_entities()

    def _setup_test_entities(self):
        """Creates the player and enemies for the test."""
        # Player is conceptually at the center, no entity needed for this test

        # Enemy inside 90-degree attack arc (in front of player)
        enemy_in_range = self.entity_manager.create_entity()
        pos_in = PositionComponent(x=self.player_pos.x, y=self.player_pos.y - 100)
        health_in = HealthComponent(base_maximum=50, current=50, maximum=50)
        self.enemies.append(MockEnemy(id=enemy_in_range.id, health=health_in, pos=pos_in))

        # Enemy outside 90-degree attack arc (behind player)
        enemy_out_of_range = self.entity_manager.create_entity()
        pos_out = PositionComponent(x=self.player_pos.x, y=self.player_pos.y + 100)
        health_out = HealthComponent(base_maximum=50, current=50, maximum=50)
        self.enemies.append(MockEnemy(id=enemy_out_of_range.id, health=health_out, pos=pos_out))

    def handle_input(self, event):
        """Handles user input for the test."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if self.bat.level == 0:
                    self.bat.level = 1
                else:
                    self.bat.level_up()
                print(f"Baseball Bat leveled up to {self.bat.level}")
            elif event.key == pygame.K_SPACE:
                self.perform_attack()
                print("Attack performed.")

    def perform_attack(self):
        """Simulates a baseball bat attack."""
        mouse_pos = pygame.mouse.get_pos()
        attack_angle_rad = math.atan2(mouse_pos[1] - self.player_pos.y, mouse_pos[0] - self.player_pos.x)

        for enemy in self.enemies:
            enemy_angle_rad = math.atan2(enemy.pos.y - self.player_pos.y, enemy.pos.x - self.player_pos.x)
            angle_diff = abs(math.degrees(attack_angle_rad - enemy_angle_rad))
            if angle_diff > 180:
                angle_diff = 360 - angle_diff

            # Check if within 90-degree arc (45 degrees on each side)
            if angle_diff <= 45:
                damage = 10 * self.bat.level # Level-based damage
                enemy.health.current -= damage
                # Add damage text to be rendered
                text_pos = (int(enemy.pos.x), int(enemy.pos.y - 20))
                self.damage_texts.append((str(damage), text_pos, pygame.time.get_ticks()))

    def update(self):
        """Updates the state of damage texts."""
        now = pygame.time.get_ticks()
        # Remove damage texts that have been displayed for more than 0.5 seconds
        self.damage_texts = [dt for dt in self.damage_texts if now - dt[2] < 500]

    def render(self):
        """Renders the game state to the screen."""
        self.screen.fill((10, 10, 30)) # Dark blue background

        # Draw player
        pygame.draw.circle(self.screen, (0, 200, 0), (int(self.player_pos.x), int(self.player_pos.y)), 15)

        # Draw enemies
        for enemy in self.enemies:
            color = (200, 0, 0) if enemy.health.current > 0 else (80, 80, 80)
            pygame.draw.rect(self.screen, color, (enemy.pos.x - 10, enemy.pos.y - 10, 20, 20))

        # Draw damage texts
        for text, pos, start_time in self.damage_texts:
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, pos)

        # --- Render UI based on requirements ---
        # 1. Bat Level
        level_text = f"Baseball Bat Level: {self.bat.level}"
        level_surface = self.font.render(level_text, True, (255, 255, 255))
        self.screen.blit(level_surface, (self.screen_width - level_surface.get_width() - 10, self.screen_height - level_surface.get_height() - 10))

        # 2. Enemy Health Info
        for i, enemy in enumerate(self.enemies):
            health_text = f"Enemy {i+1} Health: {enemy.health.current}/{enemy.health.maximum}"
            health_surface = self.font.render(health_text, True, (200, 200, 200))
            self.screen.blit(health_surface, (10, 10 + i * 30))
            
        # 3. Instructions
        instructions = [
            "--- CONTROLS ---",
            "1: Level up Bat",
            "SPACE: Attack towards mouse",
            "ESC: Quit"
        ]
        for i, line in enumerate(instructions):
            inst_surface = self.font.render(line, True, (255, 215, 0))
            self.screen.blit(inst_surface, (10, 100 + i * 30))

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
    test_game = TestGame()
    test_game.run()

if __name__ == "__main__":
    main()
