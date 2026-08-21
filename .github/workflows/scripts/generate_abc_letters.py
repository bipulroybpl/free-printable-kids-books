#!/usr/bin/env python3
"""
Generate the "letter" half of each Baby's First ABC page entirely in code
(no AI image generation). The "object" half (apple, ball, cat, ...) stays
AI-generated -- that side worked fine; the letter side is what failed.

Rationale: AI generation for the letter side failed consistently -- both
an 'A' and a 'K' request rendered as a generic glossy ring/donut shape
regardless of which letter was actually requested. AI image generation
cannot reliably draw a specific dimensional letterform, so it's rendered
deterministically instead: a big bold colored letter with a simple googly-
eyes-and-smile face, matching the "cute mascot" look the book wants.

Usage:
    python generate_abc_letters.py <path-to-book-dir>

Reads:
    <book-dir>/prompts/image_prompts.json  (uses each entry's "letter" field)

Writes:
    <book-dir>/assets/raw/page-N-letter.png
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = 2000
BG = (235, 235, 235)
OUTLINE = (30, 30, 30)
WHITE = (255, 255, 255)

LETTER_COLORS = [
    (227, 6, 19), (0, 114, 188), (255, 242, 0), (0, 166, 81),
    (146, 39, 143), (247, 148, 29), (236, 0, 140), (0, 169, 157),
]


def load_font(size):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_letter(letter, color):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), BG)
    draw = ImageDraw.Draw(canvas)

    font = load_font(round(CANVAS_SIZE * 0.62))
    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (CANVAS_SIZE - w) / 2 - bbox[0]
    y = (CANVAS_SIZE - h) / 2 - bbox[1]

    # thick dark outline via offset copies, then the solid color letter on top
    offset = round(CANVAS_SIZE * 0.012)
    for dx in (-offset, 0, offset):
        for dy in (-offset, 0, offset):
            draw.text((x + dx, y + dy), letter, font=font, fill=OUTLINE)
    draw.text((x, y), letter, font=font, fill=color)

    # googly eyes + smile, positioned relative to the glyph's bounding box
    glyph_top = y + bbox[1]
    glyph_cx = CANVAS_SIZE / 2
    eye_y = glyph_top + h * 0.32
    eye_spacing = max(w * 0.16, CANVAS_SIZE * 0.09)
    eye_r = CANVAS_SIZE * 0.052
    pupil_r = eye_r * 0.45

    for ex in (glyph_cx - eye_spacing, glyph_cx + eye_spacing):
        draw.ellipse([ex - eye_r, eye_y - eye_r, ex + eye_r, eye_y + eye_r], fill=WHITE, outline=OUTLINE, width=8)
        draw.ellipse([ex - pupil_r, eye_y - pupil_r, ex + pupil_r, eye_y + pupil_r], fill=OUTLINE)

    smile_y = eye_y + eye_r * 1.6
    smile_w = eye_spacing * 1.3
    draw.arc(
        [glyph_cx - smile_w, smile_y - smile_w * 0.5, glyph_cx + smile_w, smile_y + smile_w * 0.5],
        20, 160, fill=OUTLINE, width=14,
    )

    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    book_dir = args.book_dir
    raw_dir = os.path.join(book_dir, "assets", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    with open(os.path.join(book_dir, "prompts", "image_prompts.json"), encoding="utf-8") as f:
        data = json.load(f)

    for i, entry in enumerate(data["prompts"]):
        page = entry["page"]
        letter = entry["letter"]
        color = LETTER_COLORS[i % len(LETTER_COLORS)]
        img = render_letter(letter, color)
        out_path = os.path.join(raw_dir, f"page-{page}-letter.png")
        img.save(out_path)
        print(f"Page {page} ({letter}): rendered to {out_path}", flush=True)

    print(f"Done: {len(data['prompts'])} letter(s) rendered", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
