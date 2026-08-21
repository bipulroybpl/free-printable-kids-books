# Recommended Fonts (Ages 0-5)

Open-source, freely licensed fonts suited to children's book print and digital
use. Font files themselves are not checked into this repo — download from
Google Fonts (or the listed source) and place `.ttf`/`.otf` files locally
before rendering.

## Primary recommendations

### Fredoka
- **Style**: Rounded, friendly, geometric sans-serif.
- **Best for**: Titles, headers, ages 2-5. Rounded terminals read as
  non-threatening and are easy for early readers to distinguish.
- **License**: SIL Open Font License (OFL).
- **Source**: Google Fonts.

### Nunito
- **Style**: Rounded sans-serif, excellent legibility at small and large sizes.
- **Best for**: Body text for read-aloud pages, ages 2-5. Balanced x-height
  keeps letterforms clear for both parent and emerging reader.
- **License**: SIL Open Font License (OFL).
- **Source**: Google Fonts.

### Comic Neue
- **Style**: A cleaned-up, more legible alternative to Comic Sans.
- **Best for**: Playful dialogue/callout text, ages 3-5. Familiar casual tone
  without the legibility issues of the original Comic Sans.
- **License**: SIL Open Font License (OFL).
- **Source**: Google Fonts.

## Age-specific guidance

- **Ages 0-1**: Avoid relying on typography for this age group entirely —
  infants respond to high-contrast shapes/patterns, not text. If any text
  appears (e.g. for the reading adult), keep it minimal and use Nunito.
- **Ages 2-3**: Favor Fredoka/Nunito at large point sizes (≥ 24pt in print).
  Avoid thin or condensed weights — low contrast strokes are harder for
  developing vision to track.
- **Ages 4-5**: Fredoka, Nunito, and Comic Neue are all suitable. Numbered
  step sequences (e.g. step-by-step-drawing) should use a consistent numeral
  style across the book.

## General rules

- Never use all-caps for body text (harder for early readers to parse
  word shapes).
- Maintain minimum 18pt body text size per `templates/book_metadata_schema.json`.
- Always embed fonts (not outline/rasterize) until the final print PDF export
  stage, to keep source files editable.
