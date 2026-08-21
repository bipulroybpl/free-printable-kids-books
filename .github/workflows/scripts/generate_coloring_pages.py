#!/usr/bin/env python3
"""
Generate black-and-white line-art coloring pages entirely in code (no AI
image generation), for the drawing-fruits / drawing-flowers / drawing-animals
books.

Technique: each object is defined as a small "recipe" of primitive shapes
(ellipse, polygon, rectangle, pieslice) combined with add/subtract onto a
silhouette mask (simple constructive solid geometry -- e.g. an owl's eyes
are two circles *subtracted* from the body silhouette, a banana is a thick
curved arc, a pear is two unioned circles of different sizes). The filled
silhouette is then converted into a bold outline via edge detection +
dilation, so the final page is a clean white background with a single bold
black outline -- exactly the "line art coloring page" spec -- with no
external AI dependency and no content-safety review needed (deterministic
geometry, not generative imagery).

Usage:
    python generate_coloring_pages.py <path-to-book-dir>

Reads:
    <book-dir>/prompts/coloring_config.json   {"items": [{"page": N, "shape": "apple"}, ...]}

Writes:
    <book-dir>/assets/final/page-N.png
"""
import argparse
import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter

CANVAS_SIZE = 2000
STROKE = 16


def F(frac):
    """Fraction of canvas size -> pixels."""
    return frac * CANVAS_SIZE


def circle_bbox(cx, cy, r):
    return [F(cx - r), F(cy - r), F(cx + r), F(cy + r)]


def petal_ring(cx, cy, r_center, r_petal, count, r_offset):
    ops = [("ellipse", circle_bbox(cx, cy, r_center), "add")]
    for i in range(count):
        angle = 2 * math.pi * i / count
        px = cx + r_offset * math.cos(angle)
        py = cy + r_offset * math.sin(angle)
        ops.append(("ellipse", circle_bbox(px, py, r_petal), "add"))
    return ops


def apply_ops(mask, ops):
    draw = ImageDraw.Draw(mask)
    for kind, geom, mode in ops:
        fill = 255 if mode == "add" else 0
        if kind == "ellipse":
            draw.ellipse(geom, fill=fill)
        elif kind == "polygon":
            draw.polygon(geom, fill=fill)
        elif kind == "rectangle":
            draw.rectangle(geom, fill=fill)
        elif kind == "pieslice":
            bbox, start, end = geom
            draw.pieslice(bbox, start, end, fill=fill)
        elif kind == "arc_band":
            bbox, start, end, width = geom
            draw.arc(bbox, start, end, fill=fill, width=width)
        else:
            raise ValueError(f"Unknown op kind: {kind}")


def silhouette_to_page(ops, bg_rgb=(255, 255, 255)):
    mask = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), 0)
    apply_ops(mask, ops)

    edges = mask.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda p: 255 if p > 20 else 0)
    for _ in range(max(1, STROKE // 4)):
        edges = edges.filter(ImageFilter.MaxFilter(5))

    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg_rgb)
    black = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (20, 20, 20))
    canvas.paste(black, (0, 0), mask=edges)
    return canvas


# ---- shape recipes -------------------------------------------------------

def recipe_apple():
    ops = [("ellipse", circle_bbox(0.5, 0.55, 0.28), "add")]
    ops.append(("ellipse", circle_bbox(0.5, 0.30, 0.06), "sub"))  # top dip
    ops.append(("rectangle", [F(0.485), F(0.20), F(0.515), F(0.32)], "add"))  # stem
    ops.append(("ellipse", circle_bbox(0.60, 0.24, 0.09), "add"))  # leaf
    return ops


def recipe_banana():
    bbox = [F(0.20), F(0.15), F(0.95), F(0.90)]
    return [("arc_band", (bbox, 200, 340, round(F(0.16))), "add")]


def recipe_orange():
    ops = [("ellipse", circle_bbox(0.5, 0.55, 0.27), "add")]
    ops.append(("rectangle", [F(0.485), F(0.24), F(0.515), F(0.30)], "add"))
    ops.append(("ellipse", circle_bbox(0.60, 0.22, 0.08), "add"))
    return ops


GRAPE_CENTERS = [
    (0.5, 0.35), (0.40, 0.45), (0.60, 0.45),
    (0.32, 0.57), (0.5, 0.57), (0.68, 0.57),
    (0.40, 0.69), (0.60, 0.69), (0.5, 0.80),
]


