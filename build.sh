#!/bin/bash

# Build script for macOS .app bundle using PyInstaller
# Usage: bash build.sh

# Set script to exit on error
set -e

# Path setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GAME_DIR="$SCRIPT_DIR/Game develop"
PYGAME_SCRIPT="pygame_block_launcher.py"
ASSETS_DIR="assets"

# Check for PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Please install it with 'pip install pyinstaller'."
    exit 1
fi

cd "$GAME_DIR"

# Build command
# --windowed: no terminal
# --onefile: single executable (optional, can be omitted for .app bundle)
# --add-data: include assets folder (format: src:dest)
# --noconfirm: overwrite previous build
# --name: set app name

if [ -d "$ASSETS_DIR" ]; then
    ADD_DATA_ARG="--add-data $ASSETS_DIR:$ASSETS_DIR"
else
    ADD_DATA_ARG=""
fi

pyinstaller \
    --windowed \
    --noconfirm \
    --name "PygameBlockLauncher" \
    $ADD_DATA_ARG \
    "$PYGAME_SCRIPT"

# The .app bundle will be in the 'dist' folder inside 'Game develop'.
echo "Build complete. Find your .app in: $GAME_DIR/dist/PygameBlockLauncher.app" 