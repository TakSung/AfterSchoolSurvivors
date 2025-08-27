from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .entity_manager import EntityManager

class ISystem(ABC):
    """Interface for all systems in the ECS."""

    @abstractmethod
    def update(self, entity_manager: EntityManager, delta_time: float) -> None:
        """Updates the system's state.

        Args:
            entity_manager: The manager for all entities and components.
            delta_time: The time elapsed since the last frame.
        """
        pass
