from ..core.system import System
from ..core.entity_manager import EntityManager
from ..components.inventory_component import InventoryComponent
from ..components.player_component import PlayerComponent
from ..components.attack_component import AttackComponent
from ..components.health_component import HealthComponent

class ItemSystem(System):
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def update(self, dt: float):
        for entity in self.entity_manager.get_entities_with_components(PlayerComponent, InventoryComponent):
            self.reset_stats_to_base(entity)
            
            inventory = self.entity_manager.get_component(entity.id, InventoryComponent)
            for item in inventory.items:
                if item:
                    effects = item.get_effect()
                    self.apply_effects(entity, effects)

    def reset_stats_to_base(self, entity):
        player_component = self.entity_manager.get_component(entity.id, PlayerComponent)
        player_component.movement_speed = player_component.base_movement_speed

        if self.entity_manager.has_component(entity.id, AttackComponent):
            attack_component = self.entity_manager.get_component(entity.id, AttackComponent)
            attack_component.damage = attack_component.base_damage

        if self.entity_manager.has_component(entity.id, HealthComponent):
            health_component = self.entity_manager.get_component(entity.id, HealthComponent)
            health_component.maximum = health_component.base_maximum

    def apply_effects(self, entity, effects: dict):
        player_component = self.entity_manager.get_component(entity.id, PlayerComponent)
        
        movement_speed_increase = effects.get('movement_speed_increase', 0)
        player_component.movement_speed += player_component.base_movement_speed * movement_speed_increase

        if self.entity_manager.has_component(entity.id, AttackComponent):
            attack_component = self.entity_manager.get_component(entity.id, AttackComponent)
            attack_power_increase = effects.get('attack_power_increase', 0)
            attack_component.damage += attack_component.base_damage * attack_power_increase
        
        if self.entity_manager.has_component(entity.id, HealthComponent):
            health_component = self.entity_manager.get_component(entity.id, HealthComponent)
            max_health_increase = effects.get('max_health_increase', 0)
            health_component.maximum += max_health_increase
