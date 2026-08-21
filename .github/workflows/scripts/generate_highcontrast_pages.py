#!/usr/bin/env python3
"""
Generate solid-filled high-contrast board-book pages entirely in code (no AI
image generation).

Rationale: AI generation for this book failed badly and repeatedly -- blurry
gradient blobs instead of sharp shapes, and on two pages produced a
realistic human face and an anime-style animal instead of the required
plain abstract shape. This is the most safety-sensitive age band (0-1,
board-book shapes only), so it's rendered deterministically instead: solid
black/white/red filled shapes via Pillow primitives, no photographic or
generative content at all.

Usage:
    python generate_highcontrast_pages.py <path-to-book-dir>

Reads:
    <book-dir>/prompts/highcontrast_config.json  {"items": [{"page": N, "shape": "circle"}, ...]}

Writes:
    <book-dir>/assets/final/page-N.png
"""
import argparse
import json
import math
import os

from PIL import Image, ImageDraw

CANVAS_SIZE = 2000
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
RED = (227, 6, 19)


def F(frac):
    return frac * CANVAS_SIZE


def circle_bbox(cx, cy, r):
    return [F(cx - r), F(cy - r), F(cx + r), F(cy + r)]


def draw_circle(draw):
    draw.ellipse(circle_bbox(0.5, 0.5, 0.36), fill=BLACK)


def draw_checkerboard(draw):
    n = 4
    cell = 1.0 / n
    for row in range(n):
        for col in range(n):
            if (row + col) % 2 == 0:
                x0, y0 = col * cell, row * cell
                draw.rectangle([F(x0), F(y0), F(x0 + cell), F(y0 + cell)], fill=BLACK)


def draw_wavy_stripe(draw):
    points = []
    for i in range(201):
        t = i / 200
        x = 0.1 + t * 0.8
        y = 0.5 + 0.28 * math.sin(t * 2 * math.pi)
        points.append((F(x), F(y)))
    draw.line(points, fill=BLACK, width=round(F(0.09)), joint="curve")


def draw_square(draw):
    m = 0.16
    draw.rectangle([F(m), F(m), F(1 - m), F(1 - m)], fill=BLACK)


def draw_bullseye(draw):
    radii = [0.42, 0.32, 0.22, 0.12]
    colors = [BLACK, WHITE, BLACK, WHITE]
    for r, c in zip(radii, colors):
        draw.ellipse(circle_bbox(0.5, 0.5, r), fill=c)


def draw_face(draw):
    draw.ellipse([F(0.20), F(0.16), F(0.80), F(0.84)], fill=WHITE, outline=BLACK, width=round(F(0.015)))
    draw.ellipse(circle_bbox(0.36, 0.42, 0.07), fill=BLACK)
    draw.ellipse(circle_bbox(0.64, 0.42, 0.07), fill=BLACK)
    draw.ellipse(circle_bbox(0.5, 0.56, 0.05), fill=RED)
    draw.arc([F(0.34), F(0.55), F(0.66), F(0.78)], 20, 160, fill=BLACK, width=round(F(0.02)))


def draw_stripes_vertical(draw):
    n = 6
    cell = 1.0 / n
    for i in range(n):
        if i % 2 == 0:
            draw.rectangle([F(i * cell), 0, F((i + 1) * cell), F(1.0)], fill=BLACK)


def draw_star(draw):
    cx, cy, r_out, r_in = 0.5, 0.52, 0.38, 0.16
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = r_out if i % 2 == 0 else r_in
        points.append((F(cx + r * math.cos(angle)), F(cy - r * math.sin(angle))))
    draw.polygon(points, fill=BLACK)


def draw_heart(draw):
    draw.ellipse(circle_bbox(0.36, 0.40, 0.18), fill=RED, outline=BLACK, width=round(F(0.012)))
    draw.ellipse(circle_bbox(0.64, 0.40, 0.18), fill=RED, outline=BLACK, width=round(F(0.012)))
    draw.polygon(
        [(F(0.20), F(0.42)), (F(0.80), F(0.42)), (F(0.5), F(0.86))],
        fill=RED, outline=BLACK, width=round(F(0.012)),
    )


def draw_spiral(draw):
    # a true continuous spiral stroke -- using concentric rings here (like
    # bullseye) made this page visually identical to the bullseye page,
    # a real duplication within the same book
    points = []
    turns = 2.5
    steps = 300
    for i in range(steps + 1):
        t = i / steps
        angle = t * turns * 2 * math.pi
        r = 0.04 + t * 0.40
        x = 0.5 + r * math.cos(angle)
        y = 0.5 + r * math.sin(angle)
        points.append((F(x), F(y)))
    draw.line(points, fill=BLACK, width=round(F(0.05)), joint="curve")


SHAPES = {
    "circle": draw_circle,
    "checkerboard": draw_checkerboard,
    "wavy_stripe": draw_wavy_stripe,
    "square": draw_square,
    "bullseye": draw_bullseye,
    "face": draw_face,
    "stripes_vertical": draw_stripes_vertical,
    "star": draw_star,
    "heart": draw_heart,
    "spiral": draw_spiral,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    book_dir = args.book_dir
    final_dir = os.path.join(book_dir, "assets", "final")
    os.makedirs(final_dir, exist_ok=True)

    with open(os.path.join(book_dir, "prompts", "highcontrast_config.json"), encoding="utf-8") as f:
        config = json.load(f)

    for item in config["items"]:
        page = item["page"]
        shape = item["shape"]
        if shape not in SHAPES:
            print(f"Page {page}: unknown shape '{shape}', skipping")
            continue
        canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), WHITE)
        draw = ImageDraw.Draw(canvas)
        SHAPES[shape](draw)
        out_path = os.path.join(final_dir, f"page-{page}.png")
        canvas.save(out_path)
        print(f"Page {page} ({shape}): rendered to {out_path}", flush=True)

    print(f"Done: {len(config['items'])} page(s) rendered", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
