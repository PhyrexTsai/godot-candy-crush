#!/usr/bin/env python3
"""Generate 6 candy sprites with distinct shapes and colors."""

import math
import os
from PIL import Image, ImageDraw, ImageFilter

SIZE = 56
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")

# (base_color, highlight_color, shadow_color)
CANDIES = [
    # 0: Red circle
    {"color": (220, 50, 50), "hi": (255, 140, 140), "sh": (150, 20, 20), "shape": "circle"},
    # 1: Blue square
    {"color": (50, 100, 220), "hi": (130, 170, 255), "sh": (20, 50, 150), "shape": "square"},
    # 2: Green diamond
    {"color": (50, 190, 70), "hi": (140, 240, 150), "sh": (20, 120, 30), "shape": "diamond"},
    # 3: Yellow triangle
    {"color": (230, 210, 40), "hi": (255, 245, 140), "sh": (170, 150, 10), "shape": "triangle"},
    # 4: Purple star
    {"color": (160, 60, 210), "hi": (210, 150, 255), "sh": (100, 20, 140), "shape": "star"},
    # 5: Orange hexagon
    {"color": (230, 130, 30), "hi": (255, 190, 110), "sh": (170, 80, 10), "shape": "hexagon"},
]


def draw_circle(draw: ImageDraw.Draw, candy: dict):
    cx, cy = SIZE // 2, SIZE // 2
    r = SIZE // 2 - 4
    # Shadow
    draw.ellipse([cx - r + 2, cy - r + 2, cx + r + 2, cy + r + 2], fill=candy["sh"])
    # Base
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=candy["color"])
    # Highlight
    hr = r // 2
    draw.ellipse([cx - hr // 2 - 4, cy - hr // 2 - 4, cx + hr // 2 - 4, cy + hr // 2 - 4], fill=candy["hi"])


def draw_square(draw: ImageDraw.Draw, candy: dict):
    m = 6
    # Shadow
    draw.rounded_rectangle([m + 2, m + 2, SIZE - m + 2, SIZE - m + 2], radius=6, fill=candy["sh"])
    # Base
    draw.rounded_rectangle([m, m, SIZE - m, SIZE - m], radius=6, fill=candy["color"])
    # Highlight
    draw.rounded_rectangle([m + 6, m + 6, SIZE // 2, SIZE // 2], radius=3, fill=candy["hi"])


def draw_diamond(draw: ImageDraw.Draw, candy: dict):
    cx, cy = SIZE // 2, SIZE // 2
    s = SIZE // 2 - 5
    pts = [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)]
    shadow = [(x + 2, y + 2) for x, y in pts]
    draw.polygon(shadow, fill=candy["sh"])
    draw.polygon(pts, fill=candy["color"])
    # Highlight
    hs = s // 3
    hi_pts = [(cx - 2, cy - hs - 2), (cx + hs - 2, cy - 2), (cx - 2, cy + hs - 2), (cx - hs - 2, cy - 2)]
    draw.polygon(hi_pts, fill=candy["hi"])


def draw_triangle(draw: ImageDraw.Draw, candy: dict):
    cx, cy = SIZE // 2, SIZE // 2
    s = SIZE // 2 - 4
    pts = [
        (cx, cy - s),
        (cx + int(s * math.cos(math.radians(30))), cy + s // 2 + 2),
        (cx - int(s * math.cos(math.radians(30))), cy + s // 2 + 2),
    ]
    shadow = [(x + 2, y + 2) for x, y in pts]
    draw.polygon(shadow, fill=candy["sh"])
    draw.polygon(pts, fill=candy["color"])
    # Highlight
    draw.polygon([(cx, cy - s + 8), (cx + 6, cy - 2), (cx - 6, cy - 2)], fill=candy["hi"])


def draw_star(draw: ImageDraw.Draw, candy: dict):
    cx, cy = SIZE // 2, SIZE // 2
    outer_r = SIZE // 2 - 4
    inner_r = outer_r * 0.4
    pts = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        r = outer_r if i % 2 == 0 else inner_r
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    shadow = [(x + 2, y + 2) for x, y in pts]
    draw.polygon(shadow, fill=candy["sh"])
    draw.polygon(pts, fill=candy["color"])
    # Highlight center
    draw.ellipse([cx - 5, cy - 5, cx + 3, cy + 3], fill=candy["hi"])


def draw_hexagon(draw: ImageDraw.Draw, candy: dict):
    cx, cy = SIZE // 2, SIZE // 2
    r = SIZE // 2 - 5
    pts = []
    for i in range(6):
        angle = math.radians(i * 60 - 30)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    shadow = [(x + 2, y + 2) for x, y in pts]
    draw.polygon(shadow, fill=candy["sh"])
    draw.polygon(pts, fill=candy["color"])
    # Highlight
    hr = r // 3
    hi_pts = []
    for i in range(6):
        angle = math.radians(i * 60 - 30)
        hi_pts.append((cx + hr * math.cos(angle) - 3, cy + hr * math.sin(angle) - 3))
    draw.polygon(hi_pts, fill=candy["hi"])


SHAPE_FNS = {
    "circle": draw_circle,
    "square": draw_square,
    "diamond": draw_diamond,
    "triangle": draw_triangle,
    "star": draw_star,
    "hexagon": draw_hexagon,
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, candy in enumerate(CANDIES):
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        SHAPE_FNS[candy["shape"]](draw, candy)
        # Slight blur for smoother edges
        img = img.filter(ImageFilter.SMOOTH)
        path = os.path.join(OUTPUT_DIR, f"candy_{i}.png")
        img.save(path)
        print(f"  -> candy_{i}.png ({candy['shape']}, {candy['color']})")

    print(f"\nDone! {len(CANDIES)} sprites in assets/sprites/")


if __name__ == "__main__":
    main()
