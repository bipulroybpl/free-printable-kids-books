#!/usr/bin/env python3
"""
Batch image generation for a single book, driven by prompts/image_prompts.json.

Primary generator: Pollinations.ai (free, no API key required).
Fallback generator: Hugging Face Inference API (requires HF_TOKEN env var,
set as a GitHub Actions secret -- never hardcode a token in this file).

Usage:
    python generate_images.py <path-to-book-dir>

Writes one PNG per prompt into <book-dir>/assets/raw/page-<N>.png
"""
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


def generate_via_pollinations(prompt: str) -> bytes:
    encoded = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_BASE}{encoded}?width={IMAGE_SIZE}&height={IMAGE_SIZE}&nologo=true"
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def generate_via_huggingface(prompt: str, token: str) -> bytes:
    req = urllib.request.Request(
        HF_API_URL,
        data=json.dumps({"inputs": prompt}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def generate_page(prompt: str, hf_token: str | None) -> bytes:
    try:
        return generate_via_pollinations(prompt)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print(f"  Pollinations failed ({exc}); falling back to Hugging Face...")
        if not hf_token:
            raise RuntimeError(
                "Pollinations failed and no HF_TOKEN provided for fallback"
            ) from exc
        return generate_via_huggingface(prompt, hf_token)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: generate_images.py <path-to-book-dir>", file=sys.stderr)
        return 1

    book_dir = sys.argv[1]
    prompts_path = os.path.join(book_dir, "prompts", "image_prompts.json")
    raw_dir = os.path.join(book_dir, "assets", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    with open(prompts_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    hf_token = os.environ.get("HF_TOKEN")  # sourced from secrets.HF_TOKEN in CI only

    for entry in data["prompts"]:
        page = entry["page"]
        prompt = entry["prompt"]
        out_path = os.path.join(raw_dir, f"page-{page}.png")

        if os.path.exists(out_path):
            print(f"Page {page}: already exists, skipping")
            continue

        print(f"Page {page}: generating...")
        try:
            image_bytes = generate_page(prompt, hf_token)
        except Exception as exc:
            print(f"Page {page}: FAILED -- {exc}", file=sys.stderr)
            continue

        with open(out_path, "wb") as f:
            f.write(image_bytes)
        print(f"Page {page}: saved to {out_path}")
        time.sleep(2)  # polite pacing against free-tier rate limits

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
