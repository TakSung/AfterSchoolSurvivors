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
        # AI-NOTE : 2025-01-05 충돌 무적 타이머를 가장 먼저 업데이트
        # - 이유: 충돌 처리 전에 무적 상태를 먼저 업데이트하여 정확한 무적 판정
        # - 요구사항: 매 프레임 무적 타이머 업데이트로 정확한 무적 시간 관리
        self.update_invulnerability_timers(entity_manager, delta_time)
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
            enemy_comp = entity_manager.get_component(enemy_entity.id, EnemyComponent)

            # AI-NOTE : 2025-01-05 충돌 시 양측 무적 판정 추가
            # - 이유: 적도 무적 상태일 때는 플레이어에게 데미지를 주지 않음
            # - 요구사항: 연속 충돌로 인한 즉사 방지
            if player_sprite.rect.colliderect(enemy_sprite.rect):
                if not enemy_comp.is_invulnerable:  # 적도 무적이 아닐 때만 데미지 발생
                    player_health.current -= 10 # Simple damage for now
                    if player_health.current <= 0:
                        player_health.status = EntityStatus.DEAD

                    # AI-NOTE : 2025-01-05 충돌 후 무적 시간 부여
                    # - 이유: 플레이어와 적 모두 짧은 무적 시간을 부여하여 연속 데미지 방지
                    # - 요구사항: 플레이어 0.5초, 적 0.3초 무적
                    player_comp.is_invulnerable = True
                    player_comp.invulnerability_timer = 0.0

                    enemy_comp.is_invulnerable = True
                    enemy_comp.invulnerability_timer = 0.0

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
                enemy_comp = entity_manager.get_component(enemy_entity.id, EnemyComponent)

                if proj_sprite.rect.colliderect(enemy_sprite.rect):
                    # AI-NOTE : 2025-01-05 무기 충돌 시 무적 판정 추가
                    # - 이유: 무적 상태인 적은 데미지를 받지 않아 프레임 단위 중복 데미지 방지
                    # - 요구사항: 적이 무적이 아닐 때만 데미지 적용
                    if not enemy_comp.is_invulnerable:
                        enemy_health = entity_manager.get_component(enemy_entity.id, HealthComponent)
                        enemy_health.current -= attack_comp.damage

                        # AI-NOTE : 2025-01-05 데미지 후 적 무적 활성화
                        # - 이유: 투사체가 여러 프레임에 걸쳐 접촉해도 한 번만 데미지
                        # - 요구사항: 0.3초 무적 시간 부여
                        enemy_comp.is_invulnerable = True
                        enemy_comp.invulnerability_timer = 0.0

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
                enemy_comp = entity_manager.get_component(enemy_entity.id, EnemyComponent)

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
                    # AI-NOTE : 2025-01-05 Hitbox 충돌 시 무적 판정 추가
                    # - 이유: 야구방망이 같은 근접 공격도 프레임 단위 중복 데미지 방지
                    # - 요구사항: 적이 무적 상태가 아닐 때만 데미지 적용
                    if not enemy_comp.is_invulnerable:
                        enemy_health = entity_manager.get_component(enemy_entity.id, HealthComponent)
                        enemy_health.current -= attack.damage

                        # AI-NOTE : 2025-01-05 Hitbox 데미지 후 적 무적 활성화
                        # - 이유: 야구방망이 스윙이 여러 프레임 동안 지속되어도 한 번만 데미지
                        # - 요구사항: 0.3초 무적 시간 부여
                        enemy_comp.is_invulnerable = True
                        enemy_comp.invulnerability_timer = 0.0

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

    # AI-NOTE : 2025-01-05 충돌 무적 타이머 업데이트 시스템
    # - 이유: 플레이어와 적의 무적 상태를 시간에 따라 자동으로 해제하기 위함
    # - 요구사항: 플레이어(0.5초 충돌 무적), 적(0.3초 무적) 시간 관리
    # - 히스토리: 농구화 아이템의 무적과는 별도로 충돌 무적 시스템 추가
    def update_invulnerability_timers(self, entity_manager: EntityManager, delta_time: float) -> None:
        """플레이어와 적의 무적 타이머를 업데이트하고 시간 경과 시 무적 해제"""

        # AI-DEV : 플레이어 충돌 무적 타이머 처리
        # - 문제: 농구화 아이템의 무적(1초)과 충돌 무적(0.5초)을 구분해야 함
        # - 해결책: invulnerability_timer가 0.5초 이하일 때만 충돌 무적으로 간주
        # - 주의사항: 농구화 무적은 item_system.py에서 별도로 관리됨
        for entity in entity_manager.get_entities_with_components(PlayerComponent):
            player_comp = entity_manager.get_component(entity.id, PlayerComponent)
            if player_comp.is_invulnerable and player_comp.invulnerability_timer < 0.6:
                player_comp.invulnerability_timer += delta_time
                # 충돌 무적 시간(0.5초) 경과 시 무적 해제
                if player_comp.invulnerability_timer >= 0.5:
                    player_comp.is_invulnerable = False
                    player_comp.invulnerability_timer = 0.0

        # 적 무적 타이머 처리
        for entity in entity_manager.get_entities_with_components(EnemyComponent):
            enemy_comp = entity_manager.get_component(entity.id, EnemyComponent)
            if enemy_comp.is_invulnerable:
                enemy_comp.invulnerability_timer += delta_time
                if enemy_comp.invulnerability_timer >= enemy_comp.invulnerability_duration:
                    enemy_comp.is_invulnerable = False
                    enemy_comp.invulnerability_timer = 0.0