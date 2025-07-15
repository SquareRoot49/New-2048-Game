import pygame
import sys
import os
import random

# --- Settings ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
BLOCK_SIZE = 40
BLOCK_COLOR = (70, 130, 180)  # Steel Blue
BLOCK_IMAGE_PATH = "block.png"
FPS = 60
BLOCK_NUMBERS = [2, 4, 8, 16, 32, 64]
FONT_COLOR = (255, 255, 255)

# --- Grid Setup ---
COLUMNS = SCREEN_WIDTH // BLOCK_SIZE
ROWS = SCREEN_HEIGHT // BLOCK_SIZE

def grid_to_screen(grid_x, grid_y):
    return grid_x * BLOCK_SIZE, grid_y * BLOCK_SIZE

def screen_to_grid(x, y):
    return x // BLOCK_SIZE, y // BLOCK_SIZE

# --- Block Class ---
class Block:
    def __init__(self, grid_x, grid_y, number):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.number = number
        self.falling = True  # True if the block is falling
        self.merged_this_fall = False  # Prevent multiple merges per fall
        self.just_merged = False  # Prevent double merges in a move

    def screen_pos(self):
        return grid_to_screen(self.grid_x, self.grid_y)

# --- Horizontal Move Logic ---
def move_blocks(grid, direction):
    # direction: 1 for right, -1 for left
    moved = False
    for row in range(ROWS):
        # Extract the row
        line = [grid[col][row] for col in range(COLUMNS)]
        # Remove None
        blocks = [b for b in line if b is not None]
        # Reset merge flags
        for b in blocks:
            b.just_merged = False
        # Prepare merged flags for this row
        merged_flags = [False] * len(blocks)
        # Move and merge
        if direction == 1:  # Right
            blocks = blocks[::-1]
            merged_flags = merged_flags[::-1]
        merged_blocks = []
        i = 0
        while i < len(blocks):
            if (
                i + 1 < len(blocks)
                and blocks[i].number == blocks[i + 1].number
                and not merged_flags[i]
                and not merged_flags[i + 1]
            ):
                # Merge
                merged_block = Block(0, row, blocks[i].number * 2)
                merged_block.just_merged = True
                merged_blocks.append(merged_block)
                merged_flags[i + 1] = True  # Mark the right (or left) block as merged
                moved = True
                i += 2
            else:
                merged_blocks.append(blocks[i])
                i += 1
        # Fill with None
        while len(merged_blocks) < COLUMNS:
            merged_blocks.append(None)
        if direction == 1:
            merged_blocks = merged_blocks[::-1]
        # Place back in grid
        for col in range(COLUMNS):
            b = merged_blocks[col]
            if b is not None:
                if b.grid_x != col or b.grid_y != row:
                    moved = True
                b.grid_x = col
                b.grid_y = row
            grid[col][row] = b
    # After horizontal move/merge, apply gravity
    apply_gravity(grid)
    return moved

# --- Gravity Logic ---
def apply_gravity(grid):
    for col in range(COLUMNS):
        # Collect all blocks in this column
        stack = [grid[col][row] for row in range(ROWS) if grid[col][row] is not None]
        # Place them at the bottom
        for row in range(ROWS):
            grid[col][row] = None
        for i, block in enumerate(reversed(stack)):
            new_row = ROWS - 1 - i
            block.grid_x = col
            block.grid_y = new_row
            grid[col][new_row] = block

# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Grid 2048 Block Launcher")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    block_image = None
    if os.path.exists(BLOCK_IMAGE_PATH):
        img = pygame.image.load(BLOCK_IMAGE_PATH).convert_alpha()
        block_image = pygame.transform.scale(img, (BLOCK_SIZE, BLOCK_SIZE))

    grid = [[None for _ in range(ROWS)] for _ in range(COLUMNS)]
    falling_blocks = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                col = mx // BLOCK_SIZE
                if 0 <= col < COLUMNS:
                    for row in range(ROWS):
                        if grid[col][row] is not None:
                            break
                    else:
                        row = ROWS
                    target_row = row - 1 if row > 0 else 0
                    if grid[col][0] is None:
                        number = random.choice(BLOCK_NUMBERS)
                        new_block = Block(col, 0, number)
                        falling_blocks.append(new_block)
                        grid[col][0] = new_block
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    move_blocks(grid, 1)
                elif event.key == pygame.K_a:
                    move_blocks(grid, -1)

        # Update falling blocks
        next_falling_blocks = []
        for block in falling_blocks:
            if not block.falling:
                continue
            below_y = block.grid_y + 1
            if below_y >= ROWS:
                block.falling = False
                block.merged_this_fall = False
                continue
            below_block = grid[block.grid_x][below_y]
            if below_block is None:
                grid[block.grid_x][block.grid_y] = None
                block.grid_y += 1
                grid[block.grid_x][block.grid_y] = block
                next_falling_blocks.append(block)
            else:
                if (not block.merged_this_fall and not below_block.falling and block.number == below_block.number):
                    grid[block.grid_x][block.grid_y] = None
                    grid[block.grid_x][below_y] = None
                    merged_block = Block(block.grid_x, below_y, block.number * 2)
                    merged_block.falling = True
                    merged_block.merged_this_fall = True
                    grid[block.grid_x][below_y] = merged_block
                    next_falling_blocks.append(merged_block)
                else:
                    block.falling = False
                    block.merged_this_fall = False
        falling_blocks = [b for b in next_falling_blocks if b.falling]

        # Draw everything
        screen.fill((30, 30, 30))
        for col in range(COLUMNS):
            for row in range(ROWS):
                block = grid[col][row]
                if block is not None:
                    x, y = grid_to_screen(col, row)
                    pygame.draw.rect(screen, BLOCK_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))
                    num_surf = font.render(str(block.number), True, FONT_COLOR)
                    num_rect = num_surf.get_rect(center=(x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2))
                    screen.blit(num_surf, num_rect)
        for block in falling_blocks:
            if grid[block.grid_x][block.grid_y] is not block:
                x, y = block.screen_pos()
                pygame.draw.rect(screen, BLOCK_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))
                num_surf = font.render(str(block.number), True, FONT_COLOR)
                num_rect = num_surf.get_rect(center=(x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2))
                screen.blit(num_surf, num_rect)
        for col in range(COLUMNS + 1):
            pygame.draw.line(screen, (60, 60, 60), (col * BLOCK_SIZE, 0), (col * BLOCK_SIZE, SCREEN_HEIGHT))
        for row in range(ROWS + 1):
            pygame.draw.line(screen, (60, 60, 60), (0, row * BLOCK_SIZE), (SCREEN_WIDTH, row * BLOCK_SIZE))
        text = font.render("Click to drop, A/D to move/merge left/right!", True, (220, 220, 220))
        screen.blit(text, (20, 20))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 