import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Window title
pygame.display.set_caption("After School Survivors")

# Basic background color
BLACK = (0, 0, 0)

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            print(f"Key down: {pygame.key.name(event.key)}")
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.KEYUP:
            print(f"Key up: {pygame.key.name(event.key)}")
        elif event.type == pygame.MOUSEMOTION:
            print(f"Mouse position: {event.pos}")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse button down: {event.button} at {event.pos}")
        elif event.type == pygame.MOUSEBUTTONUP:
            print(f"Mouse button up: {event.button} at {event.pos}")

    # Update game state
    # (This is where game logic will go)

    # Draw everything
    screen.fill(BLACK)
    # (This is where drawing code will go)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 255, 0))  # Green square for now
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.health = 100
        self.speed = 5
        self.attack_speed = 1.0  # Attacks per second

    def update(self):
        # Player logic will go here
        pass

# Create player group and player instance
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)


    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