def draw_grapes_direct(canvas):
    """Grapes need each circle's own outline visible (overlapping is normal
    for a grape-bunch drawing) -- the CSG merge-and-edge-detect technique
    used elsewhere erases those internal seams, so this bypasses it and
    draws individual circle outlines directly instead."""
    draw = ImageDraw.Draw(canvas)
    for cx, cy in GRAPE_CENTERS:
        draw.ellipse(circle_bbox(cx, cy, 0.11), outline=(20, 20, 20), width=STROKE)
    draw.arc([F(0.42), F(0.15), F(0.58), F(0.35)], 200, 340, fill=(20, 20, 20), width=STROKE)


def recipe_strawberry():
    # classic simplified heart/strawberry construction: two circles for the
    # rounded shoulders + a triangle tangent below them for the pointed tip
    # -- much more reliable than a hand-tuned parametric curve, and reads
    # unambiguously as a heart/berry silhouette rather than a plain circle
    ops = [
        ("ellipse", circle_bbox(0.38, 0.42, 0.17), "add"),
        ("ellipse", circle_bbox(0.62, 0.42, 0.17), "add"),
        ("polygon", [(F(0.22), F(0.42)), (F(0.78), F(0.42)), (F(0.5), F(0.90))], "add"),
    ]
    leaf = [(0.5, 0.18), (0.64, 0.28), (0.5, 0.34), (0.36, 0.28)]
    ops.append(("polygon", [(F(x), F(y)) for x, y in leaf], "add"))
    return ops


def recipe_watermelon():
    bbox = [F(0.15), F(0.30), F(0.85), F(1.00)]
    return [("pieslice", (bbox, 180, 360), "add")]


def recipe_pineapple():
    ops = [("ellipse", circle_bbox(0.5, 0.62, 0.24), "add")]
    leaves = [
        [(0.5, 0.40), (0.40, 0.15), (0.5, 0.30), (0.60, 0.15)],
        [(0.4, 0.42), (0.22, 0.20), (0.42, 0.32)],
        [(0.6, 0.42), (0.78, 0.20), (0.58, 0.32)],
    ]
    for leaf in leaves:
        ops.append(("polygon", [(F(x), F(y)) for x, y in leaf], "add"))
    return ops


def recipe_pear():
    ops = [("ellipse", circle_bbox(0.5, 0.36, 0.16), "add")]
    ops.append(("ellipse", circle_bbox(0.5, 0.65, 0.26), "add"))
    ops.append(("rectangle", [F(0.485), F(0.12), F(0.515), F(0.22)], "add"))
    return ops


def recipe_sunflower():
    return petal_ring(0.5, 0.42, 0.14, 0.11, 8, 0.24) + [
        ("rectangle", [F(0.485), F(0.55), F(0.515), F(0.90)], "add"),
    ]


def recipe_tulip():
    # rounded 3-petal cup (two side petals + a taller center petal, unioned)
    # instead of a sharp polygon -- a coarse triangle-based cup reads as an
    # arrow/rocket, not a flower
    ops = [
        ("ellipse", [F(0.28), F(0.24), F(0.52), F(0.52)], "add"),
        ("ellipse", [F(0.48), F(0.24), F(0.72), F(0.52)], "add"),
        ("ellipse", [F(0.38), F(0.14), F(0.62), F(0.48)], "add"),
    ]
    ops.append(("rectangle", [F(0.485), F(0.42), F(0.515), F(0.88)], "add"))
    leaf = [(0.515, 0.65), (0.68, 0.58), (0.60, 0.72)]
    ops.append(("polygon", [(F(x), F(y)) for x, y in leaf], "add"))
    return ops


def recipe_daisy():
    return petal_ring(0.5, 0.45, 0.10, 0.08, 10, 0.20) + [
        ("rectangle", [F(0.485), F(0.53), F(0.515), F(0.90)], "add"),
    ]


def recipe_rose():
    ops = []
    for i, r in enumerate([0.24, 0.18, 0.12, 0.06]):
        cx = 0.5 + (0.03 if i % 2 else -0.03)
        ops.append(("ellipse", circle_bbox(cx, 0.40, r), "add" if i % 2 == 0 else "sub"))
    ops.append(("rectangle", [F(0.485), F(0.55), F(0.515), F(0.90)], "add"))
    return ops


