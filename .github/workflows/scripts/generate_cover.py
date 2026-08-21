#!/usr/bin/env python3
"""
Generate a designed front-cover image (assets/final/page-1.png) for a book,
entirely in code (Pillow) -- no AI image generation, so it's free, fast,
and immune to the character/style-consistency failures seen with AI-
generated covers on other books in this repo.

Design: solid background in the book's assigned palette, a colored border
frame, four corner accent circles, the book title centered in a white
rounded card for legibility, and a small age-range badge.

Usage:
    python generate_cover.py <path-to-book-dir>

Reads:
    <book-dir>/metadata.json
    shared_assets/color_palettes/palettes.json

Writes:
    <book-dir>/assets/final/page-1.png
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

DPI = 300


def load_font(size, bold=True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def find_repo_root(start):
    path = os.path.abspath(start)
    while path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, "shared_assets", "color_palettes", "palettes.json")):
            return path
        path = os.path.dirname(path)
    raise FileNotFoundError("Could not locate repo root (shared_assets/color_palettes/palettes.json)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    book_dir = args.book_dir
    with open(os.path.join(book_dir, "metadata.json"), encoding="utf-8") as f:
        meta = json.load(f)

    repo_root = find_repo_root(book_dir)
    with open(os.path.join(repo_root, "shared_assets", "color_palettes", "palettes.json"), encoding="utf-8") as f:
        palettes = json.load(f)["palettes"]

    palette = palettes[meta["color_palette"]]
    colors = [hex_to_rgb(c["hex"]) for c in palette["colors"]]
    bg = colors[0]
    accent = colors[1] if len(colors) > 1 else colors[0]
    accent2 = colors[2] if len(colors) > 2 else accent
    accent3 = colors[3] if len(colors) > 3 else accent2

    trim_w = meta["trim_size"]["width_in"]
    trim_h = meta["trim_size"]["height_in"]
    bleed = meta["print_spec"]["bleed_in"]
    dpi = meta["print_spec"].get("dpi", DPI)
    page_w = round((trim_w + 2 * bleed) * dpi)
    page_h = round((trim_h + 2 * bleed) * dpi)

    canvas = Image.new("RGB", (page_w, page_h), bg)
    draw = ImageDraw.Draw(canvas)

    border_inset = round(0.35 * dpi)
    border_width = round(0.05 * dpi)
    draw.rectangle(
        [border_inset, border_inset, page_w - border_inset, page_h - border_inset],
        outline=accent, width=border_width,
    )

    corner_r = round(0.45 * dpi)
    for cx, cy in [
        (border_inset, border_inset), (page_w - border_inset, border_inset),
        (border_inset, page_h - border_inset), (page_w - border_inset, page_h - border_inset),
    ]:
        draw.ellipse([cx - corner_r, cy - corner_r, cx + corner_r, cy + corner_r], fill=accent2)

    # a few small decorative dots along the top and bottom border for visual rhythm
    dot_r = round(0.12 * dpi)
    dot_y_top = border_inset
    dot_y_bottom = page_h - border_inset
    for i in range(1, 5):
        dx = border_inset + (page_w - 2 * border_inset) * i / 5
        draw.ellipse([dx - dot_r, dot_y_top - dot_r, dx + dot_r, dot_y_top + dot_r], fill=accent3)
        draw.ellipse([dx - dot_r, dot_y_bottom - dot_r, dx + dot_r, dot_y_bottom + dot_r], fill=accent3)

    title = meta["title"]
    card_w = round(page_w * 0.72)
    font_size = round(dpi * 0.62)
    font = load_font(font_size)
    max_text_width = card_w - round(0.5 * dpi)
    lines = wrap_text(draw, title, font, max_text_width)
    while len(lines) > 3 and font_size > round(dpi * 0.3):
        font_size -= round(dpi * 0.04)
        font = load_font(font_size)
        lines = wrap_text(draw, title, font, max_text_width)

    line_height = font_size + round(0.12 * dpi)
    card_h = line_height * len(lines) + round(0.6 * dpi)
    card_x0 = (page_w - card_w) / 2
    card_y0 = (page_h - card_h) / 2 - round(0.3 * dpi)
    card_x1 = card_x0 + card_w
    card_y1 = card_y0 + card_h

    draw.rounded_rectangle(
        [card_x0, card_y0, card_x1, card_y1], radius=round(0.25 * dpi),
        fill=(255, 255, 255, 245), outline=accent, width=round(0.03 * dpi),
    )

    y = card_y0 + round(0.3 * dpi)
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((page_w - w) / 2, y), line, font=font, fill=(30, 30, 30))
        y += line_height

    age_text = f"Ages {meta['age_range']}"
    age_font = load_font(round(dpi * 0.22))
    age_w = draw.textlength(age_text, font=age_font)
    badge_r_x = age_w / 2 + round(0.25 * dpi)
    badge_r_y = round(0.35 * dpi)
    badge_cx = page_w / 2
    badge_cy = card_y1 + round(0.55 * dpi)
    # fixed dark badge regardless of palette -- some palettes (e.g.
    # high-contrast) have "accent" resolve to white, which would make white
    # badge text invisible against it
    draw.rounded_rectangle(
        [badge_cx - badge_r_x, badge_cy - badge_r_y, badge_cx + badge_r_x, badge_cy + badge_r_y],
        radius=badge_r_y, fill=(40, 40, 40),
    )
    draw.text((badge_cx - age_w / 2, badge_cy - round(0.16 * dpi)), age_text, font=age_font, fill=(255, 255, 255))

    out_path = os.path.join(book_dir, "assets", "final", "page-1.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)
    print(f"Cover saved to {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
