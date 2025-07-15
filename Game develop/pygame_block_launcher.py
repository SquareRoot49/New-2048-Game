import pygame
import sys
import os

# --- Settings ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
BLOCK_SIZE = 40
BLOCK_COLOR = (70, 130, 180)  # Steel Blue
BLOCK_IMAGE_PATH = "block.png"  # Place an image named 'block.png' in the same folder if available
LAUNCH_SPEED = -15  # Negative for upward
GRAVITY = 0.6
FPS = 60

# --- Block Class ---
class Block:
    def __init__(self, x, y, image=None):
        self.x = x
        self.y = y
        self.vy = LAUNCH_SPEED
        self.image = image
        self.rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(surface, BLOCK_COLOR, self.rect)

# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Block Launcher Demo")
    clock = pygame.time.Clock()

    # Try to load block image
    block_image = None
    if os.path.exists(BLOCK_IMAGE_PATH):
        img = pygame.image.load(BLOCK_IMAGE_PATH).convert_alpha()
        block_image = pygame.transform.scale(img, (BLOCK_SIZE, BLOCK_SIZE))

    blocks = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Launch a new block from the bottom center
                x = SCREEN_WIDTH // 2 - BLOCK_SIZE // 2
                y = SCREEN_HEIGHT - BLOCK_SIZE
                blocks.append(Block(x, y, block_image))

        # Update blocks
        for block in blocks:
            block.update()

        # Remove blocks that fall off the screen
        blocks = [b for b in blocks if b.y < SCREEN_HEIGHT]

        # Draw everything
        screen.fill((30, 30, 30))  # Dark background
        for block in blocks:
            block.draw(screen)
        
        # Instructions
        font = pygame.font.SysFont(None, 28)
        text = font.render("Click to launch a block!", True, (220, 220, 220))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 