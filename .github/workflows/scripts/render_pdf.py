#!/usr/bin/env python3
"""
Render a single book's assets/final/*.png images + manuscript.md text into
one print-ready PDF, using the trim/bleed/DPI spec from metadata.json.

This is a from-scratch compositor (Pillow only, no browser/HTML engine),
so it does not literally parse templates/print-style.css -- it reimplements
the same trim/bleed/safe-area measurements in Python. Keep the two in sync
if the print spec changes.

Usage:
    python render_pdf.py <path-to-book-dir> [--out <output.pdf>]

Reads:
    <book-dir>/metadata.json
    <book-dir>/manuscript.md          (page -> text content)
    <book-dir>/assets/final/page-N.png (interior page art; cover/back pages
                                         with no matching file get a plain
                                         color background instead)

Writes:
    <book-dir>/<book_id>.pdf (default), or the path given by --out
"""
import argparse
import json
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

DPI = 300


def load_metadata(book_dir):
    with open(os.path.join(book_dir, "metadata.json"), encoding="utf-8") as f:
        return json.load(f)


def parse_manuscript(book_dir):
    """Returns {page_number: text_content} parsed from the manuscript.md table."""
    path = os.path.join(book_dir, "manuscript.md")
    pages = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 2:
                continue
            page_match = re.match(r"^(\d+)", cells[0])
            if not page_match:
                continue  # header row, separator row, etc.
            page_num = int(page_match.group(1))
            text = cells[1].strip().strip('"')
            pages[page_num] = text
    return pages


def load_font(size):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


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


def render_page(page_w, page_h, image_path, text, font, bleed_px, safe_px, bg_color):
    canvas = Image.new("RGB", (page_w, page_h), bg_color)

    if image_path and os.path.exists(image_path):
        art = Image.open(image_path).convert("RGB")
        # Fit-to-width and pad top/bottom rather than cover-fit-and-crop --
        # cover-fit was cropping ~28% off the left/right edges of every
        # square (1:1) final-art page to fill the taller portrait trim size,
        # clipping letters/objects positioned near the panel edges.
        scale = page_w / art.width
        new_size = (page_w, round(art.height * scale))
        art = art.resize(new_size, Image.LANCZOS)
        if new_size[1] >= page_h:
            top = (new_size[1] - page_h) // 2
            art = art.crop((0, top, page_w, top + page_h))
            canvas.paste(art, (0, 0))
        else:
            top = (page_h - new_size[1]) // 2
            canvas.paste(art, (0, top))

    if text:
        draw = ImageDraw.Draw(canvas, "RGBA")
        max_text_width = page_w - 2 * (bleed_px + safe_px)
        lines = wrap_text(draw, text, font, max_text_width)
        line_height = font.size + 10
        band_height = line_height * len(lines) + 40
        band_top = page_h - bleed_px - safe_px - band_height
        draw.rectangle(
            [(bleed_px, band_top), (page_w - bleed_px, page_h - bleed_px - safe_px // 2)],
            fill=(255, 255, 255, 235),
        )
        y = band_top + 20
        for line in lines:
            w = draw.textlength(line, font=font)
            draw.text(((page_w - w) / 2, y), line, font=font, fill=(20, 20, 20, 255))
            y += line_height
    else:
        draw = ImageDraw.Draw(canvas)

    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    book_dir = args.book_dir
    metadata = load_metadata(book_dir)
    manuscript_pages = parse_manuscript(book_dir)

    trim_w_in = metadata["trim_size"]["width_in"]
    trim_h_in = metadata["trim_size"]["height_in"]
    bleed_in = metadata["print_spec"]["bleed_in"]
    dpi = metadata["print_spec"].get("dpi", DPI)

    page_w = round((trim_w_in + 2 * bleed_in) * dpi)
    page_h = round((trim_h_in + 2 * bleed_in) * dpi)
    bleed_px = round(bleed_in * dpi)
    safe_px = round(0.25 * dpi)

    min_pt = metadata["font_spec"].get("min_point_size", 24)
    font_px = round(min_pt * dpi / 72)
    font = load_font(font_px)

    total_pages = metadata["total_pages"]
    final_dir = os.path.join(book_dir, "assets", "final")

    rendered = []
    for page_num in range(1, total_pages + 1):
        image_path = os.path.join(final_dir, f"page-{page_num}.png")
        # page 1 is a code-generated cover (see generate_cover.py) with the
        # title already baked into the art -- skip the text banner there so
        # it doesn't draw the title a second time on top
        text = "" if (page_num == 1 and os.path.exists(image_path)) else manuscript_pages.get(page_num, "")
        bg_color = (255, 246, 230)  # warm off-white for cover/back/missing pages
        page_img = render_page(page_w, page_h, image_path, text, font, bleed_px, safe_px, bg_color)
        rendered.append(page_img)
        print(f"Rendered page {page_num}/{total_pages}"
              f"{' (no art, text-only)' if not os.path.exists(image_path) else ''}", flush=True)

    out_path = args.out or os.path.join(book_dir, f"{metadata['book_id']}.pdf")
    rendered[0].save(
        out_path, "PDF", save_all=True, append_images=rendered[1:], resolution=dpi
    )
    print(f"Wrote {out_path} ({len(rendered)} pages)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
