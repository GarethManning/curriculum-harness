# AP CED character-doubling investigation — 2026-04-18

## Context

Session 4a-1 extracted the AP US Government CED PDF (198 pages) with scope
`page_range=[40,55]`. The manifest reported `extract_pdf_text` as `status:
"ok"` with 26,338 chars. But the content contained doubled characters:
`"AAPP UU..SS.. GGoovveerrnnmmeenntt"` and
`"RReettuurrnn ttoo TTaabbllee ooff CCoonntteennttss"`. Session 4a-1's
self-assessment guessed two-column Y-line interleaving; panel review raised
two alternative hypotheses (pdfplumber parameter misconfiguration;
character-stream duplication in the source PDF).

This memo records the empirical investigation that classifies the
mechanism and selects the fix.

## Investigation

PDF: `outputs/phase0-test-ap-usgov-unit1-2026-04-18/_source.pdf`
(11,627,002 bytes, 198 pages, pdfplumber 0.11.9).

Primary diagnostic page: 48 (known-affected by 4a-1 verification_excerpt).
Secondary pages inspected: 40 (first page in scope), 42, 55 (last page in
scope). Diagnostic scripts under `/tmp/session-4a-2a-investigation/`.

### Six extraction samples (head of page 48, first 500 chars)

1. **`page.extract_text()` (default)** — 1351 chars, body text clean:
   `"UNIT\nFoundations of American Democracy 1\nTOPIC 1.4 SUGGESTED SKILL\nSource Analysis\nChallenges of\n4.B\n..."`.
2. **`page.extract_text(layout=True)`** — 5441 chars, layout-padded but
   still emits doubling in footer region.
3. **`page.extract_text(x_tolerance=2, y_tolerance=2)`** — identical
   output to default (1351 chars).
4. **`page.extract_text(layout=False, use_text_flow=True)`** — 1373 chars;
   different reading order, footer doubling absent from mid-body but
   re-appears at tail, and introduces a new artefact: page-number "48"
   is duplicated as `"48 48"` because the doubled footer is parsed as
   two separate text streams.
5. **`extract_words()` reassembled by `round(top)`** — 1351 chars, same
   doubling pattern as default.
6. **`page.chars` coordinate analysis** — see next section.

No parameter combination produces a clean extraction without introducing
a different artefact (sample #4 replaces the doubling with "48 48"
page-number duplication). Path A (parameter fix) is ruled out.

### `page.chars` coordinate analysis — per page

| page | chars_total | coord_dup_groups | adjacent_same_char_pairs | total_adjacent_pairs |
|------|-------------|------------------|--------------------------|----------------------|
| 40   | 372         | 129              | 114                      | 357                  |
| 42   | 3,444       | 129              | 145                      | 3,350                |
| 48   | 1,346       | 129              | 130                      | 1,298                |
| 55   | 963         | 131              | 127                      | 931                  |

`coord_dup_groups` = number of (round(x0), round(top), text) triples that
appear 2+ times — i.e. same character at same coordinates. On every page,
this count is ~129, independent of body-text volume.

Sample dup triples on page 48 (all at `top=773` — the "Return to Table of
Contents" footer line):

```
("R", x0≈468, top=773) × 2
("e", x0≈473, top=773) × 2
("t", x0≈477, top=773) × 2
("u", x0≈480, top=773) × 2
("r", x0≈484, top=773) × 2
("n", x0≈487, top=773) × 2
(" ", x0≈492, top=773) × 2
("t", x0≈494, top=773) × 2
("o", x0≈496, top=773) × 2
```

Per-line flagging (doubling ratio ≥ 0.3, min 4 chars) surfaces the same
three lines on every page, at `top` values 764, 773, 779:

- **top=764** — `"AAPP  UU..SS..  GGoovveerrnnmmeenntt ..."` — running
  brand footer `"AP U.S. Government and Politics Course and Exam
  Description"`.
- **top=773** — `"RReettuurrnn  ttoo  TTaabbllee  ooff  CCoonntteennttss"` —
  TOC-link footer.
- **top=779** — `"\u00a9\u00a9  22002233  CCoolllleeggee  BBooaarrdd"` —
  copyright line.

Body-text lines (all other `top` values) show no adjacent-char doubling.

### Classification

**Mechanism B — coordinate-level overlapping text.** The PDF renders the
three-line footer twice at identical (x0, top) coordinates on every page.
pdfplumber's character stream includes both copies, so `extract_text`
emits each character twice in reading order, producing `"RR"` `"ee"`
`"tt"` etc.

This is not Mechanism A (no parameter combination fixes it cleanly) and
not Mechanism C (the duplicates are at the SAME coordinates, not at
adjacent different coordinates — a character-stream duplication would
show adjacent duplicates at distinct x0 values).

Additional per-page `adjacent_same_char_pairs` counts (114–145 across the
four pages) reflect incidental legitimate adjacencies in the footer
text: double-space between words, `"SS.."` sequences, etc. These do not
indicate a separate mechanism.

### Dedup verification

A coordinate-level dedup (group `page.chars` by
`(round(x0), round(top), text)`, keep one representative, reassemble in
`top`-then-`x0` order) produces clean output:

- Page 40 tail:
  `"...\nAP U.S. Government and Politics\u2002Course and Exam DescriptionCourse Framework\u2002V.1\u2003\u200333\nReturn to Table of Contents\n\u00a9 2023 College Board"`.
- Page 48 tail:
  `"...\nAP U.S. Government and Politics\u2002Course and Exam DescriptionCourse Framework\u2002V.1\u2003\u200341\nReturn to Table of Contents\n\u00a9 2023 College Board"`.
- Page 55 tail: clean, ends `"\u00a9 2023 College Board"`.

Character counts after dedup: 243 (page 40), 1,217 (page 48), 832 (page
55) — roughly 10 % of chars removed per page, consistent with footer-only
duplication.

## Recommended fix — Path B

Create `curriculum_harness/phases/phase0_acquisition/primitives/extract_pdf_text_deduped.py`
as a variant of `extract_pdf_text` that:

1. Groups `page.chars` by `(round(x0, tol), round(top, tol), text)` where
   `tol` is a configurable rounding precision (default 1 pixel, exposed
   as a primitive parameter and recorded in the acquisition trace).
2. Keeps one representative per group.
3. Reassembles text by sorting unique chars by `top` then `x0` per page.
4. Records the dedup count per page in the primitive's trace (`summary` /
   `meta`).

Keep `extract_pdf_text` as the fast path. The deduped variant is opt-in
via scope spec; Session 4a-2a's `verify_extraction_quality` primitive
auto-selects it when the fast path produces a "failed" verdict. This
composition preserves the fast path for well-behaved PDFs and avoids
incurring dedup cost on every extraction.

## Why not operate at text level

A regex `(.)\1 → \1` collapse would corrupt legitimate English doubles
(`"book"`, `"see"`, `"off"`, `"add"`, `"ll"`, ligatures). A page-level
threshold gate (collapse only if >30% of adjacent pairs are doubled) was
considered as safer but still coarser than coordinate dedup: some pages
might have footer-doubling that falls below the threshold while other
pages are flagged spuriously due to legitimate content. Coordinate dedup
is the precise tool — it targets exactly the failure mode observed and
leaves body text untouched.
