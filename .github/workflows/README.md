# CI/CD — PDF Rendering & Image Generation Pipeline

This directory holds GitHub Actions workflows for this repo. Implemented so far:

- **`generate-book-images.yml`** — manually triggered (`workflow_dispatch`),
  takes a book path, runs `scripts/generate_images.py` to call free image
  generation APIs (Pollinations.ai primary, Hugging Face Inference API
  fallback), and opens a PR with the results in `assets/raw/` for human
  review. It never handles a Hugging Face token as a literal value — it only
  reads `secrets.HF_TOKEN`, which must be set under
  **Settings → Secrets and variables → Actions** in this repository. If a
  token was ever pasted in chat, a commit, an issue, or anywhere outside that
  secrets UI, revoke it at https://huggingface.co/settings/tokens and issue a
  new one — treat any exposed token as compromised immediately.

Not yet implemented (documented for future work):

## Intended pipeline stages

1. **Validate metadata** — lint every `books/*/*/metadata.json` against
   `templates/book_metadata_schema.json` (e.g. with `ajv-cli`). Fail fast on
   missing trim size, DPI, or page count fields.
2. **Validate manuscript structure** — check `manuscript.md` page breakdown
   matches `metadata.json.total_pages` (no missing/duplicate page numbers).
3. **Check asset completeness** — confirm every page referenced in
   `manuscript.md` has a corresponding final asset in `assets/final/` at the
   required resolution (300 DPI at 8.5x8.5in + 0.125in bleed = 2625x2625px).
3b. **Upscale for print** — free image APIs (Pollinations, HF free tier) cap
   out around 1024–1536px, below the ~2625px needed for 8.5x8.5in @ 300 DPI
   with bleed. Run a free upscaler (e.g. Real-ESRGAN) on approved images
   during the `assets/raw/` → `assets/final/` promotion step.
4. **Render layout** — combine `assets/final/*` with `templates/print-style.css`
   (or an InDesign/HTML-to-PDF renderer) into a single print-ready PDF per book.
5. **Preflight check** — verify CMYK color conversion, embedded fonts, bleed
   marks, and no RGB/spot-color leakage before the PDF is treated as
   print-ready.
6. **Publish artifact** — since this is a public repo intended for parents to
   freely download finished books, attach the rendered PDF to a **GitHub
   Release** (e.g. tag `high-contrast-shapes-v1`) rather than committing the
   binary into the tracked history — keeps clones fast and gives a stable
   public download URL.

## Suggested triggers

- On push/PR touching `books/<age-range>/<book>/**`, run stages 1-3 as a fast
  sanity check.
- On tag or manual dispatch, run the full pipeline (1-6) for release-ready PDFs.

## Suggested workflow file names (not yet created)

- `validate-metadata.yml`
- `render-book-pdf.yml`