def recipe_tree():
    ops = [("ellipse", circle_bbox(0.5, 0.32, 0.22), "add")]
    ops.append(("ellipse", circle_bbox(0.34, 0.42, 0.15), "add"))
    ops.append(("ellipse", circle_bbox(0.66, 0.42, 0.15), "add"))
    ops.append(("rectangle", [F(0.46), F(0.50), F(0.54), F(0.90)], "add"))
    return ops


def recipe_butterfly():
    ops = [("ellipse", [F(0.14), F(0.20), F(0.48), F(0.52)], "add")]
    ops.append(("ellipse", [F(0.52), F(0.20), F(0.86), F(0.52)], "add"))
    ops.append(("ellipse", [F(0.20), F(0.50), F(0.46), F(0.78)], "add"))
    ops.append(("ellipse", [F(0.54), F(0.50), F(0.80), F(0.78)], "add"))
    ops.append(("rectangle", [F(0.47), F(0.22), F(0.53), F(0.78)], "add"))
    ops.append(("polygon", [(F(0.47), F(0.22)), (F(0.40), F(0.10)), (F(0.45), F(0.20))], "add"))
    ops.append(("polygon", [(F(0.53), F(0.22)), (F(0.60), F(0.10)), (F(0.55), F(0.20))], "add"))
    return ops


def recipe_leaf():
    body = [(0.5, 0.12), (0.80, 0.45), (0.5, 0.92), (0.20, 0.45)]
    return [("polygon", [(F(x), F(y)) for x, y in body], "add")]


def recipe_mushroom():
    ops = [("pieslice", ([F(0.22), F(0.15), F(0.78), F(0.65)], 180, 360), "add")]
    ops.append(("rectangle", [F(0.40), F(0.50), F(0.60), F(0.88)], "add"))
    return ops


def recipe_cow():
    ops = [("ellipse", [F(0.20), F(0.42), F(0.80), F(0.75)], "add")]
    ops.append(("ellipse", circle_bbox(0.78, 0.42, 0.14), "add"))
    ops.append(("ellipse", circle_bbox(0.70, 0.28, 0.06), "add"))
    ops.append(("ellipse", circle_bbox(0.86, 0.28, 0.06), "add"))
    for lx in (0.30, 0.42, 0.58, 0.70):
        ops.append(("rectangle", [F(lx - 0.03), F(0.72), F(lx + 0.03), F(0.92)], "add"))
    return ops


def recipe_dog():
    ops = [("ellipse", [F(0.22), F(0.44), F(0.78), F(0.74)], "add")]
    ops.append(("ellipse", circle_bbox(0.76, 0.40, 0.16), "add"))
    ops.append(("ellipse", circle_bbox(0.68, 0.30, 0.08), "add"))
    ops.append(("ellipse", circle_bbox(0.86, 0.32, 0.07), "add"))
    for lx in (0.32, 0.44, 0.58, 0.70):
        ops.append(("rectangle", [F(lx - 0.03), F(0.70), F(lx + 0.03), F(0.90)], "add"))
    ops.append(("ellipse", circle_bbox(0.20, 0.50, 0.06), "add"))
    return ops


def recipe_cat():
    ops = [("ellipse", [F(0.24), F(0.46), F(0.76), F(0.74)], "add")]
    ops.append(("ellipse", circle_bbox(0.74, 0.38, 0.15), "add"))
    ops.append(("polygon", [(F(0.64), F(0.28)), (F(0.68), F(0.16)), (F(0.72), F(0.27))], "add"))
    ops.append(("polygon", [(F(0.80), F(0.27)), (F(0.84), F(0.16)), (F(0.86), F(0.29))], "add"))
    for lx in (0.34, 0.46, 0.58, 0.68):
        ops.append(("rectangle", [F(lx - 0.03), F(0.70), F(lx + 0.03), F(0.88)], "add"))
    return ops


def recipe_duck():
    ops = [("ellipse", [F(0.22), F(0.40), F(0.78), F(0.78)], "add")]
    ops.append(("ellipse", circle_bbox(0.72, 0.36, 0.14), "add"))
    ops.append(("polygon", [(F(0.83), F(0.34)), (F(0.94), F(0.37)), (F(0.83), F(0.42))], "add"))
    return ops


