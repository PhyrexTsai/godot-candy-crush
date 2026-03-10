# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Candy Crush clone built with **Godot 4.6** using GDScript. 2D match-3 puzzle game with GL Compatibility renderer. Viewport is 1280x720.

## Running the Project

Use the Godot MCP server tools (`mcp__godot__run_project`, `mcp__godot__stop_project`) to run and test the game. The main scene is `res://scenes/main.tscn`.

## Architecture

The entire game logic lives in a single script: `scripts/main.gd`, attached to the root `Node2D` in `scenes/main.tscn`.

### Core Data Model

- `grid: Array` — 8x8 2D array of ints representing candy types (0–5), or -1 for empty
- `candy_nodes: Array` — parallel 8x8 2D array holding the `Sprite2D` nodes for each candy
- These two arrays must stay in sync at all times

### Game Loop Flow

1. **Init** (`_ready`): `_init_sfx()` loads audio, `_init_grid()` fills the grid with random types (avoiding initial matches via `_random_candy_no_match`), then `_draw_board()` creates all `Sprite2D` nodes
2. **Input** (`_input`): Click to select a candy, click adjacent candy to attempt swap. `is_animating` flag blocks input during animations
3. **Swap** (`_try_swap`): Swaps data + animates. If no match found, swaps back
4. **Match Resolution** (`_process_matches`): Removes matched candies → applies gravity (`_apply_gravity`) → refills empty cells (`_refill`) → recursively checks for chain reactions

### Key Constants

- `GRID_SIZE = 8`, `CELL_SIZE = 64`, `CANDY_TYPES = 6`
- `BOARD_OFFSET = Vector2(384, 104)` — positions the 512x512 board centered in the viewport

### Visual Approach

Candies are `Sprite2D` nodes using preloaded PNG textures (`CANDY_TEXTURES` array). Each candy type has a distinct shape and color (circle/red, square/blue, diamond/green, triangle/yellow, star/purple, hexagon/orange). Board background and cells remain `ColorRect` nodes.

### Audio

5 sound effects loaded as `AudioStreamPlayer` nodes via `_init_sfx()`:

| File | Trigger |
|------|---------|
| `swap.ogg` | `_try_swap()` start |
| `match.ogg` | `_process_matches()` first match |
| `no_match.ogg` | `_try_swap()` swap-back |
| `cascade.ogg` | `_process_matches()` chain reaction |
| `refill.ogg` | `_refill()` complete |

### Asset Generation

Assets are procedurally generated via Python scripts in `tools/`:

- `tools/generate_sprites.py` — generates 6 candy PNGs (56x56) to `assets/sprites/` using Pillow
- `tools/generate_sfx.py` — generates 5 OGG sound effects to `assets/sfx/` using numpy + ffmpeg

Re-run to regenerate: `python3 tools/generate_sprites.py` or `python3 tools/generate_sfx.py`

### Web Export & Deployment

- `export.sh` — one-command web export + deploy to `gh-pages` branch
- Config: `export_presets.cfg` (preset name: "Web", output: `./export/index.html`)
- Guide: `docs/web-export-guide.md`

## GDScript Conventions

- Use static typing (`:=`, `-> void`, typed arrays like `Array[Vector2i]`)
- Prefix private functions with underscore (`_init_grid`, `_find_matches`)
- Use `Vector2i` for grid coordinates, `Vector2` for pixel positions
- Animations use `Tween` with `await tween.finished`
