# Session 4a-3 Step 7 — NZ Curriculum Online, Social Sciences Phase 2

- **Source:** `https://newzealandcurriculum.tahurangi.education.govt.nz/new-zealand-curriculum-online/nzc---social-sciences-years-4---6/5637290852.p`
- **Source type:** `js_rendered_progressive_disclosure`
- **Schema version:** 0.4.0
- **Run date:** 2026-04-18
- **Runner:** `scripts/phase0/run_nz_curriculum.py`

## Purpose — the generalisation test

This run tests whether the `fetch_via_browser` primitive handles a
structurally different JS-heavy curriculum site **with scope-level
differences only** — no code changes to the primitive. If the primitive
would have required `if site == ...` branching, the architectural
claim behind Session 4a-3 fails. It did not.

## Primitive sequence

`fetch_via_browser → dom_hash → extract_css_selector → verify_raw_extraction → normalise_whitespace → verify_normalised_extraction → content_hash`

Identical to the Ontario DCP run. No branching.

## Scope difference from Ontario DCP

| Scope field | Ontario DCP | NZ Curriculum |
| --- | --- | --- |
| `url` | `…/g7-history/strands` | `…/5637290852.p` |
| `wait_for_selector` | `main` | `main` |
| `dismiss_modal_selector` | (omitted) | `button[aria-label*='cookie' i]` |
| `click_sequence` | (omitted) | (omitted) |
| `css_selector` | `main` | `main` |
| `browser_timeout_ms` | 60000 | 60000 |

One additional optional scope field (`dismiss_modal_selector`). That
is the whole difference.

## Hashes

- `content_hash`: `a01e288c63d217fb4f3fcf8e8e49294e9f9a176a416fd36e143717b861b8e44a`
- `dom_hash`: `2669189a4f2679d92de6aa5cfc5ad623359e71373821240297111b04fb131d45`

## Verification verdicts

Both automated passes `clean`. Fetch summary: HTTP 200,
`modal_dismissed: false` (the consent banner was not visible at
extraction time — it may be shown only to cookie-persistent sessions
or triggered after scroll; the primitive's advisory behaviour correctly
continued without failing), `click_count: 0`, 2 benign console errors
(third-party stylesheet MIME and CDN resolver warnings).

## Structural verification (Check A)

NZ Phase 2 curriculum has four strands instead of Ontario's two;
Knowledge + Practices substructure rather than overall-expectations +
specific-expectations.

- **History** strand: present.
- **Civics and Society** strand: present.
- **Geography** strand: present.
- **Economic Activity** strand: present.
- **Knowledge** sub-headings: 4 (one per strand).
- **Practices** sub-headings: 4 (one per strand).

**Verdict: PASS.**

## Volume sanity (Check C)

- Extracted content: **37,245 chars**.
- Threshold: 5,000–50,000 chars.
- Outcome: **pass.** This site ships the whole Phase 2 curriculum on
  one URL, which places it comfortably inside the band.

## Cross-validation

No PDF ground truth is available for direct title match, so the
comparison against PDF columns used in the Ontario DCP test does not
apply here. The spot check + structural + volume combination, plus
manual inspection of headings, is the evidence that extraction is
correct. Spot check: `spot-check.txt`.

## Architectural verdict

**Architecture validated.**

The same `fetch_via_browser` primitive handled Ontario DCP (Angular
Material SPA, no consent modal, content inline at /strands) and NZ
Curriculum (heavy custom CMS, consent modal, content inline with
four strands × Knowledge/Practices) without code changes. Only scope
configuration differed — exactly one extra optional field. This is
the session's central architectural claim, and it holds.

## Files

- `manifest.json`
- `content.txt`
- `rendered_state.png`
- `_detection.json`
- `spot-check.txt`
- `README.md`

## Notes on fallback-preference ordering (from the session plan)

NZ Curriculum was the primary secondary-source candidate and did not
require falling back to Singapore MOE or Australian Curriculum. The URL
was verified accessible, JS-rendered, and structurally different from
Ontario — the three criteria the session plan required for the
generalisation test to be meaningful.
