from core.system import ISystem
from core.entity_manager import EntityManager
from components.inventory_component import InventoryComponent
from components.player_component import PlayerComponent
from components.attack_component import AttackComponent
from components.health_component import HealthComponent
from components.enums import ItemID, ItemType

class ItemSystem(ISystem):
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def update(self, dt: float):
        for entity in self.entity_manager.get_entities_with_components(PlayerComponent, InventoryComponent):
            inventory = self.entity_manager.get_component(entity.id, InventoryComponent)
            
            self.reset_stats_to_base(entity)
            
            equipped_item_ids = {item.item_id for item in inventory.items if item}
            
            # Apply passive effects and special effects
            self.apply_item_effects(entity, inventory, equipped_item_ids, dt)
            
            # Handle synergies
            self.apply_synergies(entity, inventory, equipped_item_ids)

            # Process one-time items
            self.process_consumables(entity, inventory)

    def reset_stats_to_base(self, entity):
        if self.entity_manager.has_component(entity.id, PlayerComponent):
            player_comp = self.entity_manager.get_component(entity.id, PlayerComponent)
            player_comp.movement_speed = player_comp.base_movement_speed
            player_comp.attack_speed = player_comp.base_attack_speed

        if self.entity_manager.has_component(entity.id, AttackComponent):
            attack_comp = self.entity_manager.get_component(entity.id, AttackComponent)
            attack_comp.damage = attack_comp.base_damage
            attack_comp.attack_speed = attack_comp.base_attack_speed
            attack_comp.weapon_type = None
            attack_comp.projectiles = 1
            attack_comp.bounces = 0
            attack_comp.pierce = 0
            attack_comp.angle = 90

    def apply_item_effects(self, entity, inventory, equipped_item_ids, dt):
        player_comp = self.entity_manager.get_component(entity.id, PlayerComponent)
        attack_comp = self.entity_manager.get_component(entity.id, AttackComponent)

        # Determine the active weapon (highest level)
        active_weapon = None
        highest_level = -1
        if inventory.items:
            for item in inventory.items:
                if item and hasattr(item, 'item_type') and item.item_type == ItemType.WEAPON:
                    if hasattr(item, 'level') and item.level > highest_level:
                        highest_level = item.level
                        active_weapon = item

        # Apply active weapon's primary effects
        if attack_comp and active_weapon:
            effects = active_weapon.get_effect()
            attack_comp.weapon_type = effects.get("weapon_type")
            attack_comp.projectiles = effects.get("projectiles", 1)
            attack_comp.bounces = effects.get("bounces", 0)
            attack_comp.pierce = effects.get("pierce", 0)
            attack_comp.angle = effects.get("angle", 90)

            # AI-NOTE: 2025-11-05 무기별 기본 데미지 차등 적용
            # - 이유: 사용자의 요청으로 게임 밸런스 조정
            # - 요구사항: 축구공과 농구공의 데미지를 증가시켜달라는 요청
            if attack_comp.weapon_type == "soccer_ball":
                attack_comp.damage = int(attack_comp.base_damage * 1.5) # 50% 증가
            elif attack_comp.weapon_type == "basketball":
                attack_comp.damage = int(attack_comp.base_damage * 1.2) # 20% 증가

        # Apply passive effects from ALL items
        if inventory.items:
            for item in inventory.items:
                if not item:
                    continue

                effects = item.get_effect()

                # Passive stats
                if player_comp:
                    player_comp.movement_speed += player_comp.base_movement_speed * effects.get('movement_speed_increase', 0)
                if attack_comp:
                    attack_comp.attack_speed += attack_comp.base_attack_speed * effects.get('attack_speed_increase', 0)

                # Special ability effects
                if player_comp and "invulnerability_jump" in effects:
                    jump_props = effects["invulnerability_jump"]
                    player_comp.invulnerability_cooldown = jump_props["cooldown"]
                    player_comp.invulnerability_duration = jump_props["duration"]
                    
                    if not player_comp.is_invulnerable:
                        player_comp.invulnerability_timer += dt
                        if player_comp.invulnerability_timer >= player_comp.invulnerability_cooldown:
                            player_comp.is_invulnerable = True
                            player_comp.invulnerability_timer = 0
                    else:
                        player_comp.invulnerability_timer += dt
                        if player_comp.invulnerability_timer >= player_comp.invulnerability_duration:
                            player_comp.is_invulnerable = False
                            player_comp.invulnerability_timer = 0
                            # Synergy: Baseball bat swing on land
                            if ItemID.BASEBALL_BAT in equipped_item_ids:
                                setattr(player_comp, 'trigger_bat_swing', True)


    def apply_synergies(self, entity, inventory, equipped_item_ids):
        attack_comp = self.entity_manager.get_component(entity.id, AttackComponent)
        if not attack_comp: return

        # (Soccer Ball + Soccer Shoes)
        if ItemID.SOCCER_BALL in equipped_item_ids and ItemID.SOCCER_SHOES in equipped_item_ids:
            if attack_comp.weapon_type == "soccer_ball":
                attack_comp.damage = int(attack_comp.damage * 1.3)

    def process_consumables(self, entity, inventory):
        health_comp = self.entity_manager.get_component(entity.id, HealthComponent)
        if not health_comp: return

        items_to_remove = []
        for i, item in enumerate(inventory.items):
            if not item:
                continue
            
            effects = item.get_effect()
            if "instant_heal_percentage" in effects:
                heal_percent = effects["instant_heal_percentage"]
                health_comp.current += health_comp.maximum * heal_percent
                if health_comp.current > health_comp.maximum:
                    health_comp.current = health_comp.maximum
                items_to_remove.append(i)

        for i in sorted(items_to_remove, reverse=True):
            inventory.remove_item(i)
