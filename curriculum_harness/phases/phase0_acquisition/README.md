# Phase 0 — Acquisition

Phase 0 separates **acquisition** from extraction. It takes a source
reference (URL or local path) plus a structured scope spec, classifies
the source into a supported type, runs the matching primitive sequence,
and emits a manifest plus one or more content text files.

Downstream phases never read raw URLs. They read:

- `manifest.json` — acquisition trace, content hash, detection hash,
  scope requested vs acquired, any user interactions.
- `content.txt` (and siblings) — normalised UTF-8 text.

## Phase 0 status: COMPLETE (schema 0.6.0)

All five source types ship with a deterministic primitive sequence,
type-detector routing, manifest schema 0.6.0, dual-mode verification,
raw-content caching, and a regression-tested extraction artefact.
Architectural generalisation has been verified in two places:
`extract_nested_dom` handles two structurally-distinct sites
(gov.uk vs hwb.gov.wales — Session 4a-4 Steps 8/9) with scope-only
differences; `fetch_via_browser` handles two structurally-distinct
JS-rendered sites (Ontario DCP vs NZ Curriculum — Session 4a-3)
with scope-only differences. Raw-content caching (Session 4a-4.5)
lets future regression tests re-run extraction against cached bytes
rather than re-fetching from origins that may have become
unavailable. Domain coverage reaches all three curriculum domain
types — hierarchical, horizontal, dispositional — after Session
4a-5 added a dispositional-domain source using existing primitives
unchanged. Next: Session 4b — reference test corpus construction.

## Domain coverage in the extracted corpus

Phase 0's mandate is to handle curriculum sources across the three
domain types the project vision commits to: **hierarchical** (strong
prerequisite ordering, e.g. most mathematics and the sciences),
**horizontal** (broad thematic organisation without strict
prerequisite ordering, e.g. history, humanities), and
**dispositional** (framed around sustained orientations, enabled
capabilities, and occasion-prompted behaviours, e.g. wellbeing,
character, regeneration).

As of Session 4a-5 (2026-04-19), the extracted corpus covers all
three domain types. This is the precondition Session 4b's reference
corpus design requires.

| Domain type    | Source                                              | Primitive sequence                 | Run snapshot                                                                                |
| -------------- | --------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------- |
| hierarchical   | Common Core 7.RP                                    | `static_html_linear`               | `docs/run-snapshots/2026-04-18-session-4a-2a-regression-common-core-7rp/`                    |
| hierarchical   | UK DfE KS3 Maths (statutory PDF)                    | `flat_pdf_linear`                  | `docs/run-snapshots/2026-04-18-session-4a-1-phase0-test-dfe-ks3/`                            |
| hierarchical   | UK gov.uk National Curriculum Maths KS3             | `html_nested_dom`                  | `docs/run-snapshots/2026-04-18-session-4a-4-gov-uk-nc-maths-ks3/`                            |
| hierarchical   | Welsh CfW Maths & Numeracy SoW                      | `html_nested_dom`                  | `docs/run-snapshots/2026-04-18-session-4a-4-wales-cfw-maths-sow/`                            |
| horizontal     | Ontario Grade 7 History (K-8 PDF)                   | `multi_section_pdf`                | `docs/run-snapshots/2026-04-18-session-4a-2b-ontario-g7-history/`                            |
| horizontal     | Ontario Grade 7 History (DCP site)                  | `js_rendered_progressive_disclosure` | `docs/run-snapshots/2026-04-18-session-4a-3-ontario-dcp-g7-history/`                       |
| horizontal     | AP US Government Unit 1 (CED PDF)                   | `flat_pdf_linear`                  | `docs/run-snapshots/2026-04-18-session-4a-2a-ap-usgov-requeued/`                             |
| dispositional  | Welsh CfW Health and Well-being SoW (source_archetype: `rich_dispositional`) | `html_nested_dom` | `docs/run-snapshots/2026-04-19-session-4a-5-wales-cfw-health-wellbeing-sow/`                 |

