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
GRAVITY = 0.7
LAUNCH_VX = 10
LAUNCH_VY = -12

# --- Grid Setup ---
COLUMNS = (SCREEN_WIDTH // 2) // BLOCK_SIZE  # Only right half is grid
ROWS = SCREEN_HEIGHT // BLOCK_SIZE
GRID_X_OFFSET = SCREEN_WIDTH // 2

def grid_to_screen(grid_x, grid_y):
    return GRID_X_OFFSET + grid_x * BLOCK_SIZE, grid_y * BLOCK_SIZE

def screen_to_grid(x, y):
    return (x - GRID_X_OFFSET) // BLOCK_SIZE, y // BLOCK_SIZE

# --- Block Class ---
class Block:
    def __init__(self, x, y, number, vx=LAUNCH_VX, vy=LAUNCH_VY, grid_x=None, grid_y=None, in_grid=False):
        self.x = x  # pixel x
        self.y = y  # pixel y
        self.vx = vx
        self.vy = vy
        self.number = number
        
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.in_grid = in_grid
        self.falling = not in_grid
        self.just_merged = False

    def screen_pos(self):
        if self.in_grid:
            return grid_to_screen(self.grid_x, self.grid_y)
        else:
            return int(self.x), int(self.y)

# --- Grid Logic ---
def move_blocks(grid, direction):
    moved = False
    for row in range(ROWS):
        # Extract the row and reset merge flags
        line = [grid[col][row] for col in range(COLUMNS)]
        tiles = [b for b in line if b is not None]
        for b in tiles:
            b.just_merged = False
        # Reverse for right move
        if direction == 1:
            tiles = tiles[::-1]
        # Merge pass (standard 2048 logic)
        merged_tiles = []
        i = 0
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i].number == tiles[i + 1].number and not tiles[i].just_merged and not tiles[i + 1].just_merged:
                merged_block = Block(0, row, tiles[i].number * 2, in_grid=True)
                merged_block.just_merged = True
                merged_tiles.append(merged_block)
                moved = True
                i += 2  # Skip the next tile, as it was merged
            else:
                merged_tiles.append(tiles[i])
                i += 1
        # Fill with None to match grid size
        while len(merged_tiles) < COLUMNS:
            merged_tiles.append(None)
        # Reverse back for right move
        if direction == 1:
            merged_tiles = merged_tiles[::-1]
        # Place back in grid
        for col in range(COLUMNS):
            b = merged_tiles[col]
            if b is not None:
                if b.grid_x != col or b.grid_y != row:
                    moved = True
                b.grid_x = col
                b.grid_y = row
                b.in_grid = True
            grid[col][row] = b
    apply_gravity(grid)
    return moved

def move_blocks_down(grid):
    moved = False
    for col in range(COLUMNS):
        # Extract the column and reset merge flags
        line = [grid[col][row] for row in range(ROWS)]
        tiles = [b for b in line if b is not None]
        for b in tiles:
            b.just_merged = False
        # Merge pass (bottom to top)
        merged_tiles = []
        i = len(tiles) - 1
        while i >= 0:
            if i > 0 and tiles[i].number == tiles[i - 1].number and not tiles[i].just_merged and not tiles[i - 1].just_merged:
                merged_block = Block(col, 0, tiles[i].number * 2, in_grid=True)
                merged_block.just_merged = True
                merged_tiles.insert(0, merged_block)
                moved = True
                i -= 2  # Skip the next tile, as it was merged
            else:
                merged_tiles.insert(0, tiles[i])
                i -= 1
        # Fill with None to match grid size
        while len(merged_tiles) < ROWS:
            merged_tiles.insert(0, None)
        # Place back in grid, shift down
        for row in range(ROWS):
            b = merged_tiles[row]
            if b is not None:
                if b.grid_x != col or b.grid_y != row:
                    moved = True
                b.grid_x = col
                b.grid_y = row
                b.in_grid = True
            grid[col][row] = b
    return moved

# --- Gravity Logic ---
def apply_gravity(grid):
    # For each column, let blocks fall straight down to fill empty spaces
    for col in range(COLUMNS):
        stack = [grid[col][row] for row in range(ROWS) if grid[col][row] is not None]
        for row in range(ROWS):
            grid[col][row] = None
        for i, block in enumerate(reversed(stack)):
            new_row = ROWS - 1 - i
            block.grid_x = col
            block.grid_y = new_row
            block.in_grid = True
            grid[col][new_row] = block

