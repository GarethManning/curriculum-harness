# Session 4a-4 Step 9 — Welsh hwb Curriculum for Wales Mathematics & Numeracy "Statements of what matters"

**Date:** 2026-04-18
**Source URL:** https://hwb.gov.wales/curriculum-for-wales/mathematics-and-numeracy/statements-of-what-matters/
**Source type:** `html_nested_dom`
**Primitive sequence:** `fetch_requests → encoding_detection → extract_nested_dom → verify_raw_extraction → normalise_whitespace → verify_normalised_extraction → content_hash`
**Investigation memo:** `docs/diagnostics/2026-04-18-wales-cfw-mathematics-sow-investigation.md`

## Outcome — PASS WITH NOTES (architecture validated)

Triangulated verification all green; verify primitive surfaced the
same `suspicious` completeness-check verdict as the gov.uk artefact
(sub-section-scoped extraction below the document-wide volume
threshold).

| Check                                | Result          | Notes                                                                                       |
| ------------------------------------ | --------------- | ------------------------------------------------------------------------------------------- |
| A — four mandatory statements        | STRONG PASS     | All four mandatory mathematics statements present verbatim.                                  |
| B — chrome exclusion (reason-based)  | STRONG PASS     | Zero leakage from the 11-item hwb chrome list catalogued in Step 2's investigation memo.     |
| C — volume sanity (2 500–6 000)      | PASS (3 792)    | Inside the calibrated range from the investigation memo.                                     |
| Pipeline `verify_raw_extraction`     | `clean`         | whitespace_runs check passed.                                                                |
| Pipeline `verify_normalised_extraction` | `suspicious` | completeness check flagged: 3 792 / 121 028 = 3.13 % vs 5 % threshold. Same calibration caveat as Step 8 (gov.uk) and Session 4a-3 Ontario DCP. |

## Architectural generalisation — VALIDATED

This is the central architectural claim of Session 4a-4.

| Property                                    | Step 8 (gov.uk KS3)                  | Step 9 (Wales SoW)                                                |
| ------------------------------------------- | ------------------------------------ | ----------------------------------------------------------------- |
| Primitive used                              | `extract_nested_dom`                 | `extract_nested_dom` (**same primitive, no code branching**)       |
| `content_root_selector`                     | `.govspeak`                          | `article#aole-v2`                                                  |
| Section scoping mechanism                   | `section_anchor_selector="#key-stage-3"` (heading-anchor) | none — single URL = single section                                 |
| `exclude_selectors`                         | empty (chrome lives outside `.govspeak`) | `["nav", ".tab-next-prev", ".explore-links", ".contents", ".cookie-block", ".breadcrumb"]` (6 items) |
| Interaction-pattern classification           | `hierarchical_with_scope`            | `single_main_container`                                            |
| Site platform                               | GOV.UK Publishing                    | hwb.gov.wales custom CMS                                           |
| Container depth (root → content)            | 10 levels                            | 5 levels                                                           |
| Result                                      | STRONG PASS on A/B/C                 | STRONG PASS on A/B/C                                               |

**The same primitive code handled both sources with scope-level
differences only.** No branching, no per-site override path, no
"if site == ..." conditional. The architectural claim that
nested-DOM extraction is a *capability* (not a per-site solution)
is validated.

## Architectural verdict

**Architecture validated.** Same primitive, two structurally-distinct
sources (different platforms, different container depths, different
scoping disciplines, different chrome patterns), scope-level
differences only. Phase 0 source-type coverage (5 of 5) is complete.

## Files

- `manifest.json` — acquisition manifest (schema 0.5.0)
- `content.txt` — extracted text (3 792 chars, UTF-8)
- `_detection.json` — type detector output (with override applied)