**Session 4a-5 architectural finding.** The dispositional-domain
source was extracted using the `html_nested_dom` primitive sequence
unchanged from Session 4a-4 Step 9. Scope fields are structurally
isomorphic to the Welsh Maths SoW run: identical
`content_root_selector="article#aole-v2"`, identical
`exclude_selectors`, no section scoping. Only the URL differs. This
is confirming evidence that Phase 0 primitives generalise across
**curriculum domain types**, not merely across **website structural
types**. The architecture handled a dispositional-domain source
without modification; the "no site-specific `if` branches in the
primitive" discipline held.

**Check B outcome.** Welsh CfW Health and Well-being SoW classified
as `rich_dispositional` (source_archetype recorded in
`verification_trace.dispositional_content_distribution`). Sampled
distribution: Category 1 = 4 / Category 2 = 3 / Category 3 = 2 /
Uncertain = 1 (sample size 10). All three categories are present;
two lines classified as Category 3 (sustained operating states)
establish visible dispositional-as-enacted content beyond mere
propositional claims about dispositions. The five mandatory
Statements of what matters in their surface form are propositional
claims about dispositions (Category 1), but the explanatory
paragraphs carry occasion-prompted skills (Category 2) and
sustained-orientation framing (Category 3).

**Scope note — extraction success ≠ harness validation.** This
session validates that Phase 0 can **acquire** dispositional-domain
content. It does **not** validate Phase 1+ harness behaviour on
dispositional content — the KUD extractor, Learning Target generator,
and surface-form gates have not yet been exercised on a
dispositional-domain source. That work belongs to Session 4b and
onwards.

**4b planning hint — operational underspecification.** Even for
`rich_dispositional` sources, dispositional content often carries
operational underspecification: the Statements of what matters
surface as propositional claims whose intended operationalisation
depends on teacher interpretation. Reference writers for 4b will
face the question of what's authorised when the source
underspecifies a construct — invent specificity (injection,
forbidden), preserve the underspecification (may leave the reference
too vague to assess), or annotate the gap explicitly. This is a 4b
design decision, not a 4a-5 decision, but flagged here so it is
visible in 4b planning.

## Supported source types

| Source type                          | Primitive sequence                                                                                                                                                                                                                                               | Status       |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| `static_html_linear`                 | `fetch_requests → encoding_detection → extract_* → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                                                                        | implemented  |
| `flat_pdf_linear`                    | `fetch_pdf_file → (extract_pdf_text \| extract_pdf_text_deduped) → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                                                        | implemented  |
| `multi_section_pdf`                  | `fetch_pdf_file → detect_toc → resolve_section_scope → (extract_pdf_text \| extract_pdf_text_deduped) → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                   | implemented  |
| `js_rendered_progressive_disclosure` | `fetch_via_browser → dom_hash → extract_css_selector → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                                                                     | implemented  |
| `html_nested_dom`                    | `fetch_requests → encoding_detection → extract_nested_dom → verify_raw → normalise_whitespace → verify_normalised → content_hash`                                                                                                                                | implemented  |

Future deferred types (none currently planned) would raise
`Phase0Paused` with a user-in-the-loop request file.

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

## `html_nested_dom` primitive sequence (Session 4a-4)

For deeply-nested HTML curriculum pages whose content is rendered in
the initial server response but distributed across a chrome-heavy DOM
that needs structured selector-based scoping. Two structurally-
distinct site shapes are validated:

