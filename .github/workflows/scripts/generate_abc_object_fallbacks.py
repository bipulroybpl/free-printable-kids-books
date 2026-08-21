#!/usr/bin/env python3
"""
Code-generated replacements for the 8 baby-first-abc object images that
failed AI generation: hat, kite, queen (crown), sun, umbrella, violin,
xylophone, yoyo.

Rationale: reviewing all 26 AI-generated objects found 8 failures, and
critically 4 of them were unprompted photorealistic/anime human faces
instead of the requested plain object (H "hat" -> a girl's portrait, Q
"queen" -> an adult-coded doll bust, S "sun" -> a girl's portrait, V
"violin" -> an anime girl's face) -- a real safety pattern: anything
semantically associated with a person (worn, held, performed) seems to
pull the model toward rendering a human. The other two failures (K
"kite", X "xylophone") rendered as unrecognizable blurry shapes, and Y
"yoyo" rendered as a plain ball with no yoyo silhouette at all.

Each object here is a solid color-filled shape with a black outline and
the same googly-eyes-and-smile face used on the successful AI objects and
the code-generated letters, so it stays visually consistent with the rest
of the book.

Usage:
    python generate_abc_object_fallbacks.py <path-to-book-dir>

Writes:
    <book-dir>/assets/raw/page-N-object.png  for the 8 pages listed in OBJECTS
"""
import argparse
import os

from PIL import Image, ImageDraw

CANVAS_SIZE = 2000
OUTLINE = (30, 30, 30)
WHITE = (255, 255, 255)


def F(frac):
    return frac * CANVAS_SIZE


def circle_bbox(cx, cy, r):
    return [F(cx - r), F(cy - r), F(cx + r), F(cy + r)]


def add_face(draw, cx, cy, scale=1.0):
    eye_r = CANVAS_SIZE * 0.05 * scale
    pupil_r = eye_r * 0.45
    spacing = CANVAS_SIZE * 0.09 * scale
    for ex in (cx - spacing, cx + spacing):
        draw.ellipse([ex - eye_r, cy - eye_r, ex + eye_r, cy + eye_r], fill=WHITE, outline=OUTLINE, width=6)
        draw.ellipse([ex - pupil_r, cy - pupil_r, ex + pupil_r, cy + pupil_r], fill=OUTLINE)
    smile_w = spacing * 1.2
    smile_y = cy + eye_r * 1.7
    draw.arc([cx - smile_w, smile_y - smile_w * 0.5, cx + smile_w, smile_y + smile_w * 0.5], 20, 160, fill=OUTLINE, width=10)


