# 2048 Launcher Hybrid

A hybrid arcade-style game combining projectile physics and classic 2048 merging mechanics.  
Players launch numbered blocks from the left side of the screen. Blocks land on a 2048-style grid on the right, where they can be merged via keyboard input.

## How to Play

- **Launch Blocks**:  
  Click anywhere on the **left half** of the screen to fire a block toward the right. Each block has a random number (2, 4, 8, 16, 32, or 64) and follows a projectile path.

- **Landing and Snapping**:  
  When a block enters the **right half**, it will snap into the nearest valid grid cell, falling into place automatically.

- **2048 Controls**:  
  Once blocks are on the grid, press keys to shift and merge:
  - `A` – Move all blocks left (merge same numbers)
  - `D` – Move all blocks right (merge same numbers)
  - `S` – Apply vertical merges downwards

- **Merging Logic**:  
  Blocks with the same number that collide in a move will merge into one block of double the value. Merge only once per move per block.

## Features

- Parabolic projectile physics for launching blocks
- Grid-based snapping system on the right half of the screen
- 2048-style block merging with animation-ready logic
- Automatic gravity application to fill empty grid spaces
- Smooth handling of multiple merges and block stacking
- Visual grid lines for clarity

## Screenshots

*(You can paste screenshots or GIFs here of gameplay once available.)*

## 🔧 Dependencies

- Python 3.x
- `pygame`

Install dependencies with:

```bash
pip install pygame
