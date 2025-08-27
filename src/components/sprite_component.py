from dataclasses import dataclass
import pygame
from core.component import Component

@dataclass
class SpriteComponent(Component):
    surface: pygame.Surface
    rect: pygame.Rect
