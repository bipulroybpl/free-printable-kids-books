# Free Printable Kids Books (Ages 0-5)

**Free printable children's books for babies, toddlers, and preschoolers —
high-contrast baby books, feelings & emotions books for toddlers, and
step-by-step drawing books for kids.** Every book is print-ready (300 DPI,
8.5x8.5in) and free to download as a PDF — no sign-up required.

📦 Repo: [github.com/bipulroybpl/free-printable-kids-books](https://github.com/bipulroybpl/free-printable-kids-books)

## Download free kids books by age

| Age | Book | What it teaches | Status |
|---|---|---|---|
| 0-1 (babies) | [High-Contrast Shapes](books/age-0-1/high-contrast-shapes/) | Visual contrast tracking — a free **high contrast baby book** for newborn visual stimulation | In progress |
| 2-3 (toddlers) | [Character Feelings](books/age-2-3/character-feelings/) | Emotional vocabulary — a free **feelings book for toddlers** / emotions book for kids | In progress |
| 2-3 (toddlers) | [Baby's First Learning ABC](books/age-2-3/baby-first-abc/) | Letter-shape recognition & vocabulary — a free **alphabet book for toddlers** / ABC book for kids | In progress |
| 2-3 (toddlers) | [Baby's First Learning 123](books/age-2-3/baby-first-123/) | Number recognition & one-to-one counting (1-10) — a free **counting book for toddlers** / 123 book for kids | In progress |
| 4-5 (preschoolers) | [Step-by-Step Drawing](books/age-4-5/step-by-step-drawing/) | Fine-motor sequencing — a free **kids drawing book**, learn to draw step by step | In progress |

> Finished, print-ready PDFs are published under [Releases](https://github.com/bipulroybpl/free-printable-kids-books/releases) as each title is completed. Source manuscripts, prompts, and print specs for every book live in this repo.

## Why this repo exists

Most "free printable" children's books online are scattered single PDFs with
no consistency in print quality, sizing, or age-appropriateness. This project
is a **children's book design system**: a shared print spec, font guidance,
and color palette so every free printable kids book here — whether it's a
baby book, a toddler feelings book, or a kids drawing book — is print-ready
at professional quality and safe for its intended age.

## Repository layout

```
.github/workflows/       CI/CD: automated image generation + PDF rendering pipeline docs
templates/                Shared schema + print stylesheet (8.5x8.5in, 300 DPI, 0.125in bleed)
shared_assets/
  fonts/                   Recommended open-source kids fonts (Fredoka, Nunito, Comic Neue)
  color_palettes/          Shared HEX/CMYK palette definitions
books/
  age-0-1/
    high-contrast-shapes/  Free high-contrast baby book (newborn visual stimulation)
  age-2-3/
    character-feelings/    Free toddler feelings & emotions book
  age-4-5/
    step-by-step-drawing/  Free kids drawing book (step-by-step, ages 4-5)
```

Each book folder contains:
- `metadata.json` — title, age range, trim size, font spec, page count, palette.
- `manuscript.md` — page-by-page breakdown (text, visual description, layout type).
- `prompts/image_prompts.json` — structured AI image prompts per page.
- `assets/raw/` — unedited AI-generated draft images.
- `assets/final/` — approved, print-ready final images (300 DPI, CMYK).

## Developmental philosophy (Ages 0-5)

Each age band targets a specific developmental milestone, not just a vague
"younger/older" split:

- **Ages 0-1 — high-contrast baby book (`high-contrast-shapes`)**: Infant
  vision responds most strongly to sharp black/white/red contrast before
  color perception and object recognition mature. This free baby book avoids
  text entirely and relies on bold, single-shape-per-page visual stimulation.
  No small or choking-hazard-shaped isolated details.
- **Ages 2-3 — toddler feelings book (`character-feelings`)**: Toddlers are
  building an emotional vocabulary and beginning to self-regulate. This free
  emotions book for kids uses one unambiguous emotion per spread, a
  consistent character design, and always pairs a "difficult" emotion (sad,
  angry, scared) with a coping/resolution page — the character is never left
  in unresolved distress.
- **Ages 4-5 — kids drawing book (`step-by-step-drawing`)**: Preschoolers can
  follow short multi-step sequences and are refining fine-motor/pencil-grip
  skills. This free drawing book for kids breaks each drawing into at most
  6 numbered steps using only basic shapes, with a consistent step-highlight
  color so a child (or reading adult) can visually track what's new at each
  step.

### Content safety checklist (applied to every book before release)

- [ ] 0-1: no small/choking-hazard-shaped details; no thin single-stroke line art; no text on baby-facing pages.
- [ ] 2-3: one clear emotion per spread; no blended/ambiguous expressions; every difficult emotion resolves within 1-2 pages.
- [ ] 4-5: no depiction of scissors/blades/unsupervised tool use; max 6 steps per drawing; encouraging, non-competitive tone.
- [ ] All ages: consistent character model sheet across a title; body text at or above the `min_point_size` in `metadata.json`.

## Asset pipeline workflow

```
manuscript.md  →  prompts/image_prompts.json  →  free AI image generation  →  assets/raw/
                                                                              │
                                                                              ▼
                                                            human review + edit/upscale
                                                                              │
                                                                              ▼
                                                                      assets/final/
                                                                              │
                                                                              ▼
                                                    layout render (templates/print-style.css)
                                                                              │
                                                                              ▼
                                                    print-ready PDF → published as a GitHub Release
```

1. **Manuscript** (`manuscript.md`) defines the page-by-page text, visual
   description, and layout type for a book.
2. **Image prompts** (`prompts/image_prompts.json`) translate each page's
   visual description into a structured AI prompt, using the book's assigned
   color palette (`shared_assets/color_palettes/palettes.json`), consistent
   style modifiers, and `--ar 1:1` aspect ratio (matching the 8.5x8.5in
   square trim).
3. **Image generation** uses free APIs (Pollinations.ai, Hugging Face
   Inference API) via `.github/workflows/generate-book-images.yml` to produce
   draft images into `assets/raw/`.
4. **Review & finalize**: approved/edited/upscaled images move to
   `assets/final/` at full print resolution.
5. **Layout rendering** combines `assets/final/*` with
   `templates/print-style.css` (or an HTML-to-PDF/InDesign renderer) into a
   single print-ready PDF per book.
6. **Publish**: the finished PDF is attached to a
   [GitHub Release](https://github.com/bipulroybpl/free-printable-kids-books/releases)
   so parents can download it directly — see `.github/workflows/README.md`
   for the full CI/CD pipeline.

## Print specifications

All free printable books in this repo share one print spec, defined once in
`templates/book_metadata_schema.json` and `templates/print-style.css`:

- **Trim size**: 8.5in x 8.5in (square format, common for picture books).
- **Resolution**: 300 DPI — at trim size this is 2550x2550px; with bleed,
  2625x2625px.
- **Bleed**: 0.125in on all four sides. All full-bleed art must extend to the
  bleed edge; keep text and key visual elements inside the "safe area"
  (0.25in inset from the trim line — see `.safe-area` in `print-style.css`).
- **Color mode**: Final print files must be converted to **CMYK** before
  submission to a printer. AI-generated/raw assets are typically RGB —
  convert during the `assets/raw/` → `assets/final/` step, using the target
  printer's ICC profile if one is specified.
- **Fonts**: Always embed fonts in the final PDF. See
  `shared_assets/fonts/README.md` for recommended open-source kids fonts
  (Fredoka, Nunito, Comic Neue) and age-specific usage guidance.

## Adding a new free kids book

1. Create `books/<age-range>/<book-id>/` following the existing structure.
2. Copy the `metadata.json` shape from an existing sibling book and validate
   it against `templates/book_metadata_schema.json`.
3. Write `manuscript.md` first, then derive `prompts/image_prompts.json` from
   it — don't skip straight to image prompts without a manuscript.
4. Pick the appropriate palette from
   `shared_assets/color_palettes/palettes.json` for the target age band.
5. Run through the content safety checklist above before generating final
   assets.

## License

Code, schema, and tooling: MIT (see [LICENSE](LICENSE)). Final book PDFs are
free to download and print for personal/educational use — see the note in
`LICENSE` regarding separate terms for illustrations and manuscripts.

## Keywords

free printable kids books, free children's books pdf, high contrast baby book,
baby book for newborns, toddler feelings book, emotions book for toddlers,
kids drawing book, how to draw for kids step by step, free printable coloring
book, open source children's books, print-ready book design system
