#!/usr/bin/env python3
"""
Generate step-by-step drawing pages entirely in code (no AI image
generation).

Rationale: AI generation for this book failed -- wildly inconsistent
styles across pages (photographic hand/pencil photos mixed with painterly
cartoon renders), no consistent child character, and one page rendered a
photorealistic cat instead of the required "simple basic shapes" activity-
book style. Rendered deterministically instead: each subject (cat, house,
rocket) is built from a fixed list of primitive parts added one step at a
time. Parts already drawn in a prior step render in plain black outline;
parts newly added on the current page render in a highlight color -- the
same "what's new" visual cue the manuscript originally asked for.

Usage:
    python generate_stepbystep_pages.py <path-to-book-dir>

Reads:
    <book-dir>/prompts/stepbystep_config.json
        {"items": [{"page": N, "subject": "cat", "through_step": 1}, ...]}
    through_step is the highest step index included cumulatively; every
    part from steps 1..through_step-1 renders black, parts belonging to
    through_step itself render in the highlight color. Pass "final": true
    instead of through_step to render every part in plain black (no new
    highlight) for the "you did it!" completed-drawing pages.

Writes:
    <book-dir>/assets/final/page-N.png
"""
import argparse
import json
import os

from PIL import Image, ImageDraw

CANVAS_SIZE = 2000
BLACK = (20, 20, 20)
HIGHLIGHT = (230, 90, 20)
STROKE = 16


def F(frac):
    return frac * CANVAS_SIZE


def circle_bbox(cx, cy, r):
    return [F(cx - r), F(cy - r), F(cx + r), F(cy + r)]


def draw_part(draw, kind, geom, color):
    if kind == "ellipse":
        draw.ellipse(geom, outline=color, width=STROKE)
    elif kind == "ellipse_fill":
        draw.ellipse(geom, fill=color)
    elif kind == "polygon":
        draw.polygon(geom, outline=color, width=STROKE)
    elif kind == "rectangle":
        draw.rectangle(geom, outline=color, width=STROKE)
    elif kind == "line":
        draw.line(geom, fill=color, width=round(STROKE * 0.7))
    else:
        raise ValueError(f"Unknown part kind: {kind}")


# Each subject is a list of steps; each step is a list of (kind, geom) parts.
SUBJECTS = {
    "cat": [
        [("ellipse", circle_bbox(0.5, 0.55, 0.28))],  # step 1: head
        [  # step 2: ears
            ("polygon", [F(0.30), F(0.32), F(0.38), F(0.14), F(0.46), F(0.30)]),
            ("polygon", [F(0.54), F(0.30), F(0.62), F(0.14), F(0.70), F(0.32)]),
        ],
        [  # step 3: eyes
            ("ellipse_fill", circle_bbox(0.40, 0.50, 0.035)),
            ("ellipse_fill", circle_bbox(0.60, 0.50, 0.035)),
        ],
        [  # step 4: whiskers
            ("line", [F(0.30), F(0.60), F(0.44), F(0.62)]),
            ("line", [F(0.30), F(0.68), F(0.44), F(0.68)]),
            ("line", [F(0.56), F(0.62), F(0.70), F(0.60)]),
            ("line", [F(0.56), F(0.68), F(0.70), F(0.68)]),
        ],
    ],
    "house": [
        [("rectangle", [F(0.28), F(0.46), F(0.72), F(0.86)])],  # step 1: base
        [("polygon", [F(0.22), F(0.46), F(0.5), F(0.18), F(0.78), F(0.46)])],  # step 2: roof
        [("rectangle", [F(0.45), F(0.62), F(0.55), F(0.86)])],  # step 3: door
        [("rectangle", [F(0.34), F(0.54), F(0.42), F(0.62)])],  # step 4: window
    ],
    "rocket": [
        [("polygon", [F(0.42), F(0.42), F(0.5), F(0.16), F(0.58), F(0.42)])],  # step 1: nose
        [("rectangle", [F(0.40), F(0.42), F(0.60), F(0.74)])],  # step 2: body
        [  # step 3: fins
            ("polygon", [F(0.40), F(0.62), F(0.28), F(0.80), F(0.40), F(0.74)]),
            ("polygon", [F(0.60), F(0.62), F(0.72), F(0.80), F(0.60), F(0.74)]),
        ],
        [  # step 4: flames + stars
            ("polygon", [F(0.42), F(0.74), F(0.5), F(0.94), F(0.58), F(0.74)]),
            ("line", [F(0.20), F(0.30), F(0.24), F(0.24), F(0.28), F(0.30), F(0.24), F(0.34), F(0.20), F(0.30)]),
            ("line", [F(0.76), F(0.40), F(0.80), F(0.34), F(0.84), F(0.40), F(0.80), F(0.44), F(0.76), F(0.40)]),
        ],
    ],
}


def render_page(subject, through_step, final):
    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    steps = SUBJECTS[subject]
    last_step = through_step if not final else len(steps)

    for i in range(last_step):
        color = BLACK if (final or i < last_step - 1) else HIGHLIGHT
        for kind, geom in steps[i]:
            draw_part(draw, kind, geom, color)

    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    args = parser.parse_args()

    book_dir = args.book_dir
    final_dir = os.path.join(book_dir, "assets", "final")
    os.makedirs(final_dir, exist_ok=True)

    with open(os.path.join(book_dir, "prompts", "stepbystep_config.json"), encoding="utf-8") as f:
        config = json.load(f)

    for item in config["items"]:
        page = item["page"]
        subject = item["subject"]
        final = item.get("final", False)
        through_step = item.get("through_step", len(SUBJECTS[subject]))
        page_img = render_page(subject, through_step, final)
        out_path = os.path.join(final_dir, f"page-{page}.png")
        page_img.save(out_path)
        print(f"Page {page} ({subject}, through_step={through_step}, final={final}): rendered to {out_path}", flush=True)

    print(f"Done: {len(config['items'])} page(s) rendered", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
