# Candy Crush

A match-3 puzzle game built with Godot 4.6 and GDScript.

## Gameplay

- Click a candy to select it, then click an adjacent candy to swap
- Match 3 or more same-colored candies in a row/column to score points
- Matched candies are removed, remaining candies fall down, and new candies fill in from the top
- Chain reactions are automatically resolved

## How to Run

Open the project in Godot 4.6 and press F5, or run from command line:

```bash
godot --path .
```

## Technical Details

- **Engine**: Godot 4.6 (GL Compatibility renderer)
- **Resolution**: 1280x720
- **Board**: 8x8 grid, 6 candy types
- **Rendering**: Procedural `ColorRect` nodes — no external assets required
- **Animation**: Tween-based swap, gravity drop, and refill animations

## Project Structure

```
scenes/main.tscn    # Main scene (root Node2D)
scripts/main.gd     # All game logic
assets/sprites/     # Reserved for future sprite assets
```

## License

All rights reserved.