- **Hierarchical with section scoping** (gov.uk pattern). One deep
  content container holds multiple co-equal sub-sections (Key Stages
  1–4) demarcated by sibling `<h2>` headings; sub-section selection
  uses the **heading-anchor** mechanism (`section_anchor_selector`
  picks the start heading; the primitive walks following siblings
  until a sibling matching `section_anchor_stop_selector` — defaults
  to the anchor's own tag).
- **Single main container with in-content chrome stripping** (Welsh
  hwb pattern). One CSS-selectable container holds the entire scope;
  no sub-section anchoring needed; in-page nav, prev/next links, and
  related-content blocks live inside the container and must be
  excluded explicitly via `exclude_selectors`.

**Scope.** Required: `url`, `content_root_selector`. Optional:
`exclude_selectors` (list of CSS selectors to strip — over-exclude
posture); `section_scope_selector` OR `section_anchor_selector` +
`section_anchor_stop_selector` (mutually exclusive scoping
mechanisms); `include_details_content` (default True);
`preserve_headings` (default True).

**`extract_nested_dom` primitive.** Pure capability — BeautifulSoup-
backed, deterministic, no model calls, no per-site branching:

- **`<details>` elements are static HTML.** Their collapsed visual
  state is a browser-level rendering default; the contained text is
  present in the DOM regardless. `include_details_content=True`
  preserves it (the default); `=False` keeps the `<summary>` and
  drops the inner content. This is **fundamentally different from
  JavaScript-rendered accordions** (`<div role="accordion">`,
  `mat-expansion-panel`, custom-element disclosures) whose collapsed
  content is *not* in the static HTML and requires
  `fetch_via_browser` + `click_sequence`.
- **Heading-anchor scoping.** For sites whose sub-sections are flat
  siblings under a common parent (no dedicated container element
  per sub-section), `section_anchor_selector` picks the start
  heading and the primitive walks following siblings until a stop
  element. Default stop is the anchor's own tag.
- **Container scoping.** For sites where a sub-section IS in its own
  CSS-selectable container, `section_scope_selector` picks it
  directly. Mutually exclusive with `section_anchor_selector` —
  setting both is a configuration error caught at construction time.
- **Side effects.** None. The primitive only reads HTML strings from
  the upstream encoding-detection step.

**Site-specific choreography lives in the scope, not in the primitive.**
If the primitive ever needs `if site == ...` to function, that is a
design failure — refactor.

**Test artefacts.**

- `docs/run-snapshots/2026-04-18-session-4a-4-gov-uk-nc-maths-ks3/` —
  UK gov.uk National Curriculum (England) Mathematics KS3.
  `section_anchor_selector="#key-stage-3"`. Triangulated verification
  STRONG PASS on Check A (11/11 strands), STRONG PASS on Check B
  (zero leakage from 13-item gov.uk chrome list per investigation
  memo), PASS on Check C (12 461 chars in 3 000–20 000 range).
  Pipeline `verify_normalised_extraction` `suspicious` due to
  completeness check threshold not yet scope-aware (4.12% of 302KB
  page is the KS3 sub-section — known calibration caveat).
  Outcome: PASS WITH NOTES.
- `docs/run-snapshots/2026-04-18-session-4a-4-wales-cfw-maths-sow/` —
  Welsh hwb Curriculum for Wales Mathematics & Numeracy "Statements
  of what matters". `content_root_selector="article#aole-v2"` plus
  6-item `exclude_selectors`. Triangulated verification STRONG PASS
  on Check A (4/4 mandatory statements), STRONG PASS on Check B
  (zero leakage from 11-item hwb chrome list), PASS on Check C
  (3 792 chars in 2 500–6 000 range). Same calibration caveat as
  gov.uk. Outcome: PASS WITH NOTES.

**Architectural generalisation — VALIDATED.** Same primitive code
handled both sites with scope-only differences (gov.uk:
`section_anchor_selector` heading-anchor; Wales: `exclude_selectors`
list and no section anchor). Different platforms, different
container depths (10 vs 5), different scoping disciplines, different
chrome patterns. No `if site == ...` in the primitive.

## `js_rendered_progressive_disclosure` primitive sequence (Session 4a-3)

For JS-heavy curriculum sites: SPA shells with content injected
client-side (React / Vue / Angular), or heavy-scripted server-rendered
pages that ship enough JS that a requests-based fetch is unreliable.
The detector routes a URL here when JS framework markers
(`#root`, `#app`, `__NUXT__`, `__INITIAL_STATE__`, `data-reactroot`,
`ng-version`, `<mat-*>` Angular Material custom elements) are present
AND the visible-text ratio is thin. Callers can also force-route via
`detection_override` when the auto-detector is ambiguous.

**Scope.** Required: `url`, `wait_for_selector`, `css_selector` (the
extract selector). Optional: `dismiss_modal_selector`, `click_sequence`,
`browser_timeout_ms` (default 30 000).

**`fetch_via_browser` primitive.** Pure capability — Playwright
headless Chromium, no site-specific branching:

- **Fixed viewport 1280 × 720.** Non-configurable by design. The
  rendered-state hash and extraction are tied to the viewport;
  leaving it configurable invites silent reproducibility breakage.
- **Navigation waits for `networkidle`**, not `domcontentloaded`.
  JS frameworks frequently render content via post-DCL XHR, and a
  DCL-level wait lets `wait_for_selector` match an empty shell —
  caught in Session 4a-3's smoke test.
- **Per-click observability.** `click_sequence` is a list of steps,
  each traced individually in the manifest (one entry per click).
  The v3 review chose this explicitly over a terser DSL.
- **Bot-detection taxonomy.** Three distinct pause reasons:
  `bot_detection_http_403`, `bot_detection_rate_limited`
  (429 or Retry-After on a non-2xx), `bot_detection_challenge_page`
  (Cloudflare / verify-human markers). Each pauses Phase 0 for user-
  in-the-loop rather than retrying silently.
- **Side artefacts.** The primitive emits a full-page screenshot as
  `rendered_state.png`; the executor writes it to the output
  directory and appends it to `manifest.content_files`.

**`dom_hash` primitive.** Runs directly after `fetch_via_browser`.
SHA-256s the rendered HTML so consumers can detect "page shape
changed" independently of "extracted text changed" — a JS SPA that
ships identical visible text but swaps an accordion for a tab control
has the same `content_hash` and a different `dom_hash`. The manifest's
`dom_hash` field is null for non-JS source types.

**Multi-source generalisation.** Session 4a-3 validates the primitive
on two structurally different curriculum sites — Ontario DCP (Angular
Material SPA, grade-based) and NZ Curriculum Online (custom CMS,
levels-based, consent modal present). The same primitive handles both
with scope-level differences only (NZ adds `dismiss_modal_selector`,
Ontario does not). Extended multi-jurisdiction robustness testing
(Australian Curriculum, Singapore MOE, US state standards) is
deferred to a potential Session 4a-3.5.

**Site-specific choreography lives in the scope, not in the primitive.**
If the primitive grows an `if site == ...` branch, that is a design
failure — refactor to scope before merging.

**Test artefacts.**

- `docs/run-snapshots/2026-04-18-session-4a-3-ontario-dcp-g7-history/` —
  Ontario Grade 7 History strand-index route. Cross-validated against
  the 4a-2b PDF extraction: Check A structural PASS, Check B 6/6
  exact overall-expectation titles, Check B2 6/6 FOCUS ON match,
  Check C flagged (3 706 < 5 000 threshold, scope caveat — `/strands`
  route intentionally excludes specific-expectations content, which
  lives on SPA-routed sub-pages). Outcome PASS WITH NOTES.
- `docs/run-snapshots/2026-04-18-session-4a-3-nz-curriculum/` —
  NZ Social Sciences Phase 2 (Years 4–6). Check A structural PASS
  (four strands × Knowledge + Practices), Check C volume PASS
  (37 245 chars). Architectural verdict: validated — same primitive,
  one extra optional scope field.

## Source composition and selection

**Current capability.** Phase 0 extracts a single source given an
explicit source reference. A user (or runner script) specifies which
URL or PDF to extract from; the harness does not currently discover
candidate sources or rank them by completeness. One Phase 0 invocation
yields one acquired artefact (manifest + content files).

**Known limitation.** Some curricula are documented across multiple
authoritative sources at different levels of completeness. Concrete
example from this corpus: Ontario Grade 7 History has two extracted
sources —

- `multi_section_pdf` from the K-8 PDF
  (`docs/run-snapshots/2026-04-18-session-4a-2b-ontario-g7-history/`):
  contains both overall and specific expectations, ~46 K chars.
- `js_rendered_progressive_disclosure` from the DCP website
  (`docs/run-snapshots/2026-04-18-session-4a-3-ontario-dcp-g7-history/`):
  overall expectations only, ~3.7 K chars (specific-expectations text
  lives on SPA-routed sub-pages).

For applications that need the full curriculum content, the PDF source
is more authoritative; for applications that need the per-strand
overview that Ontario publishes online, the DCP source is the
canonical wording.

**Multi-source composition is supported today** by running Phase 0
multiple times on the same curriculum and treating the outputs as
complementary artefacts at the consumer layer. There is no built-in
merge / deduplication step.

**Future work hint.** Multi-source selection will likely need a
`sources_catalog` data structure that maps a curriculum reference
(jurisdiction + subject + grade) to the known sources for that
reference, with metadata about each source's coverage and
authoritativeness. Implementation specifics are deferred until
Session 4b establishes which source compositions teachers and AI
tutors actually find useful — premature schema choices here would
constrain the wrong axis.

## Scope spec

`ScopeSpec` is the back-compat constructor (callable) that infers
`source_type` from supplied fields and dispatches to the matching
discriminated-union variant. New code should construct the variant
directly (e.g. `StaticHtmlLinearScope(url=..., css_selector=...)`)
for clearer call sites. Per-type variants live in
`curriculum_harness/phases/phase0_acquisition/scope.py`:

- `StaticHtmlLinearScope` — `url`, one of `css_selector` /
  `heading_text`.
- `FlatPdfLinearScope` — `source_reference`; optional `page_range`,
  `section_heading`, `pdf_dedup_coords`.
- `MultiSectionPdfScope` — `source_reference`, one of `page_range` /
  `section_identifier` / `section_heading`.
- `JsRenderedProgressiveDisclosureScope` — `url`, `wait_for_selector`,
  `css_selector`; optional `dismiss_modal_selector`, `click_sequence`.
- `HtmlNestedDomScope` — `url`, `content_root_selector`; optional
  `exclude_selectors`, `section_scope_selector` *or*
  `section_anchor_selector` (mutually exclusive),
  `section_anchor_stop_selector`, `include_details_content`,
  `preserve_headings`.

Each variant uses Pydantic's `extra="forbid"` so cross-type field
smuggling (e.g. `page_range` on a JS scope) is rejected at
construction time. The forward-compatible deserialiser in `scope.py`
upgrades 0.4.0 flat-shaped manifests to the discriminated union on
load. See `docs/diagnostics/2026-04-18-session-4a-4-step-3b-regression-report.md`
for the regression evidence that the upgrade is byte-stable.

> **Phase 0 expects a specific source reference per run.**
> Multi-source curriculum composition is future work (Session 4b
> onwards). See the "Source composition and selection" section above
> for the current single-source posture and the rationale for
> deferring composition.

## Raw-content caching (Session 4a-4.5)

Every fetch primitive saves the raw fetched bytes alongside the
extracted content in the run-snapshot directory. The manifest's
`raw_content_files` field carries per-file `(path, hash, file_type,
bytes)` records. Downstream regression tests re-run extraction
against the cache rather than re-fetching from the source —
essential because three corpus sources have become
programmatically inaccessible (Common Core 7.RP behind Cloudflare;
NZ Curriculum serving a bot-detection shell; AP CED blanket-
disallowed by robots.txt since the source was first acquired).

**Per fetch primitive:**

- `fetch_requests` writes `raw.html` with `file_type: source_html`.
- `fetch_pdf_file` (URL source) writes `raw.pdf` with
  `file_type: source_pdf`.
- `fetch_pdf_file` (local path) does **not** copy the file — it
  records a `source_reference` entry with the absolute path and a
  SHA-256 of the current bytes. Disk-space discipline: local PDFs
  are often large and already archived, so duplicating wastes disk
  and risks diverging copies. Regression tests re-hash at run
  start to detect drift (`LocalSourceReferenceInvalid`, kind
  `missing_path | hash_drift`).
- `fetch_via_browser` writes `raw_rendered.html` with
  `file_type: rendered_html` and `rendered_state.png` with
  `file_type: rendered_screenshot`. The `dom_hash` primitive then
  verifies its SHA-256 over the rendered HTML matches the raw-cache
  entry's hash, raising `DomHashDivergenceError` (which halts the
  pipeline) on disagreement.

