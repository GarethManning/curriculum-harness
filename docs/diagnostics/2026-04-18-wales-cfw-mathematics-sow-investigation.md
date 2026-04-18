# Welsh Curriculum for Wales — Mathematics & Numeracy "Statements of What Matters" — interaction-pattern investigation

**Date:** 2026-04-18
**Session:** 4a-4 Step 2 (secondary nested-DOM source)
**Source URL:** https://hwb.gov.wales/curriculum-for-wales/mathematics-and-numeracy/statements-of-what-matters/
**Fetched bytes:** 121,028 (raw HTML)
**Saved at:** `/tmp/wales-sow.html` (transient)

## Verification before investigation (Step 2 v2 guards)

The session prompt's three primary candidates each failed pre-checks:

- **Scottish Curriculum for Excellence (Education Scotland)**:
  HTTP 200 on the index page, but the actual experiences-and-outcomes
  content is published as **PDFs linked from an HTML index**
  (e.g. "Numeracy and mathematics (PDF, 457 KB)"). The HTML page itself
  carries only navigation. Fails the "real HTTP-fetchable HTML page
  with content" guard.
- **Singapore MOE** (`https://www.moe.gov.sg/education-in-sg/our-programmes/teach-lead`):
  Returned **HTTP 403** with a "Something's wrong" challenge page —
  bot detection. Fails accessibility guard.
- **California Department of Education content standards**
  (`https://www.cde.ca.gov/be/st/ss/`): Server immediately returns
  **HTTP 303 redirect to `/wafalert.html`** (Radware WAF block). Fails
  accessibility guard.

Per the session rule "do not fall back to another source type," the
fallback chosen is another **nested-DOM HTML curriculum source**, not
PDF or JS-rendered. After ruling out Welsh hwb's
**Descriptions of Learning** page (a JS-rendered accordion — `<div
class="c-block dol accordion">` elements have zero static text), the
**Mathematics and Numeracy "Statements of what matters"** page on the
same hwb platform was confirmed accessible with all content rendered
server-side.

Architectural distinctness from gov.uk: hwb.gov.wales runs on a
custom CMS platform (not GOV.UK Publishing); chrome conventions,
container structure, and layout selectors are entirely different
(see §2 and §3).

## 1. Container distribution

Single main content container per AoLE page. The page is one
"Area of Learning and Experience" sub-section (Mathematics and
Numeracy → Statements of what matters); the body of the page is the
four mandatory mathematics statements as `<h3>` siblings under a
`<div class="grid">` block.

CSS selector chain (deepest content container):

```
html > body.frontpage > div.main-wrapper
  > main#main-content > article#aole-v2
  > div.aole-v2-content > div.grid (the third-position content grid)
```

Depth from document root to `main`: **5 levels** (gov.uk: 10).
Depth to `article#aole-v2`: 6 levels.

Selector that uniquely picks the content root: `article#aole-v2`.

## 2. Chrome elements (comprehensive exclusion list)

hwb's chrome lives **outside** `main#main-content` for site-level
chrome (header, footer, cookie banner, search) but **inside**
`article#aole-v2 > div.aole-v2-content` for in-page chrome
(contents nav, prev/next, "more areas of learning"). The latter
must be excluded explicitly.

| Selector                                   | Purpose                              | Inside `article#aole-v2`? |
| ------------------------------------------ | ------------------------------------ | ------------------------- |
| `header`                                   | Site header / Hwb branding           | no                        |
| `footer`                                   | Site footer                          | no                        |
| `nav` (top-level)                          | Site navigation                      | no                        |
| `.menu`                                    | Menu drawer                          | no                        |
| `.search`                                  | Search affordance                    | no                        |
| `.cookie-block`                            | Cookie consent (3 instances on page) | no                        |
| `.skip-link`                               | Skip-to-content link                 | no                        |
| `.breadcrumb`                              | Breadcrumb trail                     | no                        |
| `nav.grid` (inside `.aole-v2-content`)     | In-page contents list                | **yes** — must exclude    |
| `.tab-next-prev`                           | Prev/next page navigation            | **yes** — must exclude    |
| `.explore-links`                           | "More areas of learning" footer block| **yes** — must exclude    |
| `.contents`                                | Generic contents-list class          | **yes** — must exclude    |
| `.pagefooter`                              | Page footer block                    | sibling of article        |

Conservative posture: over-exclude rather than under-exclude. The
exclude-selector list for the primitive scope is:

```python
exclude_selectors = ["nav", ".tab-next-prev", ".explore-links", ".contents",
                     ".cookie-block", ".breadcrumb"]
```

(Targeted at the article subtree; site-level chrome is already outside
the content root and so excluded by construction.)

## 3. Section scoping

**No section scoping needed.** One Welsh AoLE sub-page = one section.
The Mathematics SoW page is exclusively the SoW content — not
interleaved with other AoLEs and not containing other sub-sections
(the other Welsh sub-sections — Principles of progression, Descriptions
of learning — live on **separate URLs** per the prev/next navigation,
not on this same page).

`section_anchor_selector` and `section_scope_selector` are both unset
for this scope. The whole `article#aole-v2` minus its in-page chrome
is the target.

## 4. Internal structure

Headings on the SoW page (in document order, scoped to `article#aole-v2`):