def recipe_elephant():
    ops = [("ellipse", [F(0.18), F(0.42), F(0.75), F(0.80)], "add")]
    ops.append(("ellipse", circle_bbox(0.70, 0.42, 0.18), "add"))
    ops.append(("ellipse", circle_bbox(0.80, 0.30, 0.16), "add"))
    # trunk must extend well below the body's bottom edge (y=0.80) AND clear
    # of the rightmost leg (x up to 0.695) to be visible as its own shape --
    # too close to either and it merges into a single blended silhouette
    ops.append(("polygon", [(F(0.72), F(0.58)), (F(0.86), F(0.60)), (F(0.84), F(0.97)), (F(0.76), F(0.97))], "add"))
    for lx in (0.28, 0.40, 0.55, 0.65):
        ops.append(("rectangle", [F(lx - 0.045), F(0.75), F(lx + 0.045), F(0.94)], "add"))
    return ops


def recipe_rabbit():
    ops = [("ellipse", [F(0.28), F(0.48), F(0.72), F(0.80)], "add")]
    ops.append(("ellipse", circle_bbox(0.5, 0.40, 0.15), "add"))
    ops.append(("ellipse", [F(0.36), F(0.06), F(0.46), F(0.36)], "add"))
    ops.append(("ellipse", [F(0.54), F(0.06), F(0.64), F(0.36)], "add"))
    ops.append(("ellipse", circle_bbox(0.72, 0.62, 0.06), "add"))
    return ops


def recipe_fish():
    ops = [("ellipse", [F(0.20), F(0.35), F(0.72), F(0.65)], "add")]
    ops.append(("polygon", [(F(0.70), F(0.30)), (F(0.90), F(0.20)), (F(0.90), F(0.80)), (F(0.70), F(0.70))], "add"))
    ops.append(("polygon", [(F(0.40), F(0.34)), (F(0.46), F(0.18)), (F(0.52), F(0.34))], "add"))
    ops.append(("ellipse", circle_bbox(0.30, 0.46, 0.03), "sub"))
    return ops


def recipe_owl():
    # eyes must NOT overlap -- two overlapping subtract-circles merge into a
    # single heart-shaped notch instead of two round eyes (the original bug,
    # which also read as a cat/pumpkin face without a visible beak)
    ops = [("ellipse", [F(0.24), F(0.28), F(0.76), F(0.82)], "add")]
    ops.append(("ellipse", circle_bbox(0.35, 0.46, 0.09), "sub"))
    ops.append(("ellipse", circle_bbox(0.65, 0.46, 0.09), "sub"))
    ops.append(("polygon", [(F(0.30), F(0.28)), (F(0.34), F(0.14)), (F(0.40), F(0.27))], "add"))
    ops.append(("polygon", [(F(0.60), F(0.27)), (F(0.66), F(0.14)), (F(0.70), F(0.28))], "add"))
    ops.append(("polygon", [(F(0.44), F(0.54)), (F(0.5), F(0.66)), (F(0.56), F(0.54))], "add"))
    return ops


DIRECT_DRAW = {
    "grapes": draw_grapes_direct,
}

RECIPES = {
    "apple": recipe_apple, "banana": recipe_banana, "orange": recipe_orange,
    "strawberry": recipe_strawberry, "watermelon": recipe_watermelon,
    "pineapple": recipe_pineapple, "pear": recipe_pear,
    "sunflower": recipe_sunflower, "tulip": recipe_tulip, "daisy": recipe_daisy,
    "rose": recipe_rose, "tree": recipe_tree, "butterfly": recipe_butterfly,
    "leaf": recipe_leaf, "mushroom": recipe_mushroom,
    "cow": recipe_cow, "dog": recipe_dog, "cat": recipe_cat, "duck": recipe_duck,
    "elephant": recipe_elephant, "rabbit": recipe_rabbit, "fish": recipe_fish, "owl": recipe_owl,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    book_dir = args.book_dir
    final_dir = os.path.join(book_dir, "assets", "final")
    os.makedirs(final_dir, exist_ok=True)

    with open(os.path.join(book_dir, "prompts", "coloring_config.json"), encoding="utf-8") as f:
        config = json.load(f)

    for item in config["items"]:
        page = item["page"]
        shape = item["shape"]
        if shape in DIRECT_DRAW:
            page_img = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255))
            DIRECT_DRAW[shape](page_img)
        elif shape in RECIPES:
            ops = RECIPES[shape]()
            page_img = silhouette_to_page(ops)
        else:
            print(f"Page {page}: unknown shape '{shape}', skipping")
            continue
        out_path = os.path.join(final_dir, f"page-{page}.png")
        page_img.save(out_path)
        print(f"Page {page} ({shape}): rendered to {out_path}", flush=True)

    print(f"Done: {len(config['items'])} page(s) rendered", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