**Raw content for JS-rendered sources is the rendered DOM HTML, not
the initial server response.** Downstream extraction consumes the
post-JS DOM; the pre-JS response is never read by any primitive and
is therefore not cached.

**Per-run caching semantics.** Raw content is cached per Phase 0
invocation. If the same source is extracted twice (e.g. two
different section scopes against the same PDF), the raw content is
cached twice — once in each run-snapshot directory. Deduplication
across runs is deferred future work; not a problem at current
corpus scale.

**Known re-fetch gaps.** When a source cannot be re-fetched and no
preserved raw bytes exist, the manifest sets
`raw_content_unavailable: {value: true, reason: <string>,
first_observed_at: <iso-timestamp>}`. The timestamp lets future
sessions check whether a source has become available again. Two
2026-04-18 gaps are documented:
- Common Core 7.RP — Cloudflare challenge blocks programmatic
  re-fetch.
- NZ Curriculum — the live page returns a bot-detection shell
  rather than curriculum content (fetch succeeds but extraction
  yields zero chars; detected via the empty-hash check in the
  regeneration runner).

**Regression from cache.** `scripts/phase0/regression_from_cache.py`
reads a 0.6.0 manifest, validates source-reference hashes at
start, synthesises a fetch-shaped `PrimitiveResult` from the
cached bytes, and replays the post-fetch primitive sequence. The
canonical outcome is a regenerated `content_hash` byte-identical
with the stored value; drift indicates a regression in the
extraction chain. Report at
`docs/project-log/phase0-cache-regression-2026-04-18.md`.