def draw_hat(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    draw.ellipse([F(0.12), F(0.55), F(0.88), F(0.72)], fill=(250, 220, 90), outline=OUTLINE, width=14)
    draw.ellipse([F(0.28), F(0.28), F(0.72), F(0.62)], fill=(250, 220, 90), outline=OUTLINE, width=14)
    add_face(draw, F(0.5), F(0.46))
    return canvas


def draw_kite(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    draw.polygon([(F(0.5), F(0.14)), (F(0.78), F(0.42)), (F(0.5), F(0.72)), (F(0.22), F(0.42))],
                 fill=(120, 190, 240), outline=OUTLINE, width=14)
    draw.line([F(0.22), F(0.42), F(0.78), F(0.42)], fill=OUTLINE, width=8)
    draw.line([F(0.5), F(0.14), F(0.5), F(0.72)], fill=OUTLINE, width=8)
    tail = [(F(0.5), F(0.72)), (F(0.44), F(0.80)), (F(0.54), F(0.86)), (F(0.46), F(0.92))]
    draw.line(tail, fill=OUTLINE, width=8, joint="curve")
    add_face(draw, F(0.5), F(0.40), scale=0.8)
    return canvas


def draw_crown(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    points = [
        (0.24, 0.62), (0.24, 0.36), (0.36, 0.50), (0.42, 0.28),
        (0.5, 0.44), (0.58, 0.28), (0.64, 0.50), (0.76, 0.36),
        (0.76, 0.62),
    ]
    draw.polygon([(F(x), F(y)) for x, y in points], fill=(250, 210, 60), outline=OUTLINE, width=14)
    draw.rectangle([F(0.24), F(0.62), F(0.76), F(0.72)], fill=(250, 210, 60), outline=OUTLINE, width=14)
    add_face(draw, F(0.5), F(0.56), scale=0.75)
    return canvas


def draw_sun(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    import math
    cx, cy, r_out, r_in = 0.5, 0.5, 0.42, 0.24
    points = []
    for i in range(16):
        angle = i * math.pi / 8
        r = r_out if i % 2 == 0 else r_in
        points.append((F(cx + r * math.cos(angle)), F(cy + r * math.sin(angle))))
    draw.polygon(points, fill=(255, 205, 40), outline=OUTLINE, width=14)
    draw.ellipse(circle_bbox(cx, cy, r_in * 0.9), fill=(255, 205, 40), outline=OUTLINE, width=10)
    add_face(draw, F(cx), F(cy))
    return canvas


def draw_umbrella(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    draw.pieslice([F(0.16), F(0.20), F(0.84), F(0.68)], 180, 360, fill=(230, 90, 130), outline=OUTLINE, width=14)
    draw.line([F(0.5), F(0.44), F(0.5), F(0.86)], fill=OUTLINE, width=16)
    draw.arc([F(0.5), F(0.80), F(0.62), F(0.92)], 90, 270, fill=OUTLINE, width=14)
    add_face(draw, F(0.5), F(0.42), scale=0.8)
    return canvas


def draw_violin(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    draw.ellipse(circle_bbox(0.42, 0.55, 0.16), fill=(150, 90, 40), outline=OUTLINE, width=12)
    draw.ellipse(circle_bbox(0.58, 0.72, 0.16), fill=(150, 90, 40), outline=OUTLINE, width=12)
    draw.rectangle([F(0.47), F(0.20), F(0.53), F(0.56)], fill=(90, 55, 25), outline=OUTLINE, width=12)
    draw.ellipse(circle_bbox(0.5, 0.18, 0.05), fill=(90, 55, 25), outline=OUTLINE, width=8)
    add_face(draw, F(0.5), F(0.63), scale=0.7)
    return canvas


def draw_xylophone(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    colors = [(230, 60, 50), (250, 160, 40), (250, 220, 60), (90, 190, 90), (80, 150, 230), (150, 90, 200)]
    n = len(colors)
    bar_w = 0.10
    gap = 0.015
    total_w = n * bar_w + (n - 1) * gap
    start_x = 0.5 - total_w / 2
    for i, color in enumerate(colors):
        x0 = start_x + i * (bar_w + gap)
        length = 0.55 - i * 0.03
        draw.rectangle([F(x0), F(0.30), F(x0 + bar_w), F(0.30 + length)], fill=color, outline=OUTLINE, width=10)
    add_face(draw, F(0.5), F(0.75), scale=0.7)
    return canvas


def draw_yoyo(bg):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg)
    draw = ImageDraw.Draw(canvas)
    draw.ellipse(circle_bbox(0.5, 0.42, 0.26), fill=(230, 60, 90), outline=OUTLINE, width=14)
    draw.ellipse(circle_bbox(0.5, 0.42, 0.07), fill=(150, 30, 50), outline=OUTLINE, width=8)
    draw.line([F(0.5), F(0.68), F(0.5), F(0.92)], fill=OUTLINE, width=8)
    add_face(draw, F(0.5), F(0.42), scale=0.85)
    return canvas


OBJECTS = {
    9: ("draw_hat", (200, 220, 250)),
    12: ("draw_kite", (255, 240, 180)),
    18: ("draw_crown", (200, 240, 200)),
    20: ("draw_sun", (250, 200, 130)),
    22: ("draw_umbrella", (190, 220, 250)),
    23: ("draw_violin", (200, 240, 210)),
    25: ("draw_xylophone", (255, 240, 180)),
    26: ("draw_yoyo", (190, 220, 250)),
}

FUNCS = {
    "draw_hat": draw_hat, "draw_kite": draw_kite, "draw_crown": draw_crown,
    "draw_sun": draw_sun, "draw_umbrella": draw_umbrella, "draw_violin": draw_violin,
    "draw_xylophone": draw_xylophone, "draw_yoyo": draw_yoyo,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    raw_dir = os.path.join(args.book_dir, "assets", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    for page, (func_name, bg) in OBJECTS.items():
        img = FUNCS[func_name](bg)
        out_path = os.path.join(raw_dir, f"page-{page}-object.png")
        img.save(out_path)
        print(f"Page {page} ({func_name}): rendered to {out_path}", flush=True)

    print(f"Done: {len(OBJECTS)} object(s) rendered", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
