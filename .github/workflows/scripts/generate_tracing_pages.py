#!/usr/bin/env python3
"""
Generate tracing-practice pages entirely in code (no AI image generation).

Rationale: dotted/outline letterform tracing guides need pixel-precise
typography and geometry, which free AI image APIs cannot reliably produce
(same lesson learned from the ABC book's failed AI-composited split panels,
but worse -- organic illustration tolerates AI fuzziness, precise tracing
guides do not). A real font + PIL primitives is both more reliable and free.

Usage:
    python generate_tracing_pages.py <path-to-book-dir>

Reads:
    <book-dir>/prompts/tracing_config.json

Writes:
    <book-dir>/assets/final/page-N.png  (written directly -- no human visual
    review step needed since there's no AI content-safety risk here, just a
    deterministic render)
"""
import argparse
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = 2000
TRACE_GRAY = (190, 190, 190)
REFERENCE_BLACK = (30, 30, 30)


def load_font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_letter_page(content, label, bg_color):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg_color)
    draw = ImageDraw.Draw(canvas)

    big_font = load_font(round(CANVAS_SIZE * 0.65))
    bbox = draw.textbbox((0, 0), content, font=big_font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (CANVAS_SIZE - w) / 2 - bbox[0]
    y = (CANVAS_SIZE - h) / 2 - bbox[1]
    draw.text((x, y), content, font=big_font, fill=TRACE_GRAY)

    # small solid reference badge, top-left
    badge_font = load_font(round(CANVAS_SIZE * 0.12))
    draw.ellipse([(60, 60), (60 + 220, 60 + 220)], fill=(255, 255, 255), outline=REFERENCE_BLACK, width=6)
    rb = draw.textbbox((0, 0), label, font=badge_font)
    rw, rh = rb[2] - rb[0], rb[3] - rb[1]
    draw.text((60 + 110 - rw / 2 - rb[0], 60 + 110 - rh / 2 - rb[1]), label, font=badge_font, fill=REFERENCE_BLACK)

    return canvas


def render_shape_page(shape, bg_color):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), bg_color)
    draw = ImageDraw.Draw(canvas)
    c = CANVAS_SIZE // 2
    r = round(CANVAS_SIZE * 0.32)
    width = 22

    if shape == "vertical_line":
        draw.line([(c, c - r), (c, c + r)], fill=TRACE_GRAY, width=width)
    elif shape == "horizontal_line":
        draw.line([(c - r, c), (c + r, c)], fill=TRACE_GRAY, width=width)
    elif shape == "circle":
        draw.ellipse([(c - r, c - r), (c + r, c + r)], outline=TRACE_GRAY, width=width)
    elif shape == "cross":
        draw.line([(c, c - r), (c, c + r)], fill=TRACE_GRAY, width=width)
        draw.line([(c - r, c), (c + r, c)], fill=TRACE_GRAY, width=width)
    elif shape == "diagonal_line":
        draw.line([(c - r, c - r), (c + r, c + r)], fill=TRACE_GRAY, width=width)
    elif shape == "curve_wave":
        points = []
        for i in range(0, 201):
            t = i / 200
            px = c - r + t * 2 * r
            py = c + r * 0.5 * math.sin(t * 2 * math.pi)
            points.append((px, py))
        draw.line(points, fill=TRACE_GRAY, width=width, joint="curve")
    elif shape == "zigzag":
        points = [
            (c - r, c - r * 0.5), (c - r * 0.33, c + r * 0.5),
            (c + r * 0.33, c - r * 0.5), (c + r, c + r * 0.5),
        ]
        draw.line(points, fill=TRACE_GRAY, width=width, joint="curve")
    elif shape == "square":
        draw.rectangle([(c - r, c - r), (c + r, c + r)], outline=TRACE_GRAY, width=width)
    else:
        raise ValueError(f"Unknown shape: {shape}")

    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    book_dir = args.book_dir
    final_dir = os.path.join(book_dir, "assets", "final")
    os.makedirs(final_dir, exist_ok=True)

    with open(os.path.join(book_dir, "prompts", "tracing_config.json"), encoding="utf-8") as f:
        config = json.load(f)

    bg_color = tuple(config.get("background_rgb", [255, 250, 240]))

    for item in config["items"]:
        page = item["page"]
        if config["type"] in ("letter", "number"):
            page_img = render_letter_page(item["content"], item.get("label", item["content"]), bg_color)
        elif config["type"] == "shape":
            page_img = render_shape_page(item["shape"], bg_color)
        else:
            raise ValueError(f"Unknown config type: {config['type']}")

        out_path = os.path.join(final_dir, f"page-{page}.png")
        page_img.save(out_path)
        print(f"Page {page}: rendered to {out_path}", flush=True)

    print(f"Done: {len(config['items'])} page(s) rendered", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