# --- Main Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("2048 Launcher Hybrid")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    block_image = None
    if os.path.exists(BLOCK_IMAGE_PATH):
        img = pygame.image.load(BLOCK_IMAGE_PATH).convert_alpha()
        block_image = pygame.transform.scale(img, (BLOCK_SIZE, BLOCK_SIZE))

    grid = [[None for _ in range(ROWS)] for _ in range(COLUMNS)]
    flying_blocks = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if mx < GRID_X_OFFSET:
                    number = random.choice(BLOCK_NUMBERS)
                    flying_blocks.append(Block(mx, my, number))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    move_blocks(grid, 1)
                elif event.key == pygame.K_a:
                    move_blocks(grid, -1)
                elif event.key == pygame.K_s:
                    move_blocks_down(grid)

        # Update flying blocks (parabolic motion)
        next_flying_blocks = []
        for block in flying_blocks:
            # Apply gravity and velocity
            block.vy += GRAVITY
            block.x += block.vx
            block.y += block.vy
            # Only snap to grid after landing
            if block.x + BLOCK_SIZE // 2 >= GRID_X_OFFSET:
                # Predict landing row and col
                col = int((block.x + BLOCK_SIZE // 2 - GRID_X_OFFSET) // BLOCK_SIZE)
                col = max(0, min(COLUMNS - 1, col))
                # Find the lowest empty cell in this column
                landed = False
                for row in range(ROWS - 1, -1, -1):
                    cell_x, cell_y = grid_to_screen(col, row)
                    # Check for collision with floor
                    if block.y + BLOCK_SIZE >= SCREEN_HEIGHT:
                        block.y = SCREEN_HEIGHT - BLOCK_SIZE
                        landed = True
                        break
                    # Check for collision with another block
                    if grid[col][row] is not None and block.y + BLOCK_SIZE >= cell_y:
                        block.y = cell_y - BLOCK_SIZE
                        landed = True
                        break
                if landed:
                    # After a horizontal collision, set block.vx = 0 and let gravity pull it down.
                    block.vx = 0
                    # Snap to grid
                    snap_col = int((block.x + BLOCK_SIZE // 2 - GRID_X_OFFSET) // BLOCK_SIZE)
                    snap_col = max(0, min(COLUMNS - 1, snap_col))
                    snap_row = int(block.y // BLOCK_SIZE)
                    # If cell is occupied, move up
                    while snap_row >= 0 and grid[snap_col][snap_row] is not None:
                        snap_row -= 1
                    if snap_row >= 0:
                        block.grid_x = snap_col
                        block.grid_y = snap_row
                        block.in_grid = True
                        block.falling = False
                        block.x, block.y = grid_to_screen(snap_col, snap_row)
                        grid[snap_col][snap_row] = block
                    # If column is full, discard the block
                else:
                    next_flying_blocks.append(block)
            else:
                next_flying_blocks.append(block)
        flying_blocks = next_flying_blocks

        # After flying blocks, apply gravity to grid
        apply_gravity(grid)

        # Draw everything
        screen.fill((30, 30, 30))
        # Draw grid area
        for col in range(COLUMNS):
            for row in range(ROWS):
                block = grid[col][row]
                if block is not None:
                    x, y = grid_to_screen(col, row)
                    pygame.draw.rect(screen, BLOCK_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))
                    num_surf = font.render(str(block.number), True, FONT_COLOR)
                    num_rect = num_surf.get_rect(center=(x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2))
                    screen.blit(num_surf, num_rect)
        # Draw flying blocks
        for block in flying_blocks:
            x, y = block.screen_pos()
            pygame.draw.rect(screen, BLOCK_COLOR, (x, y, BLOCK_SIZE, BLOCK_SIZE))
            num_surf = font.render(str(block.number), True, FONT_COLOR)
            num_rect = num_surf.get_rect(center=(x + BLOCK_SIZE // 2, y + BLOCK_SIZE // 2))
            screen.blit(num_surf, num_rect)
        # Draw grid lines
        for col in range(COLUMNS + 1):
            x = GRID_X_OFFSET + col * BLOCK_SIZE
            pygame.draw.line(screen, (60, 60, 60), (x, 0), (x, SCREEN_HEIGHT))
        for row in range(ROWS + 1):
            pygame.draw.line(screen, (60, 60, 60), (GRID_X_OFFSET, row * BLOCK_SIZE), (SCREEN_WIDTH, row * BLOCK_SIZE))
        # Draw launch zone line
        pygame.draw.line(screen, (200, 200, 200), (GRID_X_OFFSET, 0), (GRID_X_OFFSET, SCREEN_HEIGHT), 3)
        # Instructions
        text = font.render("Click left to launch, right is grid. A/D to move/merge!", True, (220, 220, 220))
        screen.blit(text, (20, 20))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 