import pygame
import sys
import os
import math
import random

# --- Settings ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
BLOCK_SIZE = 40
BLOCK_COLOR = (70, 130, 180)  # Steel Blue
BLOCK_IMAGE_PATH = "block.png"  # Place an image named 'block.png' in the same folder if available
FIXED_VX = 15  # Fixed horizontal velocity (pixels per frame)
GRAVITY = 0.35  # Gravity acceleration
FPS = 60
BLOCK_NUMBERS = [2, 4, 8, 16, 32, 64]
FONT_COLOR = (255, 255, 255)

# --- Block Class ---
class Block:
    def __init__(self, x, y, vx, vy, image=None, number=2):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.image = image
        self.number = number
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

    def draw(self, surface, font):
        if self.image:
            surface.blit(self.image, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(surface, BLOCK_COLOR, self.rect)
        # Draw the number
        num_surf = font.render(str(self.number), True, FONT_COLOR)
        num_rect = num_surf.get_rect(center=self.rect.center)
        surface.blit(num_surf, num_rect)

# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Block Launcher Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

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
                number = random.choice(BLOCK_NUMBERS)
                active_blocks.append(Block(launch_x, launch_y, vx, vy, block_image, number))

        # Update active blocks
        next_active_blocks = []
        merged_indices_this_frame = set()
        for block in active_blocks:
            block.update()
            landed = False
            landed_on_block_idx = None
            merge_candidate_idx = None
            for i, rblock in enumerate(received_blocks):
                block_center = block.rect.center
                rblock_center = rblock.rect.center
                dx = abs(block_center[0] - rblock_center[0])
                dy = abs(block_center[1] - rblock_center[1])
                # Only check for vertical collision (block lands on top of rblock)
                if block.rect.colliderect(rblock.rect) and dy > dx and block.y < rblock.y:
                    # If this is the closest block below, remember it
                    if landed_on_block_idx is None or rblock.y < received_blocks[landed_on_block_idx].y:
                        landed_on_block_idx = i
            # Check for bottom collision (landed on ground)
            if block.y + BLOCK_SIZE >= SCREEN_HEIGHT:
                block.y = SCREEN_HEIGHT - BLOCK_SIZE
                block.vy = 0
                block.vx = 0
                block.rect.topleft = (int(block.x), int(block.y))
                landed = True
            elif landed_on_block_idx is not None:
                rblock = received_blocks[landed_on_block_idx]
                block.y = rblock.y - BLOCK_SIZE
                block.vy = 0
                block.vx = 0
                block.rect.topleft = (int(block.x), int(block.y))
                landed = True
            if landed:
                merged = False
                if landed_on_block_idx is not None and landed_on_block_idx not in merged_indices_this_frame:
                    rblock = received_blocks[landed_on_block_idx]
                    if block.number == rblock.number:
                        del received_blocks[landed_on_block_idx]
                        merged_number = rblock.number * 2
                        merged_block = Block(rblock.x, rblock.y, 0, 0, block_image, merged_number)
                        merged_block.rect.topleft = (int(rblock.x), int(rblock.y))
                        received_blocks.append(merged_block)
                        merged_indices_this_frame.add(landed_on_block_idx)
                        merged = True
                if not merged:
                    received_blocks.append(block)
                continue  # Do not add to next_active_blocks
            if block.y > SCREEN_HEIGHT:
                continue
            # Horizontal collision: reflect or stop horizontal motion
            horizontal_collided = False
            for rblock in received_blocks:
                block_center = block.rect.center
                rblock_center = rblock.rect.center
                dx = abs(block_center[0] - rblock_center[0])
                dy = abs(block_center[1] - rblock_center[1])
                if block.rect.colliderect(rblock.rect) and dx > dy:
                    block.vx *= -1
                    horizontal_collided = True
                    break
            if horizontal_collided:
                continue
            next_active_blocks.append(block)
        active_blocks = next_active_blocks

        # Draw everything
        screen.fill((30, 30, 30))  # Dark background
        for block in received_blocks:
            block.draw(screen, font)
        for block in active_blocks:
            block.draw(screen, font)
        
        # Instructions
        text = font.render("Click to launch a block! Merge blocks with the same number.", True, (220, 220, 220))
        screen.blit(text, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 