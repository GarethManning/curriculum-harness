# UK gov.uk National Curriculum (Mathematics, Key Stage 3) — interaction-pattern investigation

**Date:** 2026-04-18
**Session:** 4a-4 Step 1
**Source URL:** https://www.gov.uk/government/publications/national-curriculum-in-england-mathematics-programmes-of-study/national-curriculum-in-england-mathematics-programmes-of-study
**Fetched bytes:** 302,525 (raw HTML)
**Saved at:** `/tmp/gov-uk-nc-maths.html` (transient)

## 1. Container distribution

Single main content container. All key-stage content (KS1 through KS4) lives
inside one `<div class="govspeak">` element. Subject-content strands and
year-group programmes are flat children of that single container.

CSS selector chain (deepest content container):

```
html.govuk-template > body.gem-c-layout-for-public > div.govuk-width-container
  > main#content > div#contents
  > div.govuk-grid-row > div.govuk-grid-column-three-quarters-from-desktop.contents-container
  > div.gem-c-govspeak-html-publication > div.gem-c-govspeak.govuk-govspeak
  > div.govspeak
```

Depth from document root to `.govspeak`: 10 levels.

Selector that uniquely picks the content root: `.govspeak` (or
`main#content .govspeak` for defence-in-depth).

## 2. Chrome elements (comprehensive exclusion list)

All gov.uk site chrome lives **outside** `.govspeak`, so scoping to
`.govspeak` already excludes the chrome list below. The list is recorded
defensively for use as `exclude_selectors` and so the verification check
in Step 8 has a concrete reason-based reference rather than ad-hoc
regex assertions.

| Selector                                                  | Purpose                          | Inside .govspeak? |
| --------------------------------------------------------- | -------------------------------- | ----------------- |
| `.govuk-skip-link`                                        | "Skip to main content" link      | no                |
| `.govuk-cookie-banner`                                    | Cookie consent banner            | no                |
| `header`, `.gem-c-layout-super-navigation-header`         | Site header / GOV.UK branding    | no                |
| `.govuk-phase-banner`                                     | Beta / alpha phase banner        | no                |
| `.govuk-breadcrumbs`                                      | Breadcrumb navigation            | no                |
| `.gem-c-devolved-nations`                                 | "Applies to England" notice      | no                |
| `nav.gem-c-contents-list`, `.gem-c-contents-list`         | Sidebar / inline contents list   | no                |
| `.gem-c-print-link`                                       | "Print this page" affordance     | no                |
| `.gem-c-feedback`                                         | "Is this page useful?" form      | no                |
| `.gem-c-share-links`                                      | Social-share buttons             | no                |
| `.gem-c-related-navigation`, `aside`, `.app-c-side-bar`   | Related-content sidebars         | no                |
| `footer`, `.govuk-footer`                                 | Site footer                      | no                |
| `noscript`                                                | Noscript fallback                | no                |
| `.govuk-visually-hidden`                                  | Screen-reader-only spans         | mixed (advisory)  |
| `script`, `style`                                         | Behaviour / styling tags         | no (default)      |

`.govuk-visually-hidden` may appear inside content blocks for screen-reader
labelling. Conservative posture: **do not** strip it from the content
root by default (it can carry semantic content); strip it only when
empirically observed to leak into extracted text.

## 3. KS3 scoping

The KS3 section is **interleaved with KS1, KS2 and KS4** as `<h2>`
siblings inside `.govspeak`. There is no dedicated KS3 sub-container.

The KS3 region is bounded by:

- Start: `<h2 id="key-stage-3">Key stage 3</h2>`
- End: the next sibling `<h2>` (`<h2 id="key-stage-4">Key stage 4</h2>`)

CSS alone cannot express "everything between this h2 and the next h2"
as a single selector. Two viable mechanisms:

- **Heading-anchor scoping** (chosen). Anchor selector `#key-stage-3`
  picks the start heading; extraction takes that heading and its
  following siblings until an element whose tag is `h2` (the
  default stop tag — same as anchor).
