# Session 4a-4 Step 8 — UK gov.uk National Curriculum (England) Mathematics KS3

**Date:** 2026-04-18
**Source URL:** https://www.gov.uk/government/publications/national-curriculum-in-england-mathematics-programmes-of-study/national-curriculum-in-england-mathematics-programmes-of-study
**Source type:** `html_nested_dom`
**Primitive sequence:** `fetch_requests → encoding_detection → extract_nested_dom → verify_raw_extraction → normalise_whitespace → verify_normalised_extraction → content_hash`
**Investigation memo:** `docs/diagnostics/2026-04-18-gov-uk-nc-maths-ks3-investigation.md`

## Outcome — PASS WITH NOTES

Triangulated verification all green; verify primitive surfaced a
known-calibration `suspicious` verdict on the completeness check
(sub-section-scoped extraction below the document-wide volume
threshold).

| Check                                | Result          | Notes                                                                                                |
| ------------------------------------ | --------------- | ---------------------------------------------------------------------------------------------------- |
| A — structural strands present       | STRONG PASS     | All 11 strands present (3 Working-mathematically + 6 Subject-content + Introduction + Subject-content header). |
| B — chrome exclusion (reason-based)  | STRONG PASS     | Zero leakage from the 13-item gov.uk chrome list catalogued in Step 1's investigation memo.          |
| C — volume sanity (3 000–20 000)     | PASS (12 461)   | Inside the calibrated range from the investigation memo.                                             |
| Pipeline `verify_raw_extraction`     | `clean`         | whitespace_runs check passed.                                                                        |
| Pipeline `verify_normalised_extraction` | `suspicious` | completeness check flagged: 12 461 / 302 525 = 4.12 % vs 5 % threshold. **Calibration issue, not a content issue.** |

## Architecture: heading-anchor scoping

The KS3 region is interleaved with KS1, KS2 and KS4 inside the single
`.govspeak` container — there is no dedicated KS3 sub-container, so
container-CSS scoping is not applicable. The
`section_anchor_selector` mechanism (Step 4 design, picked up here
for the first time) takes the `<h2 id="key-stage-3">` anchor and walks
following siblings until the next `<h2>` (default stop tag = anchor
tag). This is the new scoping mechanism the `extract_nested_dom`
primitive added beyond the simple container-CSS pattern; this
artefact is its first production validation.

## Architectural generalisation note

This is the primary test for the `extract_nested_dom` primitive's
generalisation claim (Session 4a-4). Step 9 runs the **same primitive
with scope-only differences** on a structurally-distinct second
source (Welsh hwb.gov.wales — `single_main_container` shape, no
section anchor needed, in-container chrome stripping needed). If both
Step 8 and Step 9 pass with no per-site primitive branching, the
architecture is validated and Phase 0 is complete.

## Known calibration caveat — completeness check

The pipeline's completeness check is calibrated to a "full document"
expectation (chars_total / fetched_bytes ≥ 5 %). Sub-section
extractions — like KS3 alone from a five-key-stage page — naturally
fall below this ratio. Same issue called out in the Ontario DCP
artefact (Session 4a-3) and tracked in the Phase 0 README's
"Scheduled (next sessions)" list:

> Scope-aware volume thresholds so Check C in triangulated
> verification can honour "overall-expectations-only" scopes without
> flagging correctly-extracted content below the full-document
> threshold (Session 4a-3 Step 6 caveat).

The triangulated verification (Check A + B + C) is the authoritative
quality signal for sub-section runs until the verify primitive
becomes scope-aware.

## Files

- `manifest.json` — acquisition manifest (schema 0.5.0)
- `content.txt` — extracted text (12 461 chars, UTF-8)
- `_detection.json` — type detector output (with override applied)
