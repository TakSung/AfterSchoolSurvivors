import pygame
import math

from core.system import ISystem
from core.entity_manager import EntityManager
from components.position_component import PositionComponent
from components.health_component import HealthComponent
from components.player_component import PlayerComponent
from components.enemy_component import EnemyComponent
from components.attack_component import AttackComponent
from components.item_component import ItemComponent
from components.experience_component import ExperienceComponent
from components.sprite_component import SpriteComponent
from components.projectile_component import ProjectileComponent
from components.hitbox_component import HitboxComponent
from components.velocity_component import VelocityComponent
from components.enums import EntityStatus, ItemID

class CollisionSystem(ISystem):
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        self.handle_player_enemy_collisions(entity_manager)
        self.handle_weapon_enemy_collisions(entity_manager)
        self.handle_player_item_collisions(entity_manager)
        self.handle_hitbox_enemy_collisions(entity_manager)
        self.update_hitboxes(entity_manager, delta_time)
        self.handle_projectile_wall_collisions(entity_manager)

    def handle_player_enemy_collisions(self, entity_manager: EntityManager):
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, SpriteComponent, HealthComponent)
        enemy_entities = entity_manager.get_entities_with_components(EnemyComponent, SpriteComponent, HealthComponent)

        if not player_entities: return
        player_entity = player_entities[0]
        player_sprite = entity_manager.get_component(player_entity.id, SpriteComponent)
        player_health = entity_manager.get_component(player_entity.id, HealthComponent)
        player_comp = entity_manager.get_component(player_entity.id, PlayerComponent)

        if player_comp.is_invulnerable: return

        for enemy_entity in enemy_entities:
            enemy_sprite = entity_manager.get_component(enemy_entity.id, SpriteComponent)
            if player_sprite.rect.colliderect(enemy_sprite.rect):
                player_health.current -= 10 # Simple damage for now
                if player_health.current <= 0:
                    player_health.status = EntityStatus.DEAD
                # TODO: Add invulnerability timer after hit

    def handle_weapon_enemy_collisions(self, entity_manager: EntityManager):
        projectile_entities = entity_manager.get_entities_with_components(ProjectileComponent, SpriteComponent, AttackComponent)
        enemy_entities = entity_manager.get_entities_with_components(EnemyComponent, SpriteComponent, HealthComponent)
        enemies_to_destroy = set()

        for proj_entity in projectile_entities:
            proj_sprite = entity_manager.get_component(proj_entity.id, SpriteComponent)
            proj_comp = entity_manager.get_component(proj_entity.id, ProjectileComponent)
            attack_comp = entity_manager.get_component(proj_entity.id, AttackComponent)

            for enemy_entity in enemy_entities:
                if enemy_entity.id in enemies_to_destroy: continue
                enemy_sprite = entity_manager.get_component(enemy_entity.id, SpriteComponent)

                if proj_sprite.rect.colliderect(enemy_sprite.rect):
                    enemy_health = entity_manager.get_component(enemy_entity.id, HealthComponent)
                    enemy_health.current -= attack_comp.damage

                    if enemy_health.current <= 0:
                        enemies_to_destroy.add(enemy_entity.id)
                    
                    if proj_comp.pierce > 0:
                        proj_comp.pierce -= 1
                    elif proj_comp.bounces > 0:
                        proj_comp.bounces -= 1
                        vel = entity_manager.get_component(proj_entity.id, VelocityComponent)
                        vel.dx *= -1
                        vel.dy *= -1
                    else:
                        entity_manager.destroy_entity(proj_entity.id)
                        break # Projectile is destroyed, move to next projectile
        
        self.destroy_enemies_and_drop_exp(entity_manager, enemies_to_destroy)

    def handle_hitbox_enemy_collisions(self, entity_manager: EntityManager):
        hitbox_entities = entity_manager.get_entities_with_components(HitboxComponent, AttackComponent)
        enemy_entities = entity_manager.get_entities_with_components(EnemyComponent, SpriteComponent, HealthComponent)
        enemies_to_destroy = set()

        for hitbox_entity in hitbox_entities:
            hitbox = entity_manager.get_component(hitbox_entity.id, HitboxComponent)
            attack = entity_manager.get_component(hitbox_entity.id, AttackComponent)
            pos = entity_manager.get_component(hitbox_entity.id, PositionComponent)
            
            hitbox_angle_rad = math.radians(hitbox.angle)
            
            for enemy_entity in enemy_entities:
                if enemy_entity.id in enemies_to_destroy: continue
                
                enemy_pos = entity_manager.get_component(enemy_entity.id, PositionComponent)
                
                # 1. Distance Check
                distance_sq = (enemy_pos.x - pos.x)**2 + (enemy_pos.y - pos.y)**2
                if distance_sq > hitbox.width**2: # hitbox.width is used as radius
                    continue

                # 2. Angle Check
                enemy_angle_rad = math.atan2(enemy_pos.y - pos.y, enemy_pos.x - pos.x)
                
                angle_diff = enemy_angle_rad - hitbox_angle_rad
                angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
                
                arc_angle_rad = math.radians(hitbox.height) # hitbox.height is used as arc angle
                
                if abs(angle_diff) <= arc_angle_rad / 2:
                    enemy_health = entity_manager.get_component(enemy_entity.id, HealthComponent)
                    enemy_health.current -= attack.damage
                    if enemy_health.current <= 0:
                        enemies_to_destroy.add(enemy_entity.id)
        
        self.destroy_enemies_and_drop_exp(entity_manager, enemies_to_destroy)

    def update_hitboxes(self, entity_manager: EntityManager, delta_time: float):
        for entity in entity_manager.get_entities_with_components(HitboxComponent):
            hitbox = entity_manager.get_component(entity.id, HitboxComponent)
            hitbox.timer += delta_time
            if hitbox.timer >= hitbox.duration:
                entity_manager.destroy_entity(entity.id)

    def handle_player_item_collisions(self, entity_manager: EntityManager):
        player_entities = entity_manager.get_entities_with_components(PlayerComponent, SpriteComponent)
        item_entities = entity_manager.get_entities_with_components(ItemComponent, SpriteComponent)

        if not player_entities: return
        player_entity = player_entities[0]
        player_sprite = entity_manager.get_component(player_entity.id, SpriteComponent)
        player_comp = entity_manager.get_component(player_entity.id, PlayerComponent)

        for item_entity in item_entities:
            item_sprite = entity_manager.get_component(item_entity.id, SpriteComponent)
            if player_sprite.rect.colliderect(item_sprite.rect):
                if entity_manager.has_component(item_entity.id, ExperienceComponent):
                    exp_comp = entity_manager.get_component(item_entity.id, ExperienceComponent)
                    player_comp.experience += exp_comp.amount
                    entity_manager.destroy_entity(item_entity.id)

    def handle_projectile_wall_collisions(self, entity_manager: EntityManager):
        for entity in entity_manager.get_entities_with_components(ProjectileComponent, PositionComponent, VelocityComponent):
            pos = entity_manager.get_component(entity.id, PositionComponent)
            vel = entity_manager.get_component(entity.id, VelocityComponent)
            proj = entity_manager.get_component(entity.id, ProjectileComponent)

            if pos.x < 0 or pos.x > self.screen_width:
                if proj.bounces > 0:
                    proj.bounces -= 1
                    vel.dx *= -1
                else:
                    entity_manager.destroy_entity(entity.id)
            elif pos.y < 0 or pos.y > self.screen_height:
                if proj.bounces > 0:
                    proj.bounces -= 1
                    vel.dy *= -1
                else:
                    entity_manager.destroy_entity(entity.id)

    def destroy_enemies_and_drop_exp(self, entity_manager: EntityManager, enemy_ids: set[int]):
        for enemy_id in enemy_ids:
            enemy_pos = entity_manager.get_component(enemy_id, PositionComponent)
            enemy_comp = entity_manager.get_component(enemy_id, EnemyComponent)
            if enemy_pos and enemy_comp:
                self._create_exp_orb(entity_manager, enemy_pos.x, enemy_pos.y, enemy_comp.enemy_type.base_experience_yield)
            entity_manager.destroy_entity(enemy_id)

    def _create_exp_orb(self, entity_manager: EntityManager, x: float, y: float, exp_amount: int):
        orb_entity = entity_manager.create_entity()
        entity_manager.add_component(orb_entity.id, PositionComponent(x=x, y=y))
        entity_manager.add_component(orb_entity.id, ItemComponent(item_id=ItemID.EXPERIENCE_ORB))
        entity_manager.add_component(orb_entity.id, ExperienceComponent(amount=exp_amount))
        
        orb_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(orb_surface, (255, 255, 0), (5, 5), 5)
        orb_rect = orb_surface.get_rect(center=(x, y))
        entity_manager.add_component(orb_entity.id, SpriteComponent(surface=orb_surface, rect=orb_rect))