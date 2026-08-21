#!/usr/bin/env python3
"""
Compose a book's split-panel pages from separately-generated letter/object
images (assets/raw/page-N-letter.png + page-N-object.png) into a single
page-N.png written to assets/final/.

Run this AFTER a human has reviewed the individual letter/object images in
assets/raw/ -- it does not itself judge content safety, it only lays out
images that have already been approved.

Usage:
    python compose_split_panel.py <path-to-book-dir>

Reads:
    <book-dir>/prompts/image_prompts.json  (for the badge letter/number per page)
    <book-dir>/assets/raw/page-N-letter.png
    <book-dir>/assets/raw/page-N-object.png

Writes:
    <book-dir>/assets/final/page-N.png
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS_SIZE = 2000  # square output; final PDF render step crops/scales to page


def load_font(size):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def cover_fit(img, w, h):
    scale = max(w / img.width, h / img.height)
    new_size = (round(img.width * scale), round(img.height * scale))
    img = img.resize(new_size, Image.LANCZOS)
    left = (img.width - w) // 2
    top = (img.height - h) // 2
    return img.crop((left, top, left + w, top + h))


def compose_page(letter_path, object_path, badge_text):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255))
    half_w = CANVAS_SIZE // 2

    left = cover_fit(Image.open(letter_path).convert("RGB"), half_w, CANVAS_SIZE)
    canvas.paste(left, (0, 0))

    right = cover_fit(Image.open(object_path).convert("RGB"), CANVAS_SIZE - half_w, CANVAS_SIZE)
    canvas.paste(right, (half_w, 0))

    draw = ImageDraw.Draw(canvas)
    divider_w = 6
    draw.rectangle(
        [(half_w - divider_w // 2, 0), (half_w + divider_w // 2, CANVAS_SIZE)],
        fill=(255, 255, 255),
    )

    if badge_text:
        badge_r = 70
        badge_center = (CANVAS_SIZE - badge_r - 30, badge_r + 30)
        draw.ellipse(
            [
                (badge_center[0] - badge_r, badge_center[1] - badge_r),
                (badge_center[0] + badge_r, badge_center[1] + badge_r),
            ],
            fill=(255, 255, 255),
            outline=(40, 40, 40),
            width=4,
        )
        font = load_font(round(badge_r * 1.1))
        w = draw.textlength(badge_text, font=font)
        draw.text(
            (badge_center[0] - w / 2, badge_center[1] - badge_r * 0.65),
            badge_text,
            font=font,
            fill=(40, 40, 40),
        )

    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    book_dir = args.book_dir
    raw_dir = os.path.join(book_dir, "assets", "raw")
    final_dir = os.path.join(book_dir, "assets", "final")
    os.makedirs(final_dir, exist_ok=True)

    with open(os.path.join(book_dir, "prompts", "image_prompts.json"), encoding="utf-8") as f:
        data = json.load(f)

    composed = 0
    for entry in data["prompts"]:
        if "letter_prompt" not in entry:
            continue  # single-image page, nothing to compose
        page = entry["page"]
        letter_path = os.path.join(raw_dir, f"page-{page}-letter.png")
        object_path = os.path.join(raw_dir, f"page-{page}-object.png")
        if not (os.path.exists(letter_path) and os.path.exists(object_path)):
            print(f"Page {page}: missing letter/object source image(s), skipping", flush=True)
            continue

        badge_text = str(entry.get("letter", entry.get("number", "")))
        page_img = compose_page(letter_path, object_path, badge_text)
        out_path = os.path.join(final_dir, f"page-{page}.png")
        page_img.save(out_path)
        print(f"Page {page}: composed to {out_path}", flush=True)
        composed += 1

    print(f"Composed {composed} page(s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
