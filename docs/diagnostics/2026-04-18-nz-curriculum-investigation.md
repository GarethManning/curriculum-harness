# New Zealand Curriculum Online (Social Sciences Y4–6) — interaction-pattern investigation

Session 4a-3 Step 2. Target URL:
`https://newzealandcurriculum.tahurangi.education.govt.nz/new-zealand-curriculum-online/nzc---social-sciences-years-4---6/5637290852.p`

Investigation script:
`docs/diagnostics/2026-04-18-nz-curriculum-investigation-script.py`.
Raw artefacts under
`docs/diagnostics/2026-04-18-nz-curriculum-investigation-artefacts/`.

Target selected as the rough age-match to Ontario Grade 7 (Years 4–6
= roughly ages 8–11; Ontario Grade 7 = age 12). Close enough to exercise
a structurally different curriculum organisation against the same
primitive.

## Findings (structured)

| Concern | Result |
| --- | --- |
| Initial HTTP status | 200 |
| Consent modal | **Present.** `button[aria-label*='cookie' i]` is visible on first render. Dismiss required before extraction to keep rendered-state snapshots free of the banner. |
| Framework | No React / Next / Nuxt / Angular markers. Heavy custom CMS (Sitecore-/Dynamics-style; `ms-*`, `moe-*` class prefixes). 78 scripts on the page. Content itself is server-rendered into `main` on first load. |
| SPA routing | None observed — URL does not change on in-page interaction. Internal navigation is page-load. |
| Accordion on content | **None.** The only `aria-expanded` buttons are top-nav menu buttons; content does not sit behind toggles. |
| Lazy-load / scroll reveal | Not observed; all four strands present in `main` on initial `networkidle`. |
| Async XHR on interaction | Not applicable — no content-revealing interaction needed. |
| Bot detection | None detected. |
| Main content volume | `main.innerText` = **38,641 chars** covering all four strands (History, Civics and Society, Geography, Economic Activity) with Knowledge/Practices × Year 4/5/6 columns. |
| Sibling URL (`/social-sciences-1-10/5637208398.p`) | 200. URL-pattern stable. |
| Console errors | Three non-fatal (style MIME, resolver failure on a third-party CDN, DOM target warning). None blocks content render. |

## Interaction-pattern classification

**`other`** — specifically: heavily scripted page with content
server-rendered into `main` on first load. Closest behavioural analogue
to a static HTML page, even though the page ships 78 scripts and
classifies as JS-rendered on cursory inspection.

## Selectors and scope for the Step 7 test

- `wait_for_selector`: `main`.
- `dismiss_modal_selector`: `button[aria-label*='cookie' i]`.
- `extract_selector`: `main`.
- `click_sequence`: **empty** — same as Ontario DCP, for a different
  reason (Ontario ships content inline on the strand-index route; NZ
  ships the full levels-4–6 curriculum inline).

## What's SAME across Ontario DCP and NZ Curriculum

- Both ministry-authoritative, both English-language.
- Both technically JS-rendered (Ontario Angular SPA; NZ heavy custom
  CMS with 78 scripts) but both render their target content into
  `main` on `networkidle`, **without requiring a click sequence**.
- Both respond well to a vanilla Playwright headless fetch with a
  fixed-viewport user-agent.
- Neither shows Cloudflare / verify-human challenges.

## What's DIFFERENT

- **Curriculum organisation.** Ontario: grade-based (Grade 7 History
  strand with Strands A and B, each with three overall expectations
  A1/A2/A3 and B1/B2/B3). NZ: levels-based (Phase 2 = Years 4–6), with
  four conceptual strands (History, Civics and Society, Geography,
  Economic Activity), each organised as Knowledge + Practices.
- **Granularity.** Ontario's overall-expectations route is one page
  (`/strands`), with specific expectations on sub-pages. NZ ships the
  full phase content on a single page.
- **Consent modal.** NZ has one; Ontario does not. The primitive must
  support an optional `dismiss_modal_selector` field, exercised on NZ
  and unused on Ontario — exactly the kind of scope-level difference
  the architecture calls for.
- **Content volume on the target URL.** Ontario `/strands` ≈ 4,700
  chars (overall expectations only). NZ Phase 2 ≈ 38,600 chars (full
  phase curriculum). Same primitive, same `extract_selector=main`.

## Primitive-architecture implications

The same `fetch_via_browser` primitive should handle both sites with
scope-level differences only:

| Scope field | Ontario DCP | NZ Curriculum |
| --- | --- | --- |
| `url` | `.../g7-history/strands` | `.../5637290852.p` |
| `wait_for_selector` | `main` | `main` |
| `dismiss_modal_selector` | (omitted) | `button[aria-label*='cookie' i]` |
| `click_sequence` | (omitted) | (omitted) |
| `extract_selector` | `main` | `main` |
| `timeout_ms` | default (30000) | default (30000) |

If any of these require the primitive to contain `if site == ...`
branching, the architecture is wrong and Step 3 must refactor until
the primitive is pure capability.
