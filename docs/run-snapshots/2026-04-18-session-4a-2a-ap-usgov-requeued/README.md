# Phase 0 AP US Gov Unit 1 — requeued (Session 4a-2a Step 5)

Clean re-acquisition of the AP US Government and Politics CED, Unit 1
("Foundations of American Democracy"), after the extraction-quality
fix from Session 4a-2a.

- **Supersedes:**
  `docs/run-snapshots/2026-04-18-session-4a-1-phase0-test-ap-usgov/`
  (and the live outputs directory
  `outputs/phase0-test-ap-usgov-unit1-2026-04-18/`, marked
  `SUPERSEDED.md`).
- **Origin URL:** `https://apcentral.collegeboard.org/media/pdf/ap-us-government-and-politics-course-and-exam-description.pdf`
- **Publication:** College Board — AP United States Government and
  Politics Course and Exam Description (CED), 2023.
- **Source type (detected):** `flat_pdf_linear` (via detector fallback
  for large PDFs — see Session 4a-1 notes).
- **Scope:** `page_range=[40, 55]`,
  `section_heading="Foundations of American Democracy"` (verification
  only), `pdf_dedup_coords=True`,
  `pdf_dedup_coord_tolerance=1`.
- **Sequence:** `fetch_pdf_file → extract_pdf_text_deduped → normalise_whitespace → verify_extraction_quality → content_hash`
- **Content hash:** `e6eea33806b8ab5ef1b17955d3417032ec549e602262c45f48d20b40c06f396d`
- **Detection hash:** `1798f5cb42351397d17814760e95fd23066c69ea98a0c5433d7e156a5be9ac87`
- **Content size:** 24,586 chars across 828 lines.
- **Chars removed by dedup:** 2,067 (8 % of 26,218 raw chars across 16
  pages, matching the investigation's footer-only projection).
- **Verification verdict:** `clean` (all four checks pass).
- **pdfplumber version:** 0.11.9.
- **phase0_version:** `0.3.0`.

## Files

- `manifest.json` — full acquisition manifest (schema 0.3.0,
  including `verification_trace`).
- `_detection.json` — type-detector output (unchanged from 4a-1).
- `content.txt` — normalised UTF-8 text of pages 40–55, with the
  three-line overlaid footer deduplicated.
- `spot-check.txt` — rendered manifest summary including the
  verification trace.

## What changed vs Session 4a-1's AP artefact

- **Extraction primitive:** `extract_pdf_text_deduped` replaces
  `extract_pdf_text` (opt-in via `pdf_dedup_coords=True`). The deduped
  variant groups `page.chars` by `(round(x0), round(top), text)` and
  keeps one representative per group before reassembling text.
- **Verification primitive:** `verify_extraction_quality` is a new
  mandatory step in the `flat_pdf_linear` sequence. The verdict for
  this artefact is `clean`; for comparison, the superseded 4a-1 AP
  content returns verdict `failed` under the same checks (systematic
  character-doubling, mean line ratio 0.43, 64 flagged lines).
- **Manifest schema:** 0.2.0 → 0.3.0 (adds the
  `verification_trace` field).
- **Content hash:** `47d41e8b…` (4a-1) → `e6eea338…` (4a-2a). The
  4a-1 hash is preserved as an audit fingerprint of the corrupt
  extraction.

## Verification summary

```
character_doubling   value=0.0    threshold=0.2  [ok]
repeated_bigram      value=0.183  threshold=0.75 [ok]
whitespace_runs      value=0      threshold=50   [ok]
empty_line_ratio     value=0.021  threshold=0.6  [ok]
```