## Manifest schema (v0.6.0)

Session 4a-4.5 adds `raw_content_files: list[RawContentFile]` and
`raw_content_unavailable: RawContentUnavailable | None`.

- `RawContentFile` — `{path, hash, file_type, bytes}` where
  `file_type` is one of `source_html | source_pdf | rendered_html
  | rendered_screenshot | source_reference`. For cached files,
  `path` is the cache-file path written alongside `content.txt`;
  for `source_reference`, `path` is the original local filesystem
  path (not copied).
- `RawContentUnavailable` — `{value, reason, first_observed_at}`.
  Set on manifests for known-gapped sources so the regression
  utility can report them without running the replay.
- `phase0_version` bumped from `0.5.0` to `0.6.0`.

## Manifest schema (v0.5.0)

Session 4a-4 Step 3a refactored the scope schema into per-source-type
**discriminated unions** bound by ``source_type`` literal (see
``scope.py``). Each variant declares only the fields its primitive
sequence needs; cross-type field smuggling
(e.g. ``page_range`` on a JS-rendered scope) is rejected at
construction time via ``extra="forbid"``. The manifest's
``scope_requested`` field uses Pydantic's discriminator-based
dispatch. A forward-compatible deserialiser upgrades 0.4.0
flat-shaped scope dicts on load by copying the manifest-level
``source_type`` into the scope dict before discriminator parsing —
0.4.0 manifests round-trip byte-stably under 0.5.0.

