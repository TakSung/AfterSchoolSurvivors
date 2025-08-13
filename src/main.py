import pygame
import random

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
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Load player sprite
        try:
            self.original_image = pygame.image.load("assets/player.svg").convert_alpha()
            self.original_image = pygame.transform.scale(self.original_image, (50, 50))
        except pygame.error:
            # Create a fallback surface if the image is not found
            print("Player sprite 'assets/player.png' not found. Using fallback triangle.")
            self.original_image = pygame.Surface((50, 50), pygame.SRCALPHA)
            # Draw a triangle pointing right (0 degrees)
            pygame.draw.polygon(self.original_image, (0, 255, 0), [(50, 25), (0, 0), (0, 50)])
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        
        self.max_health = 100
        self.health = 100
        self.speed = 5
        self.attack_speed = 4.0  # Attacks per second
        self.last_attack_time = 0
        
        self.invulnerable = False
        self.invulnerable_duration = 1000  # 1 second
        self.last_hit_time = 0

    def get_angle(self):
        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.math.Vector2(mouse_pos) - self.rect.center
        return direction.angle_to(pygame.math.Vector2(1, 0))

    def attack(self, projectiles, all_sprites):
        now = pygame.time.get_ticks()
        attack_cooldown = 1000 / self.attack_speed  # Cooldown in milliseconds
        if now - self.last_attack_time > attack_cooldown:
            self.last_attack_time = now
            angle = self.get_angle()
            projectile = Projectile(self.rect.center, angle)
            projectiles.add(projectile)
            all_sprites.add(projectile)

    def take_damage(self, amount):
        now = pygame.time.get_ticks()
        if not self.invulnerable:
            self.health -= amount
            self.invulnerable = True
            self.last_hit_time = now
            if self.health < 0:
                self.health = 0

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def update(self):
        # Invulnerability timer
        now = pygame.time.get_ticks()
        if self.invulnerable and now - self.last_hit_time > self.invulnerable_duration:
            self.invulnerable = False

        angle = self.get_angle()

        # --- Rotation Logic ---
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        # --- End Rotation Logic ---

        # --- Movement Logic ---
        mouse_pos = pygame.mouse.get_pos()
        current_vector = pygame.math.Vector2(self.rect.center)
        target_vector = pygame.math.Vector2(mouse_pos)
        # Move only if not too close to the target to prevent jittering
        if target_vector.distance_to(current_vector) > 1:
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

# Projectile class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((10, 5), pygame.SRCALPHA)
        self.image.fill((255, 255, 0)) # Yellow
        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)
        
        # Rotate image to match player's angle
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Convert angle to a vector
        self.velocity = pygame.math.Vector2(1, 0).rotate(-angle) * 10

    def update(self):
        self.rect.center += self.velocity
        # Remove projectile if it goes off-screen
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (15, 15), 15)
        self.rect = self.image.get_rect()
        
        # Spawn at a random edge
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            self.rect.center = (random.randint(0, SCREEN_WIDTH), 0)
        elif edge == 'bottom':
            self.rect.center = (random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT)
        elif edge == 'left':
            self.rect.center = (0, random.randint(0, SCREEN_HEIGHT))
        else: # right
            self.rect.center = (SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT))
            
        self.speed = random.randint(1, 3)

    def update(self):
        # Simple AI: move towards player
        if player.rect.centerx > self.rect.centerx:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed
        if player.rect.centery > self.rect.centery:
            self.rect.y += self.speed
        else:
            self.rect.y -= self.speed

# Create sprite groups
all_sprites = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Create player instance and add to all_sprites group
player = Player()
all_sprites.add(player)

# Timer for enemy spawns
enemy_spawn_timer = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn_timer, 1000) # Spawn an enemy every second

# Game loop
running = True
game_over = False

def draw_health_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, (0, 255, 0), fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def show_game_over_screen():
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, RED)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)


while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == enemy_spawn_timer and not game_over:
            new_enemy = Enemy()
            all_sprites.add(new_enemy)
            enemies.add(new_enemy)

    if not game_over:
        # Update game state
        player.attack(projectiles, all_sprites) # Player attack logic
        all_sprites.update()

        # Check for collisions
        # Enemies hitting player
        hits = pygame.sprite.spritecollide(player, enemies, True) # True to kill enemy on hit
        for hit in hits:
            player.take_damage(10)
            if player.health <= 0:
                game_over = True

        # Projectiles hitting enemies
        pygame.sprite.groupcollide(projectiles, enemies, True, True) # Both killed

    # Draw everything
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_health_bar(screen, 5, 5, player.health)

    if game_over:
        show_game_over_screen()
        running = False

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
