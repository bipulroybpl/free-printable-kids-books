#!/usr/bin/env python3
"""
Batch image generation for a single book, driven by prompts/image_prompts.json.

Two generators are supported, either can be primary (the other becomes the
fallback if the primary fails):
- pollinations: Pollinations.ai, free, no API key required.
- huggingface: Hugging Face Inference API (FLUX.1-schnell), requires HF_TOKEN
  env var, set as a GitHub Actions secret -- never hardcode a token in this
  file.

Usage:
    python generate_images.py <path-to-book-dir> [--primary pollinations|huggingface]

Each entry in prompts/image_prompts.json is either:
  - {"page": N, "prompt": "..."} -> writes assets/raw/page-N.png
  - {"page": N, "letter_prompt": "...", "object_prompt": "..."} -> writes
    assets/raw/page-N-letter.png and assets/raw/page-N-object.png separately
    (used when a page's full layout is composited from two simpler images
    rather than generated as one complex composition -- see
    scripts/compose_split_panel.py)
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"
HF_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
IMAGE_SIZE = 1024  # free-tier ceiling; upscale separately for print DPI
USER_AGENT = "free-printable-kids-books-image-gen/1.0 (+https://github.com/bipulroybpl/free-printable-kids-books)"
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 5


def _fetch_with_retries(build_request, attempts: int = MAX_ATTEMPTS) -> bytes:
    last_exc = None
    for attempt in range(1, attempts + 1):
        try:
            req = build_request()
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_exc = exc
            if attempt < attempts:
                print(f"    attempt {attempt}/{attempts} failed ({exc}), retrying in {RETRY_DELAY_SECONDS}s...", flush=True)
                time.sleep(RETRY_DELAY_SECONDS)
    raise last_exc


def generate_via_pollinations(prompt: str) -> bytes:
    encoded = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_BASE}{encoded}?width={IMAGE_SIZE}&height={IMAGE_SIZE}&nologo=true"

    def build_request():
        return urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    return _fetch_with_retries(build_request)


def generate_via_huggingface(prompt: str, token: str) -> bytes:
    def build_request():
        return urllib.request.Request(
            HF_API_URL,
            data=json.dumps({"inputs": prompt}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )

    return _fetch_with_retries(build_request)


def generate_page(prompt: str, hf_token: str | None, primary: str) -> bytes:
    generators = {
        "pollinations": ("Pollinations", lambda: generate_via_pollinations(prompt)),
        "huggingface": ("Hugging Face", lambda: generate_via_huggingface(prompt, hf_token)),
    }
    order = [primary] + [g for g in generators if g != primary]

    last_exc = None
    for i, name in enumerate(order):
        label, call = generators[name]
        if name == "huggingface" and not hf_token:
            print(f"  Skipping {label}: no HF_TOKEN set", flush=True)
            continue
        try:
            return call()
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_exc = exc
            remaining = order[i + 1:]
            if remaining:
                print(f"  {label} failed ({exc}); falling back to {generators[remaining[0]][0]}...", flush=True)
    raise last_exc or RuntimeError("No generator available (check HF_TOKEN)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("book_dir")
    parser.add_argument("--primary", choices=["pollinations", "huggingface"], default="pollinations")
    args = parser.parse_args()

    book_dir = args.book_dir
    prompts_path = os.path.join(book_dir, "prompts", "image_prompts.json")
    raw_dir = os.path.join(book_dir, "assets", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hf_token = os.environ.get("HF_TOKEN")  # sourced from secrets.HF_TOKEN in CI only

    print(f"Primary generator: {args.primary}", flush=True)

    jobs = []  # list of (label, prompt, out_path)
    for entry in data["prompts"]:
        page = entry["page"]
        if "prompt" in entry:
            jobs.append((f"page {page}", entry["prompt"], os.path.join(raw_dir, f"page-{page}.png")))
        else:
            jobs.append((f"page {page} letter", entry["letter_prompt"], os.path.join(raw_dir, f"page-{page}-letter.png")))
            jobs.append((f"page {page} object", entry["object_prompt"], os.path.join(raw_dir, f"page-{page}-object.png")))

    for label, prompt, out_path in jobs:
        if os.path.exists(out_path):
            print(f"{label}: already exists, skipping")
            continue

        print(f"{label}: generating...", flush=True)
        try:
            image_bytes = generate_page(prompt, hf_token, args.primary)
        except Exception as exc:
            print(f"{label}: FAILED -- {exc}", file=sys.stderr, flush=True)
            continue

        with open(out_path, "wb") as f:
            f.write(image_bytes)
        print(f"{label}: saved to {out_path}", flush=True)
        time.sleep(2)  # polite pacing against free-tier rate limits

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
