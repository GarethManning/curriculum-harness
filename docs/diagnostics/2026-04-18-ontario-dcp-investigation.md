# Ontario DCP Grade 7 History — interaction-pattern investigation

Session 4a-3 Step 1. Target URL:
`https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/grades/g7-history/strands`

Investigation script:
`docs/diagnostics/2026-04-18-ontario-dcp-investigation-script.py` (initial
probe) and `2026-04-18-ontario-dcp-probe.py` (DOM dump) and
`2026-04-18-ontario-dcp-subpage-probe.py` (per-expectation sub-page
check). Raw artefacts under
`docs/diagnostics/2026-04-18-ontario-dcp-investigation-artefacts/`.

## Findings (structured)

| Concern | Result |
| --- | --- |
| Initial HTTP status | 200 |
| Consent modal / cookie banner | None detected (probed six common selectors). |
| Framework | Angular Material (`mat-*` custom elements, `ng-*` attributes). No React/Next markers. |
| SPA routing | Yes. Per-expectation URLs follow `/grades/g7-history/{strand}/{code}` pattern (e.g. `/a/a1`, `/b/b3`). Routed client-side via Angular router; initial navigation is a standard GET. |
| Accordion on `/strands` | **None.** No `aria-expanded` buttons in the content area, no `<details>` elements. All six overall-expectation titles and their FOCUS ON tags render inline on the initial `/strands` page. |
| Lazy-load / scroll reveal | Not observed; `networkidle` completes and content is present at that point. |
| Async XHR on interaction | Not applicable — no on-page interaction needed to reveal overall-expectation content. |
| Bot detection | None observed (no Cloudflare challenge, no 403, no rate-limit headers on two sub-page requests). |
| URL-pattern generalisation | `grades/g7-geography/strands` → 200. `grades/g5-history/strands` → 200. Pattern holds. |

## Interaction-pattern classification

**`other`** — specifically: Angular Material SPA, content inline on the
strand-index route, further detail lives on SPA-routed per-expectation
sub-URLs.

None of the original hazards the panel flagged (consent modal, async
XHR on reveal, hostile bot detection) materialised. The tree-navigation
chevrons in the left sidebar are the closest thing to "accordion," and
they operate on the sidebar tree, not on the content area.

## Selectors and scope for the Step 6 test

- `wait_for_selector`: `main` (main content container; present once
  Angular has bootstrapped).
- `extract_selector`: `main` — the `<main>` element's inner text
  contains all six overall-expectation titles with FOCUS ON tags and
  the strand overview text.
- `dismiss_modal_selector`: not needed.
- `click_sequence`: **empty** for the `/strands` route — the six
  overall expectations render without any interaction.

## Content scope trade-off

The `/strands` page produces roughly 4,710 chars of `main.innerText`,
covering:

- Strand A and Strand B headings.
- All six overall-expectation titles (A1, A2, A3, B1, B2, B3).
- FOCUS ON tag text for each overall expectation.
- "Specific Expectations" **headings** with no content beneath them —
  the specific-expectation text lives on per-expectation sub-pages.

Per-sub-page probes (`/a/a1`, `/a/a3`, `/b/b3`) confirm ~4,000–5,500
chars each, so aggregating the six sub-pages would approximate the PDF
volume. The session's `fetch_via_browser` primitive is designed for a
single URL with optional click choreography. Multi-URL aggregation is
therefore **out of scope for this session** and a future session can
add a multi-URL follow primitive if the specific-expectations content
is needed.

For this session's cross-validation claims:

- Check B (six overall-expectation title match against 4a-2b's PDF
  extraction): achievable from `/strands` alone.
- Check B2 (FOCUS ON tag match): achievable from `/strands` alone.
- Check C (volume sanity 5,000–50,000 chars): will flag or fail at
  ~4,710 chars. This is a **scope caveat**, not an extraction bug —
  the DCP `/strands` route is inherently lighter than the full PDF
  strand chapter. Either accept the pass-with-notes classification (as
  4a-2b did when Check C miscalibrated high) or relax Check C for this
  specific scope. Recommendation: document as pass-with-notes and leave
  the threshold as-is.

## Bot-detection taxonomy (forward-looking, for primitive design)

Based on this investigation, the primitive should surface the following
distinct failure modes to the user-in-the-loop protocol rather than
retrying silently:

- HTTP 403 on initial navigation.
- `cloudflare` or `verify you are human` text appearing on the first
  render.
- 429 response or `Retry-After` header indicating rate-limiting.

None of these fired for Ontario DCP. The primitive should still handle
them generically so NZ Curriculum and future targets benefit.

## What's SAME across Ontario DCP and "typical curriculum sites"

Angular Material is a mainstream framework and this SPA pattern
generalises. Many Canadian-province and US-state curriculum sites use
similar React/Angular SPA patterns with content-revealing via routing,
accordions, or tabs. The primitive's `click_sequence` scope field is
forward-compatible with accordion / tab sites even though Ontario's
`/strands` does not exercise it.
