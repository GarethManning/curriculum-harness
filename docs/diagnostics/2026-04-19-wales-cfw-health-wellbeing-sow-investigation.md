# Welsh Curriculum for Wales — Health and Well-being "Statements of what matters" — interaction-pattern investigation

**Date:** 2026-04-19
**Session:** 4a-5 Step 2
**Source URL:** https://hwb.gov.wales/curriculum-for-wales/health-and-well-being/statements-of-what-matters/
**Fetched bytes:** 122,003 (raw HTML)
**Saved at:** `/tmp/wales-hwb-sow.html` (transient)

Parallels Session 4a-4 Step 9 (Welsh Maths SoW) one-to-one: same CMS,
same container selector, same chrome patterns. This memo records that
the structural equivalence holds so the run can reuse the Step 9
extraction primitive unchanged with only scope-level differences.

## 1. Container distribution

Single main content container. The page is exactly one Area of Learning
and Experience sub-section (Health and Well-being → Statements of what
matters). Body is five `<h3>` mandatory statements as siblings under the
content `<div class="grid">` block.

CSS selector chain (deepest content container):

```
html > body.frontpage > div.main-wrapper
  > main#main-content.content > article#aole-v2
  > div.aole-v2-content
```

Depth from document root to `main`: **5 levels** (identical to Welsh
Maths SoW).

Selector that uniquely picks the content root: `article#aole-v2`.

## 2. Chrome elements (comprehensive exclusion list)

Chrome outside `main#main-content` is excluded by construction. Chrome
inside `article#aole-v2 > div.aole-v2-content` must be excluded
explicitly — matches Welsh Maths SoW's chrome list one-to-one:

| Selector            | Purpose                              | Inside `article#aole-v2`? | Verified inside probe |
| ------------------- | ------------------------------------ | ------------------------- | --------------------- |
| `header`            | Site header                          | no                        | outside=1, inside=0   |
| `footer`            | Site footer                          | no                        | outside=1, inside=0   |
| `.menu`             | Menu drawer                          | no                        | outside=1, inside=0   |
| `.search`           | Search affordance                    | no                        | outside=1, inside=0   |
| `.cookie-block`     | Cookie consent (3 instances)         | no                        | outside=3, inside=0   |
| `.skip-link`        | Skip-to-content link                 | no                        | outside=1, inside=0   |
| `.pagefooter`       | Page footer block                    | no                        | outside=1, inside=0   |
| `.breadcrumb`       | Breadcrumb trail                     | no (but kept for parity)  | outside=1, inside=0   |
| `nav`               | In-page contents nav (`nav.grid`)    | **yes** — must exclude    | inside=1              |
| `.tab-next-prev`    | Prev/next navigation                 | **yes** — must exclude    | inside=1              |
| `.explore-links`    | "More areas of learning" footer block| **yes** — must exclude    | inside=1              |
| `.contents`         | Generic contents-list class          | (outside=3, inside=0; kept for parity) |        |

Verified inside-article headings mapped to the chrome containers:

- `h2 "Contents"` lives inside `nav.grid < div.aole-v2-content` — stripped
  via the `nav` selector.
- `h2 "More areas of learning and experience"` lives inside
  `.explore-links` — stripped via `.explore-links`.
- `h2 "2. Statements of what matters"` and `h2 "Mandatory"` are content;
  preserved.

Exclude list carried verbatim from Welsh Maths SoW:

```python
exclude_selectors = ["nav", ".tab-next-prev", ".explore-links",
                     ".contents", ".cookie-block", ".breadcrumb"]
```

After strip: article body reduces from 4,974 chars (uncleaned) to
4,644 chars (content-only).

## 3. Section scoping

**No section scoping needed.** One Welsh AoLE sub-page = one section.
The Health and Well-being SoW page is exclusively the SoW content — not
interleaved with other AoLEs and not containing sub-sections. Principles
of progression and Descriptions of learning live on separate URLs per
the prev/next navigation.

`section_anchor_selector` and `section_scope_selector` are both unset.
The whole `article#aole-v2` minus in-page chrome is the target.

## 4. Internal structure

Headings on the SoW page (in document order, scoped to `article#aole-v2`,
content-only):

```
h1                  "AREA OF LEARNING AND EXPERIENCE — Health and Well-being"
  div.aole-v2-content > div.grid.typography:
    h2              "2. Statements of what matters"
  div.aole-v2-content > div.grid:
    h2              "Mandatory"
    h3 (statement 1)  "Developing physical health and well-being has lifelong benefits."
    h3 (statement 2)  "How we process and respond to our experiences affects our
                       mental health and emotional well-being."
    h3 (statement 3)  "Our decision-making impacts on the quality of our lives and
                       the lives of others."
    h3 (statement 4)  "How we engage with social influences shapes who we are and
                       affects our health and well-being."
    h3 (statement 5)  "Healthy relationships are fundamental to our well-being."
```

Five `<h3>` mandatory statements are the load-bearing content. Each
statement is followed by 2–4 explanatory paragraphs. Step 4 Check A
asserts all five statement titles are present in the extracted text.

## 5. `<details>` elements

**Zero `<details>` elements** on this page. Collapsible content on the
hwb CMS lives on the JS-rendered **Descriptions of learning** page
(`<div class="c-block dol accordion">`) — out of scope.
`include_details_content=True` is the default and is inert for this
source.

## 6. Volume estimate

`article#aole-v2` uncleaned: 4,974 chars. After chrome strip: 4,644
chars. Expected extracted volume: ~4,500–4,700 chars. Check C threshold
calibrated 3,000–6,500 chars (slightly wider than Welsh Maths SoW's
2,500–6,000 to reflect the one additional statement and longer
explanatory paragraphs).

## 7. Interaction-pattern classification

**Classification:** `single_main_container`.

Identical to Welsh Maths SoW (Session 4a-4 Step 9). One
CSS-selectable container holds the entire scope; no sub-section
anchoring; the only complication is in-container chrome that must be
excluded explicitly.

Same primitive (`extract_nested_dom`) should handle this source with
**scope-only differences** from the Welsh Maths SoW run — in fact, the
scope is structurally isomorphic: same `content_root_selector`, same
`exclude_selectors` list, only the URL differs. If the primitive needs
code changes to handle this source, the architecture is wrong.

## 8. Scope spec sketch (for Step 3)

```jsonc
{
  "source_type": "html_nested_dom",
  "url": "https://hwb.gov.wales/curriculum-for-wales/health-and-well-being/statements-of-what-matters/",
  "content_root_selector": "article#aole-v2",
  "exclude_selectors": [
    "nav", ".tab-next-prev", ".explore-links",
    ".contents", ".cookie-block", ".breadcrumb"
  ],
  "include_details_content": true,
  "preserve_headings": true
}
```

## 9. No deferred-primitive-work finding

The primitive sequence for `html_nested_dom` (Session 4a-4) handles
this source with no code modifications. The pre-flight scan + this
structural investigation confirm: scope-only differences from the
Welsh Maths run. Proceed to Step 3.
