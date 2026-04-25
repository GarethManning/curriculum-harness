# Comparison-content sources

Raw fetches of the philosophical / rationale layer of each external framework. These are the audit trail for every claim made in `level-1-essay.md`, `level-2-cards/`, and `level-3-themes/`. If a card or essay says "RSHE foregrounds X," there must be a paragraph in this directory that says X.

## Subdirectories

- `rshe/` — UK DfE statutory Relationships, Sex and Health Education guidance (July 2025)
- `cfw/` — Welsh Curriculum for Wales, Health and Well-being Area of Learning and Experience
- `casel/` — CASEL framework rationale, design principles, and competency definitions

## File-naming convention

`{framework}-{document-slug}.md` — e.g. `rshe-foreword.md`, `cfw-four-purposes.md`, `casel-fundamentals.md`.

## File header (required)

Every source file starts with this header:

```
# {Document title}

**Source URL:** {full URL}
**Fetched:** {YYYY-MM-DD}
**Publisher:** {organisation}
**Document date / edition:** {date}
**Licence:** {licence note}
**Scope captured:** {one line — what part of the document was fetched}
```

## Paragraph numbering

Each substantive paragraph in the body is preceded by a tag of the form `§N` on its own line, where N is a sequential integer starting from 1 within the file. Section headings do not get paragraph numbers; only paragraphs that contain quotable content do. Bullets within a numbered paragraph share that paragraph's number.

Citations in the comparison content take the form `[rshe-foreword §3]`, `[cfw-four-purposes §1]`, `[casel-fundamentals §2]` — file slug plus paragraph number. The build-time check confirms every such tag resolves to a paragraph in this directory.

## Append-only

Once a source file is committed, its content is not edited. Errors get a new file (`{slug}-v2.md`) with the correction noted in the header. This preserves the audit trail.
