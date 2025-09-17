import pygame
import math
import random

from core.system import ISystem
from core.entity_manager import EntityManager
from components.player_component import PlayerComponent
from components.position_component import PositionComponent
from components.attack_component import AttackComponent
from components.velocity_component import VelocityComponent
from components.sprite_component import SpriteComponent
from components.projectile_component import ProjectileComponent
from components.hitbox_component import HitboxComponent # Assuming this will be created

class PlayerAttackSystem(ISystem):
    def __init__(self):
        self.last_attack_time = 0

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, PositionComponent, AttackComponent)
        if not player_entities:
            return

        player_entity = player_entities[0]
        player_pos = entity_manager.get_component(player_entity.id, PositionComponent)
        attack_comp = entity_manager.get_component(player_entity.id, AttackComponent)
        player_comp = entity_manager.get_component(player_entity.id, PlayerComponent)

        now = pygame.time.get_ticks()
        attack_cooldown = 1000 / attack_comp.attack_speed if attack_comp.attack_speed > 0 else float('inf')

        # Synergy: Baseball bat swing on jump land
        if player_comp.trigger_bat_swing:
            self._attack_baseball_bat(entity_manager, player_pos, attack_comp)
            player_comp.trigger_bat_swing = False

        if now - self.last_attack_time > attack_cooldown:
            self.last_attack_time = now
            
            if attack_comp.weapon_type == "soccer_ball":
                self._attack_soccer_ball(entity_manager, player_pos, attack_comp, player_entity.id)
            elif attack_comp.weapon_type == "basketball":
                self._attack_basketball(entity_manager, player_pos, attack_comp, player_entity.id)
            elif attack_comp.weapon_type == "baseball_bat":
                self._attack_baseball_bat(entity_manager, player_pos, attack_comp)

    def _get_mouse_direction(self, player_pos: PositionComponent) -> tuple[float, float]:
        mouse_pos = pygame.mouse.get_pos()
        direction_x = mouse_pos[0] - player_pos.x
        direction_y = mouse_pos[1] - player_pos.y
        distance = (direction_x ** 2 + direction_y ** 2) ** 0.5
        if distance > 0:
            return (direction_x / distance, direction_y / distance)
        return (1, 0) # Default direction

    def _attack_soccer_ball(self, entity_manager: EntityManager, player_pos: PositionComponent, attack_comp: AttackComponent, owner_id: int):
        dir_x, dir_y = self._get_mouse_direction(player_pos)
        
        for i in range(attack_comp.projectiles):
            # Add some spread to the projectiles
            angle_offset = math.radians(random.uniform(-15, 15))
            new_dir_x = dir_x * math.cos(angle_offset) - dir_y * math.sin(angle_offset)
            new_dir_y = dir_x * math.sin(angle_offset) + dir_y * math.cos(angle_offset)

            projectile_entity = entity_manager.create_entity()
            entity_manager.add_component(projectile_entity.id, PositionComponent(x=player_pos.x, y=player_pos.y))
            entity_manager.add_component(projectile_entity.id, VelocityComponent(dx=new_dir_x * 10, dy=new_dir_y * 10))
            entity_manager.add_component(projectile_entity.id, AttackComponent(damage=attack_comp.damage))
            entity_manager.add_component(projectile_entity.id, ProjectileComponent(bounces=attack_comp.bounces, owner_id=owner_id))
            
            sprite_surface = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(sprite_surface, (255, 255, 255), (7, 7), 7)
            sprite_rect = sprite_surface.get_rect(center=(player_pos.x, player_pos.y))
            entity_manager.add_component(projectile_entity.id, SpriteComponent(surface=sprite_surface, rect=sprite_rect))

    def _attack_basketball(self, entity_manager: EntityManager, player_pos: PositionComponent, attack_comp: AttackComponent, owner_id: int):
        dir_x, dir_y = self._get_mouse_direction(player_pos)

        projectile_entity = entity_manager.create_entity()
        entity_manager.add_component(projectile_entity.id, PositionComponent(x=player_pos.x, y=player_pos.y))
        entity_manager.add_component(projectile_entity.id, VelocityComponent(dx=dir_x * 8, dy=dir_y * 8))
        entity_manager.add_component(projectile_entity.id, AttackComponent(damage=attack_comp.damage))
        entity_manager.add_component(projectile_entity.id, ProjectileComponent(pierce=attack_comp.pierce, owner_id=owner_id))
        
        sprite_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(sprite_surface, (255, 165, 0), (10, 10), 10)
        sprite_rect = sprite_surface.get_rect(center=(player_pos.x, player_pos.y))
        entity_manager.add_component(projectile_entity.id, SpriteComponent(surface=sprite_surface, rect=sprite_rect))

    def _attack_baseball_bat(self, entity_manager: EntityManager, player_pos: PositionComponent, attack_comp: AttackComponent):
        dir_x, dir_y = self._get_mouse_direction(player_pos)
        angle = math.atan2(dir_y, dir_x)

        hitbox_entity = entity_manager.create_entity()
        entity_manager.add_component(hitbox_entity.id, PositionComponent(x=player_pos.x, y=player_pos.y))
        entity_manager.add_component(hitbox_entity.id, AttackComponent(damage=attack_comp.damage))
        entity_manager.add_component(hitbox_entity.id, HitboxComponent(width=70, height=attack_comp.angle, angle=math.degrees(angle), duration=0.2))