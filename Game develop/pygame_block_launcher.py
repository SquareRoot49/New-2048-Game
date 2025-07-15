import pygame
import sys
import os
import math

# --- Settings ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
BLOCK_SIZE = 40
BLOCK_COLOR = (70, 130, 180)  # Steel Blue
BLOCK_IMAGE_PATH = "block.png"  # Place an image named 'block.png' in the same folder if available
FIXED_VX = 15  # Fixed horizontal velocity (pixels per frame)
GRAVITY = 0.35  # Gravity acceleration
FPS = 60

# --- Block Class ---
class Block:
    def __init__(self, x, y, vx, vy, image=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.image = image
        self.rect = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)

    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
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
    launch_x = 0
    launch_y = SCREEN_HEIGHT - BLOCK_SIZE

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Target position
                mx, my = event.pos
                dx = mx - launch_x
                dy = my - launch_y
                if dx == 0:
                    dx = 1  # Prevent division by zero
                vx = FIXED_VX if dx > 0 else -FIXED_VX
                t = abs(dx) / abs(vx)  # Time to reach target x
                # Projectile formula: y = y0 + vy*t + 0.5*g*t^2 => vy = (y - y0 - 0.5*g*t^2) / t
                vy = (dy - 0.5 * GRAVITY * t * t) / t
                blocks.append(Block(launch_x, launch_y, vx, vy, block_image))

        # Update blocks
        for block in blocks:
            block.update()

        # Remove blocks that move off the screen (right, left, top, or bottom)
        blocks = [b for b in blocks if 0 <= b.x < SCREEN_WIDTH and 0 <= b.y < SCREEN_HEIGHT]

        # Draw everything
        screen.fill((30, 30, 30))  # Dark background
        for block in blocks:
            block.draw(screen)
        
        # Instructions
        font = pygame.font.SysFont(None, 28)
        text = font.render("Click to launch a block that lands exactly at the mouse!", True, (220, 220, 220))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 