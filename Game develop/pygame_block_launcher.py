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
        self.rect = pygame.Rect(int(self.x), int(self.y), BLOCK_SIZE, BLOCK_SIZE)

    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # --- Boundary collision handling ---
        # Top edge
        if self.y < 0:
            self.y = 0
            self.vy *= -1
        # Right edge
        if self.x + BLOCK_SIZE > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - BLOCK_SIZE
            self.vx *= -1
        # (Optional: left edge, but not required by user)

        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (int(self.x), int(self.y)))
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

    active_blocks = []
    received_blocks = []
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
                active_blocks.append(Block(launch_x, launch_y, vx, vy, block_image))

        # Update active blocks
        next_active_blocks = []
        for block in active_blocks:
            block.update()
            # Check for collision with any received block
            collided = False
            for rblock in received_blocks:
                if block.rect.colliderect(rblock.rect):
                    # Determine collision direction using center coordinates
                    block_center = block.rect.center
                    rblock_center = rblock.rect.center
                    dx = abs(block_center[0] - rblock_center[0])
                    dy = abs(block_center[1] - rblock_center[1])
                    if dy > dx:
                        # Vertical collision: accept the block
                        block.vy = 0
                        block.vx = 0
                        block.rect.topleft = (int(block.x), int(block.y))
                        received_blocks.append(block)
                        collided = True
                        break
                    else:
                        # Horizontal collision: reflect or stop horizontal motion
                        block.vx *= -1
                        # Optionally, you could also set block.vx = 0 to just stop
            if collided:
                continue
            # Check for bottom collision (landed)
            if block.y + BLOCK_SIZE >= SCREEN_HEIGHT:
                block_center_x = block.x + BLOCK_SIZE / 2
                if block_center_x > SCREEN_WIDTH / 2:
                    block.y = SCREEN_HEIGHT - BLOCK_SIZE
                    block.vy = 0
                    block.vx = 0
                    block.rect.topleft = (int(block.x), int(block.y))
                    received_blocks.append(block)
                continue
            # Remove if block is completely below the screen
            if block.y > SCREEN_HEIGHT:
                continue
            next_active_blocks.append(block)
        active_blocks = next_active_blocks

        # Draw everything
        screen.fill((30, 30, 30))  # Dark background
        for block in received_blocks:
            block.draw(screen)
        for block in active_blocks:
            block.draw(screen)
        
        # Instructions
        font = pygame.font.SysFont(None, 28)
        text = font.render("Click to launch a block that lands exactly at the mouse! (Stacking supported)", True, (220, 220, 220))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 