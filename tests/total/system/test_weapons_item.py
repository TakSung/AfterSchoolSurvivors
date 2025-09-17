import pygame
import sys
import os
import math
from dataclasses import dataclass, field

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'src')))

from core.entity_manager import EntityManager
from core.system import ISystem
from components.player_component import PlayerComponent
from components.position_component import PositionComponent
from components.velocity_component import VelocityComponent
from components.sprite_component import SpriteComponent
from components.attack_component import AttackComponent
from components.enums import ItemID
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem

# --- Test-specific Component ---
@dataclass
class WeaponComponent:
    """A component to hold the player's current weapon."""
    weapon_id: ItemID = ItemID.BASEBALL_BAT

# --- Test-specific System ---
class TestPlayerAttackSystem(ISystem):
    """
    A test version of PlayerAttackSystem that handles different weapons.
    """
    def __init__(self):
        self.attack_speed = 4.0  # Attacks per second
        self.last_attack_time = 0

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, PositionComponent, WeaponComponent)
        if not player_entities:
            return

        player_entity = player_entities[0]
        player_pos = entity_manager.get_component(player_entity.id, PositionComponent)
        weapon = entity_manager.get_component(player_entity.id, WeaponComponent)

        now = pygame.time.get_ticks()
        attack_cooldown = 1000 / self.attack_speed
        if now - self.last_attack_time > attack_cooldown:
            self.last_attack_time = now
            self._create_projectile(entity_manager, player_pos, weapon.weapon_id)

    def _create_projectile(self, entity_manager: EntityManager, player_pos: PositionComponent, weapon_id: ItemID):
        projectile_entity = entity_manager.create_entity()
        entity_manager.add_component(projectile_entity.id, PositionComponent(x=player_pos.x, y=player_pos.y))

        mouse_pos = pygame.mouse.get_pos()
        direction_x = mouse_pos[0] - player_pos.x
        direction_y = mouse_pos[1] - player_pos.y
        distance = math.hypot(direction_x, direction_y)
        
        speed = 250 # projectile speed
        if distance > 0:
            vel_x = (direction_x / distance) * speed
            vel_y = (direction_y / distance) * speed
        else:
            vel_x, vel_y = speed, 0
        entity_manager.add_component(projectile_entity.id, VelocityComponent(dx=vel_x, dy=vel_y))

        # Customize projectile based on weapon
        if weapon_id == ItemID.BASEBALL_BAT:
            projectile_surface = pygame.Surface((30, 10), pygame.SRCALPHA)
            projectile_surface.fill((139, 69, 19)) # Brown for bat
            damage = 30
        elif weapon_id == ItemID.BASKETBALL:
            projectile_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(projectile_surface, (255, 140, 0), (10, 10), 10) # Orange for basketball
            damage = 20
        elif weapon_id == ItemID.SOCCER_BALL:
            projectile_surface = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(projectile_surface, (255, 255, 255), (7, 7), 7) # White for soccer ball
            damage = 15
        else: # Default
            projectile_surface = pygame.Surface((10, 5), pygame.SRCALPHA)
            projectile_surface.fill((255, 255, 0)) # Yellow
            damage = 10

        entity_manager.add_component(projectile_entity.id, AttackComponent(damage=damage))
        projectile_rect = projectile_surface.get_rect(center=(player_pos.x, player_pos.y))
        entity_manager.add_component(projectile_entity.id, SpriteComponent(surface=projectile_surface, rect=projectile_rect))
        print(f"Fired {weapon_id.name} projectile.")

def main():
    pygame.init()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test Weapons and Items")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # --- ECS Setup ---
    entity_manager = EntityManager()
    
    # --- Systems ---
    attack_system = TestPlayerAttackSystem()
    movement_system = MovementSystem()
    render_system = RenderSystem(screen)

    # --- Player Entity ---
    player_entity = entity_manager.create_entity()
    entity_manager.add_component(player_entity.id, PlayerComponent())
    entity_manager.add_component(player_entity.id, PositionComponent(x=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT / 2))
    
    # Add a simple sprite for the player
    player_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.polygon(player_surface, (0, 255, 0), [(20, 0), (0, 40), (40, 40)])
    player_rect = player_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    entity_manager.add_component(player_entity.id, SpriteComponent(surface=player_surface, rect=player_rect))
    
    # Add the custom WeaponComponent
    weapon_component = WeaponComponent(weapon_id=ItemID.BASEBALL_BAT)
    entity_manager.add_component(player_entity.id, weapon_component)

    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    weapon_component.weapon_id = ItemID.BASEBALL_BAT
                    print("Switched to Baseball Bat")
                elif event.key == pygame.K_2:
                    weapon_component.weapon_id = ItemID.BASKETBALL
                    print("Switched to Basketball")
                elif event.key == pygame.K_3:
                    weapon_component.weapon_id = ItemID.SOCCER_BALL
                    print("Switched to Soccer Ball")

        # --- System Updates ---
        attack_system.update(entity_manager, delta_time)
        movement_system.update(entity_manager, delta_time)
        
        # --- Rendering ---
        screen.fill((30, 30, 30)) # Dark grey background
        render_system.update(entity_manager, delta_time)

        # --- UI Text ---
        weapon_text = font.render(f"Weapon: {weapon_component.weapon_id.name}", True, (255, 255, 255))
        controls_text = font.render("Keys 1, 2, 3 to switch. Mouse to aim.", True, (200, 200, 200))
        screen.blit(weapon_text, (10, 10))
        screen.blit(controls_text, (10, 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
