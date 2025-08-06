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

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a transparent surface for the original image
        self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
        # Draw a triangle pointing right (0 degrees)
        pygame.draw.polygon(self.original_image, (0, 255, 0), [(50, 25), (0, 0), (0, 50)])
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.health = 100
        self.speed = 5
        self.attack_speed = 1.0  # Attacks per second

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # --- Rotation Logic ---
        # Vector from player to mouse
        direction = pygame.math.Vector2(mouse_pos) - self.rect.center
        # Angle of the vector in degrees. Vector2(1, 0) is the x-axis.
        angle = direction.angle_to(pygame.math.Vector2(1, 0))

        # Rotate the original image to avoid quality loss
        self.image = pygame.transform.rotate(self.original_image, angle) # The angle is calculated correctly, no need to negate
        self.rect = self.image.get_rect(center=self.rect.center)
        # --- End Rotation Logic ---

        # --- Movement Logic ---
        # Smooth movement using linear interpolation (lerp)
        current_vector = pygame.math.Vector2(self.rect.center)
        target_vector = pygame.math.Vector2(mouse_pos)
        self.rect.center = current_vector.lerp(target_vector, 0.05)
        # --- End Movement Logic ---

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

# Create player group and player instance
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

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
    all_sprites.update()

    # Draw everything
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()