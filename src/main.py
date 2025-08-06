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

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background
    screen.fill(BLACK)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