```
h1                                "AREA OF LEARNING AND EXPERIENCE — Mathematics and Numeracy"
  div.aole-v2-content > div.grid.typography:
    h2                            "2. Statements of what matters"
  div.aole-v2-content > div.grid:
    h2                            "Mandatory"
    h3 (statement 1)              "The number system is used to represent and compare relationships
                                   between numbers and quantities."
    h3 (statement 2)              "Algebra uses symbol systems to express the structure of mathematical
                                   relationships."
    h3 (statement 3)              "Geometry focuses on relationships involving shape, space and
                                   position, and measurement focuses on quantifying phenomena in the
                                   physical world."
    h3 (statement 4)              "Statistics represent data, probability models chance, and both
                                   support informed inferences and decisions."
```

The four `<h3>` mandatory statements are the load-bearing content. Each
statement is followed by an explanatory paragraph and a "find out more"
descriptor. Step 9 Check A asserts all four statement titles are
present in the extracted text.

## 5. `<details>` elements

**Zero `<details>` elements** on this page. The hwb CMS uses
`<div class="c-block ... accordion">` divs for collapsible content
(observed on the **Descriptions of learning** page); the SoW page has no
collapsibles. The primitive's `include_details_content` flag is
relevant for forward compatibility but does not affect this source.

## 6. Volume estimate

`article#aole-v2`: ~4,072 chars total. With chrome excluded
(`nav`, `.tab-next-prev`, `.explore-links`, `.contents`), expected
extracted volume: **~3,500–3,800 chars** (the four statements +
their explanatory paragraphs). Step 9 Check C threshold is calibrated
to this scope: 2,500–6,000 chars. (Notably tighter than gov.uk KS3's
3,000–20,000 because Welsh SoW is structurally compact by design.)

## 7. Interaction-pattern classification

**Classification:** `single_main_container`.

Rationale: one CSS-selectable container holds the entire scope; no
sub-section anchoring is needed; the only complication is in-container
chrome (in-page nav and explore-links blocks) that must be excluded
explicitly.

This is **distinct from gov.uk KS3's `hierarchical_with_scope`
classification.** The structural-difference check passes:

| Property                                | gov.uk KS3 (Step 1)                | Wales SoW (this memo)                       |
| --------------------------------------- | ---------------------------------- | ------------------------------------------- |
| Site platform                           | GOV.UK Publishing (rebranded)      | hwb.gov.wales custom CMS                    |
| Depth to content container              | 10 levels                          | 5 levels                                    |
| Content container selector              | `.govspeak`                        | `article#aole-v2`                           |
| Scoping mechanism needed                | heading-anchor (`#key-stage-3`)    | none — one URL per scope                    |
| Chrome inside content container         | none                               | nav, prev/next, explore-links               |
| `<details>` elements                    | zero                               | zero (collapsibles use `div.accordion`)     |
| Interaction-pattern classification      | `hierarchical_with_scope`          | `single_main_container`                     |

These are meaningfully distinct classifications: one demands
heading-anchor scoping discipline; the other demands in-container
chrome stripping. The same primitive should handle both with
**scope-level differences only** — that is the architectural
generalisation Step 9 verifies.

## 8. Scope spec sketch (for Step 4 use)

```jsonc
{
  "source_type": "html_nested_dom",
  "url": "https://hwb.gov.wales/curriculum-for-wales/mathematics-and-numeracy/statements-of-what-matters/",
  "content_root_selector": "article#aole-v2",
  "exclude_selectors": [
    "nav", ".tab-next-prev", ".explore-links",
    ".contents", ".cookie-block", ".breadcrumb"
  ],
  // No section scoping: one URL = one section
  "include_details_content": true,
  "preserve_headings": true
}
```

## 9. Open questions / risks for Step 8/9

- The hwb CMS publishes **Descriptions of learning** as a JS-rendered
  accordion. If the Welsh curriculum's full progression descriptions
  are needed downstream, that page belongs in a future
  `js_rendered_progressive_disclosure` extraction — out of scope for
  this nested-DOM session.
- The Welsh SoW page is compact (~3.5K chars). Step 9's Check C
  volume range is calibrated tighter (2,500–6,000) than Step 8's
  (3,000–20,000) to reflect this. The design intent of Welsh SoW is
  itself short and pithy; the volume bounds reflect the source's
  conventions, not extraction completeness.
- The structural-difference check passes: distinct site platforms,
  distinct depth, distinct scoping discipline, distinct chrome
  patterns, distinct interaction-pattern classifications.

## 10. Why not the documented v2 candidates

For audit clarity:

- **Scottish CfE**: PDF-published content; HTML index only. Wrong
  source type for a nested-DOM test.
- **Singapore MOE**: 403 / bot challenge. Cannot acquire deterministically.
- **California CDE**: WAF redirect (Radware) on plain `curl` and
  Chrome-UA `curl`. Cannot acquire without browser automation, and
  the target standards pages are themselves PDFs even when the index
  loads.
- **Welsh hwb (chosen)**: HTTP 200, content rendered server-side,
  custom-CMS chrome distinct from GOV.UK Publishing chrome,
  classification distinct from Step 1's. Satisfies all v2 guards
  except being on the prompt's named list — flagged here for
  explicit user awareness.
