# Phase 0 — Acquisition

Phase 0 separates **acquisition** from extraction. It takes a source
reference (URL or local path) plus a structured scope spec, classifies
the source into a supported type, runs the matching primitive sequence,
and emits a manifest plus one or more content text files.

Downstream phases never read raw URLs. They read:

- `manifest.json` — acquisition trace, content hash, detection hash,
  scope requested vs acquired, any user interactions.
- `content.txt` (and siblings) — normalised UTF-8 text.

## Supported source types

| Source type                          | Primitive sequence                                                                                                                                                                                                                                               | Status       |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| `static_html_linear`                 | `fetch_requests → encoding_detection → extract_* → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                                                                        | implemented  |
| `flat_pdf_linear`                    | `fetch_pdf_file → (extract_pdf_text \| extract_pdf_text_deduped) → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                                                        | implemented  |
| `multi_section_pdf`                  | `fetch_pdf_file → detect_toc → resolve_section_scope → (extract_pdf_text \| extract_pdf_text_deduped) → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                   | implemented  |
| `js_rendered_progressive_disclosure` | pending                                                                                                                                                                                                                                                          | deferred     |
| `html_nested_dom`                    | pending                                                                                                                                                                                                                                                          | deferred     |

Deferred types raise `Phase0Paused` with a user-in-the-loop request file.

## `flat_pdf_linear` primitive sequence

pdfplumber-backed, deterministic, no model calls.

**Scope.** Required: `source_reference` (URL or local filesystem path).
Optional: `page_range` (`[start, end]` 1-indexed inclusive, or the legacy
string form `"start-end"`); `section_heading` (literal or regex, toggled
by `heading_regex`). When both scope fields are set, `page_range` wins
and `section_heading` is recorded as verification-only in the primitive
trace (`heading_verification.heading_found`).

**No encoding_detection step.** pdfplumber handles PDF encoding
internally and emits UTF-8 strings directly. The absence of
`encoding_detection` from the sequence is deliberate and visible in
the manifest's `primitive_sequence` list.

**Coordinate-level overlaid text (Session 4a-2a, handled).** Some PDFs
render running headers/footers twice at identical `(x0, top)`
coordinates — pdfplumber emits every character in the stream, so
`extract_text` produces `"RR"` `"ee"` `"tt"` runs. Observed on the AP
US Gov CED. The fix is `extract_pdf_text_deduped`, which groups
`page.chars` by `(round(x0/tol), round(top/tol), text)` and keeps one
representative per group before reassembling text. Opt-in via
`pdf_dedup_coords=True` in the scope spec (see
`docs/diagnostics/2026-04-18-ap-ced-doubling-investigation.md`). Body
text is untouched; only duplicated glyphs are removed.

**Known limitations.**

- **Image-only PDFs** (no embedded text layer) need OCR. pdfplumber
  returns empty text, surfaced via `chars_out: 0` in the trace.
- **Encrypted PDFs** need a decryption key. pdfplumber raises on
  open, recorded as `extract_failure: pdfplumber_open_failed: ...`.
- **Multi-column layouts on topic-content pages** (e.g. AP CED-style
  learning-objective tables) suffer Y-aligned sidebar/body
  interleaving with pdfplumber's default and `layout=True` extraction.
  Substance preserved; line sequencing mixed. See the AP US Gov Unit
  1 run snapshot for a worked example.
- **Form-filled PDFs** extract the form's static text; filled-field
  values are partially recovered depending on the encoding used by
  the form author.

**Test artefacts.**

- `docs/run-snapshots/2026-04-18-session-4a-1-phase0-test-dfe-ks3/` —
  UK DfE statutory KS3 Maths programme of study. Full-document
  extraction; single-column; all six subject-content strands present.
  Regression-verified byte-clean under schema 0.4.0 in
  `docs/run-snapshots/2026-04-18-session-4a-2a-regression-dfe-ks3/`.
- `docs/run-snapshots/2026-04-18-session-4a-1-phase0-test-ap-usgov/` —
  AP US Gov CED, Unit 1. **Superseded** by the 4a-2a requeue;
  retained for audit under schema 0.4.0 with a `SUPERSEDED.md` note.
- `docs/run-snapshots/2026-04-18-session-4a-2a-ap-usgov-requeued/` —
  Clean re-acquisition under the coordinate-dedup primitive and
  `verify_extraction_quality`. Verification verdict `clean`.
  `known_pathology_handling: ['coordinate_level_footer_overlap']`.

## `multi_section_pdf` primitive sequence (Session 4a-2b)

For PDFs with a multi-section structure — a table of contents, an
embedded outline, or clearly heading-demarcated sections. The
detector routes a PDF here when `page_count >= 50` and either the
embedded outline has >= 2 top-level entries or the TOC-page
heuristic detects >= 3 dot-leader entries.

**Scope.** Required: `source_reference`. One of `page_range`,
`section_identifier` (exact TOC-title match), or `section_heading`
(case-insensitive prefix / regex match) must resolve — the
`resolve_section_scope` primitive pauses Phase 0 with the available
TOC entries if none does. Optional: `pdf_dedup_coords=True` for PDFs
with a coordinate-level pathology (none observed on Ontario per
Step 3's pre-check).

**`detect_toc` primitive.** Three-tier deterministic TOC detection,
no model calls:

1. **Embedded outline** via pypdf's outline tree. Yields
   `{title, page_number (1-indexed), depth, source}`. When an AODA
   structure tree (`/StructTreeRoot`) is present, it is flagged in
   the detection trace as `struct_tree_present: true` but the primary
   outline continues to drive section resolution — downstream
   consumers can opt into the structure tree in a later session.
2. **TOC-page heuristic** when no embedded outline exists. Scans the
   first 20 pages for a page titled `Contents` / `Table of Contents`,
   then parses leader lines (`title……… page_number`).
3. **Heading-structure inference** (last-resort fallback). Classifies
   lines by predominant char-height from `page.chars`; lines whose
   font is 1.35× the body-text median are flagged as headings,
   tagged `source: heading_inference` with lower confidence.

**`resolve_section_scope` primitive.** Reads the TOC from
`detect_toc`'s meta and the scope spec, producing an explicit
`[start, end]` range. Priority: explicit `page_range` wins, else
`section_identifier` (exact), else `section_heading` (fuzzy /
regex). The resolved range is propagated via `meta` so the extractor
honours it preferentially over `scope.page_range`. When no field
resolves, Phase 0 pauses with a prompt listing the available TOC
entries.

**Multi-pathology handling.** Step 3's Ontario pre-check found no
letter-level coordinate overlap at tolerances 1 or 2; the multi-
section sequence therefore defaults dedup off. Sources with a single
confirmed pathology route through the deduped extractor via
`pdf_dedup_coords=True`. Chained multi-pathology dedup is deferred
until a source with >1 confirmed pathology is observed.

**Test artefact.**

- `docs/run-snapshots/2026-04-18-session-4a-2b-ontario-g7-history/` —
  Ontario K-8 Social Studies / History / Geography (2023),
  Grade 7 History strand. `section_identifier="History, Grade 7"`
  auto-resolves to pages 245–266 via the embedded outline.
  Triangulated verification (Step 10): Check A structural PASS,
  Check B 6/6 exact overall-expectation titles, Check C volume
  46,227 chars over 22 pages with clean grade boundaries. Session
  outcome PASS WITH NOTES (Check C threshold recalibration
  recommended).

## Scope spec

`ScopeSpec` (Pydantic) carries the union of fields across all primitive
sequences. Each primitive validates the subset it needs and raises
`ScopeValidationError` if any required field is missing; the executor
converts that into a hand-editable `request.md` + `state.json` pause.

## Manifest schema (v0.4.0)

- `content_hash` — SHA-256 of the final normalised content bytes.
- `detection_hash` — SHA-256 of the `_detection.json` payload, so the
  type-detector output is tamper-evident and part of the audit trail.
- `scope_acquired.verification_excerpt` — `{first_chars, last_chars,
  line_count}` snapshot for visual inspection without loading the full
  content file.
- `verification_trace` (schema 0.3.0+) — list of `VerificationEntry`
  records, one per verification primitive. Multi-section and flat-PDF
  sequences now produce two entries (raw-mode and normalised-mode —
  see the `verify_extraction_quality` section below).
- `known_pathology_handling` (new in 0.4.0) — list of
  `KnownPathology` enum values the acquisition was configured to
  handle. Append-only enum with four reserved entries
  (`coordinate_level_footer_overlap` observed in AP CED; three others
  reserved for future confirmed pathologies). Pydantic rejects
  unknown values on write.
- `investigation_memo_refs` (new in 0.4.0) — list of diagnostic-memo
  paths relevant to this acquisition (e.g. a memo recording the
  investigation that identified a pathology).

## `verify_extraction_quality` primitive

A mandatory step in every primitive sequence. Runs deterministic
statistical checks on the extracted content and returns a verdict.
As of Session 4a-2b Step 4 the primitive runs in **two modes** within
every production sequence — the raw-mode pass catches signals that
`normalise_whitespace` would destroy, the normalised-mode pass does
the rest.

- **raw mode** (`verify_raw_extraction`, inserted between the
  extractor and `normalise_whitespace`):
  - `whitespace_runs` — count of 80+ contiguous whitespace runs.
    Must run pre-normalise; the normalise step would collapse the
    pattern into a single space and make the check a false
    reassurance.
- **normalised mode** (`verify_normalised_extraction`, inserted
  after `normalise_whitespace`):
  - `character_doubling` — per-line ratio of identical adjacent
    non-whitespace pairs, plus systematic-pattern detection (≥ 5
    lines with mean ratio ≥ 0.4) to catch footer-only doubling that
    would fall below a document-wide threshold.
  - `repeated_bigram` — top-10 letter-bigram share (typical English
    ~0.25; failure at 0.75). **Language-aware calibration** (Step 5):
    a conservative stopword-based English detector runs first; on
    non-English or low-confidence text a bigram failure is
    downgraded to `suspicious` rather than `failed`, with the
    downgrade reason recorded in the trace. Rationale: the project
    has no calibration data for non-English bigram statistics.
  - `empty_line_ratio` — fraction of lines that are empty or
    whitespace-only.
  - `completeness` (new in Step 6) — expected content volume
    against source metadata harvested by the executor. HTML: flagged
    below 5 % of fetched bytes, failed below 2 %. PDF: flagged
    below 50 chars/page, failed below 20 chars/page. Skipped with
    a recorded reason when neither metric is available.

Verdict `failed` pauses the pipeline with a user-in-the-loop request
that suggests a recovery scope change (e.g. `pdf_dedup_coords: true`
for systematic character-doubling). Verdict `suspicious` continues
with a warning recorded in the trace. Verdict `clean` is the happy
path.

No model calls. Thresholds are constructor arguments, exposed in the
trace so the audit record is reproducible. Adversarial regression
tests live in `tests/phase0/test_verify_extraction_quality.py` and
cover all five checks plus the language-aware downgrade and the
"whitespace runs are dead after normalisation" contract.

## Triangulated verification (Session 4a-2b Step 10)

For load-bearing new-source tests, a single check is not enough. The
Ontario Grade 7 History test used a three-check triangulation:

- **Check A — structural plausibility.** Shape assertions on the
  extracted content (strand headings, overall-expectation codes,
  section markers). Independent of what the content says.
- **Check B — screenshot title match.** Assertion that specific
  titles from an independent ground-truth source (a curriculum-site
  screenshot) appear in the extracted content verbatim.
- **Check C — volume sanity.** Total character count against a
  plausible range derived from the source's page count and
  per-page density.

No single check bears full weight. A mismatch in one, where the
other two pass and boundary inspection confirms clean scoping, is
evidence that the specific check's threshold is miscalibrated rather
than evidence of extraction failure. The Ontario test's PASS WITH
NOTES classification (Check C's 30k ceiling was too tight for a
2,100-char/page curriculum) is the worked example documented in the
run-snapshot README.

## Known downstream risks

### Tag-boundary line fragmentation

The `normalise_whitespace` primitive preserves line separators produced
by source tag boundaries — an HTML `<i>` inside a paragraph surfaces as
a new line, a span split inside a PDF paragraph surfaces as a new line.
Phase 0 is deliberately **faithful to source structure**; it does not
re-flow text across tag boundaries because re-flowing would be a lossy
decision that belongs in a semantic layer.

**Implication for downstream phases.** Any code that treats each line
as a semantic unit — notably `source_bullets` extraction in Phase 1 —
should expect fragmented inline content. The Common Core 7.RP test
artefact shows this pattern (embedded-example fractions on three
lines: `1/2`, `/`, `1/4`).

**Responsibility.** Phase 0 preserves fragments. Phase 1 (or
whichever phase owns semantic reconstitution) is responsible for
stitching them back together where needed.

### Multi-column PDF page interleaving

See `flat_pdf_linear` — known limitations. The Ontario Grade 7
artefact extracts cleanly under single-column per-page reading order
because the curriculum's multi-column layout is less dense than the
AP CED's sidebar/body columns. Downstream consumers of two-column
PDFs should still expect interleaving on sidebar-heavy pages until a
column-aware extraction primitive is shipped.

## Scheduled (next sessions)

- Session 4a-3: `js_rendered_progressive_disclosure` source-type
  primitive sequence.
- Column-aware extraction for dense multi-column pages (per-page
  bounding-box cropping or x-sorted column-band grouping).
- Multi-pathology chained dedup (only when a source with >1
  confirmed pathology is observed in the test corpus).