- **Container scoping**. Not applicable — no container wraps KS3
  exclusively.

The primitive must support heading-anchor scoping in addition to
container-CSS scoping for sources of this shape.

## 4. KS3 internal structure

Headings within the KS3 region (in document order):

```
h2#key-stage-3                "Key stage 3"
  h3#introduction             "Introduction"           (2 paragraphs)
  h3#working-mathematically   "Working mathematically" (intro p, then 3 h4 strands)
    h4#develop-fluency        "Develop fluency"        (ul)
    h4#reason-mathematically  "Reason mathematically"  (ul)
    h4#solve-problems         "Solve problems"         (ul)
  h3#subject-content          "Subject content"        (6 h4 strands)
    h4#number                 "Number"                 (p, ul)
    h4#algebra-1              "Algebra"                (p, ul)
    h4#ratio-proportion-and-rates-of-change "Ratio, proportion and rates of change"
    h4#geometry-and-measures  "Geometry and measures"  (p, ul)
    h4#probability            "Probability"            (p, ul)
    h4#statistics-5           "Statistics"             (p, ul)
```

The six "Subject content" strands at h4 level are the load-bearing
content for KS3 Maths. The three "Working mathematically" h4 strands are
also load-bearing. All eight strands must appear in the extracted text
for Step 8 Check A.

## 5. `<details>` elements

**Zero `<details>` elements** in this gov.uk page (`soup.find_all("details")`
returns `[]`). The page uses flat headings + `<ul>` lists, not collapsible
panels. The `<details>` handling in the primitive remains relevant for
other gov.uk pages that do use it (e.g. some publications use `<details>`
for "Documents" download collapses) and the primitive's `include_details_content`
flag should default to true so static-HTML collapsible content is captured
on those pages.

## 6. Volume estimate

Pre-extraction estimate for KS3-scoped content (from a heading-anchor walk
in the investigation script): **12,463 characters**, comfortably inside
the 3,000–20,000 character range cited in Step 8 Check C.

## 7. Interaction-pattern classification

**Classification:** `hierarchical_with_scope`.

Rationale: a single deeply-nested content container with multiple
co-equal sub-sections (key stages) demarcated by sibling H2 headings.
The primitive must (a) traverse to a deep content root, (b) optionally
narrow to one heading-anchored sub-region, (c) preserve heading
structure so downstream phases can detect strand boundaries.

This is **not** `single_main_container` (that label fits a flat HTML
page where the whole `<main>` is the target). It is **not**
`multi_container_merged` (there is one container, not several to
combine). It is hierarchical because a section-scope discipline is
necessary to extract one key stage cleanly from a multi-stage document.

## 8. Scope spec sketch (for Step 4 use)

```jsonc
{
  "source_type": "html_nested_dom",
  "url": "https://www.gov.uk/government/publications/national-curriculum-in-england-mathematics-programmes-of-study/national-curriculum-in-england-mathematics-programmes-of-study",
  "content_root_selector": ".govspeak",
  "section_anchor_selector": "#key-stage-3",
  // section_anchor_stop_selector defaults to "h2" (same tag as anchor)
  "include_details_content": true,
  "preserve_headings": true,
  "exclude_selectors": []
  // Chrome lives outside .govspeak; no exclusions needed for this scope.
}
```

## 9. Open questions for Step 4 design

- **Heading-anchor scoping is required** for this source shape and is
  not addressed by a simple `section_scope_selector` (CSS) field. Step 4
  must define both `section_scope_selector` (container CSS, optional)
  and `section_anchor_selector` + `section_anchor_stop_selector`
  (heading-anchor scoping, optional). Exactly one of the two scoping
  mechanisms is used per run.
- The default stop-tag for heading-anchor scoping is the anchor's own
  tag (`h2` if anchor is `h2`). Override via `section_anchor_stop_selector`
  if needed (e.g. anchor on h3 but stop on next h2).