The 0.4.0 → 0.5.0 regression report
(`docs/diagnostics/2026-04-18-session-4a-4-step-3b-regression-report.md`)
captures field-level evidence that the refactor is behaviour-
preserving. Adversarial tests live in
`tests/phase0/test_scope_schema.py` (18 / 18 passing).

## Manifest schema (v0.4.0 fields, retained in v0.5.0)

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
- `dom_hash` (new in 0.4.0 via Session 4a-3) — SHA-256 of the
  rendered DOM HTML for JS-rendered acquisitions, null for
  PDF / static-HTML acquisitions. Complements `content_hash`: the
  latter tracks extracted text, the former tracks rendered shape.

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

- **Session 4b**: reference test corpus. Per the failure-pattern
  decision recorded after the 4a-3d Ontario diagnosis, every Phase 0
  artefact going forward needs a human-authored reference output to
  validate against. Phase 0 is structurally complete; correctness
  needs reference grounding.
- Session 4a-3.5 (optional): extended multi-source robustness test of
  the browser primitive against additional jurisdictions (Australian
  Curriculum, US state standards). The Welsh hwb Descriptions of
  Learning page (JS-rendered accordion) is a candidate.
- **Scope-aware volume thresholds** so the pipeline's completeness
  check can honour sub-section scopes (KS3 from a five-key-stage
  page; "overall-expectations-only" from a multi-section route)
  without flagging correctly-extracted content below the full-
  document threshold. Caveat hit on Session 4a-3 Ontario DCP and
  Session 4a-4 gov.uk + Wales artefacts.
- Column-aware extraction for dense multi-column pages (per-page
  bounding-box cropping or x-sorted column-band grouping).
- Multi-pathology chained dedup (only when a source with >1
  confirmed pathology is observed in the test corpus).
- Multi-URL aggregation primitive for sites that split sections
  across SPA-routed sub-URLs (Ontario DCP specific-expectations
  use case).
- Multi-source composition: `sources_catalog` data structure for
  pages where multiple authoritative sources at different completeness
  levels exist for the same curriculum reference (deferred to 4b
  per the source-composition design note).
