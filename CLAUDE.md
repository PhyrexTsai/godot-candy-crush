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
- `candy_nodes: Array` — parallel 8x8 2D array holding the `ColorRect` nodes for each candy
- These two arrays must stay in sync at all times

### Game Loop Flow

1. **Init** (`_ready`): `_init_grid()` fills the grid with random types (avoiding initial matches via `_random_candy_no_match`), then `_draw_board()` creates all `ColorRect` nodes
2. **Input** (`_input`): Click to select a candy, click adjacent candy to attempt swap. `is_animating` flag blocks input during animations
3. **Swap** (`_try_swap`): Swaps data + animates. If no match found, swaps back
4. **Match Resolution** (`_process_matches`): Removes matched candies → applies gravity (`_apply_gravity`) → refills empty cells (`_refill`) → recursively checks for chain reactions

### Key Constants

- `GRID_SIZE = 8`, `CELL_SIZE = 64`, `CANDY_TYPES = 6`
- `BOARD_OFFSET = Vector2(384, 104)` — positions the 512x512 board centered in the viewport

### Visual Approach

All visuals are procedural `ColorRect` nodes — no sprite assets are used yet. The `assets/sprites/` directory exists but is empty. Candies are colored rectangles with a 4px margin.

## GDScript Conventions

- Use static typing (`:=`, `-> void`, typed arrays like `Array[Vector2i]`)
- Prefix private functions with underscore (`_init_grid`, `_find_matches`)
- Use `Vector2i` for grid coordinates, `Vector2` for pixel positions
- Animations use `Tween` with `await tween.finished`
