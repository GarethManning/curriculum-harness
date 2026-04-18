# Phase 0 flat-PDF primitive test — AP US Government Unit 1 (2026-04-18)

Frozen artefacts from Session 4a-1 Step 5. Second of the two PDF-source
tests for the `flat_pdf_linear` primitive sequence. Shape-variation
case: scoped page-range extraction (Unit 1 only), two-column topic
pages, section-heading verification.

- **Origin URL:** `https://apcentral.collegeboard.org/media/pdf/ap-us-government-and-politics-course-and-exam-description.pdf`
- **Publication:** College Board — AP United States Government and
  Politics Course and Exam Description (CED), 2023.
- **Source type (detected):** `flat_pdf_linear` (defaulted via detector
  fallback; see below).
- **Scope:** `page_range=[40, 55]` + `section_heading="Foundations of
  American Democracy"` (verification only).
- **Sequence:** `fetch_pdf_file → extract_pdf_text → normalise_whitespace → content_hash`
- **Content hash:** `47d41e8bc6031c9bc91decaa0be5b65f11357452022202d26d662ef0bea7215a`
- **Detection hash:** `1798f5cb42351397d17814760e95fd23066c69ea98a0c5433d7e156a5be9ac87`
- **Content size:** 26,338 chars across 690 lines.
- **pdfplumber version:** 0.11.9.

## Files

- `manifest.json` — full acquisition manifest.
- `_detection.json` — type-detector output.
- `content.txt` — normalised UTF-8 text of pages 40–55.

## Acquisition notes

- **Local-path acquisition.** College Board's `robots.txt` is
  `Disallow: /` for `User-agent: *`, which caused the first URL-based
  run to be blocked by our robots-respecting fetch primitive. The CED
  is a publicly-distributed document; a human mirror was downloaded
  once on 2026-04-18 and the local path supplied to the primitive as
  `source_reference`. The origin URL is preserved in `scope_requested.notes`
  for provenance.
- **Detector fallback to `flat_pdf_linear`.** The detector fetches
  ~200 KB for classification; pypdf can't parse a truncated head of an
  11 MB PDF, so the CED returned `PDF parse failed`. Rather than
  routing to `unknown`, the detector now falls back to
  `flat_pdf_linear` with low confidence when `%PDF-` magic is present.
  The primitive's own fetch re-reads the full file. `_detection.json`
  records this rationale.
- **Heading verification.** `page_range` wins when both scope fields
  are supplied; `section_heading="Foundations of American Democracy"`
  was recorded as verification-only and confirmed as present within
  pages 40–55 (`heading_verification.heading_found = true`,
  `heading_line = "1 Foundations of American Democracy"` at extracted
  line 105).

## Expected vs acquired

Expected: Unit 1 opener, Unit at a Glance, Sample Instructional
Activities, Topics 1.1–1.9 each with Learning Objective + Essential
Knowledge statements. Unit 2 content excluded.

Acquired:
- All nine topics present (`TOPIC 1.1` … `TOPIC 1.9` in the content).
- 11 `LEARNING OBJECTIVE` markers and 11 `ESSENTIAL KNOWLEDGE`
  markers (some topics have multiple LOs/EKs).
- 13 occurrences of "Foundations of American Democracy" (unit banner
  on each content page).
- Zero `UNIT 2` / `Interactions Among Branches of Government` mentions
  → scope boundary is clean.

## Known pdfplumber limitation on two-column topic pages

On topic-content pages, pdfplumber's default text extraction (and the
`layout=True` variant) groups words across the two columns by shared
Y-coordinate, which produces sidebar/body interleaving. Example from
Topic 1.3 (p47):

```
1.A
Describe political principles,
institutions, processes, and Individual Rights
policies, and behaviors.
OPTIONAL READING Required Course Content
```

Here "Individual Rights" comes from a right-hand sidebar and has
been interleaved with the body sentence "institutions, processes,
and policies, and behaviors." The underlying substance is preserved
— every LO, EK, and topic heading is present and associated with its
topic — but Y-aligned column spans are mixed into single lines. The
header glyph doubling ("AAPP UU..SS..") is a font-rendering artifact
of the double-stroke CED header style and is expected on these pages.

**This is not a correctness failure for the primitive.** The
abstraction holds: `page_range` scoping works; `section_heading`
verification works; the Unit 2 boundary is honoured; the content is
faithful to the source at the glyph level.

**Open item for Session 4a-2** (multi-section PDFs): add a
column-aware extraction path. Options documented in the Session 4a-1
log entry — either per-page column bounding-box cropping, or exposing
a scope flag that switches to `extract_words()` with x-sorted
column-band grouping. pdfplumber's default remains the right choice
for single-column documents (see `docs/run-snapshots/2026-04-18-session-4a-1-phase0-test-dfe-ks3/`
where the same primitive produced clean output).
