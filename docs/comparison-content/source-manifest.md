# Source manifest — Stop 1

Audit trail for the philosophical / rationale layer of each external framework. Every claim in `centre-of-gravity-briefs.md`, the forthcoming `level-1-essay.md`, the 63 Level 2 cards, and the 8 Level 3 themes must resolve to a paragraph in one of the files listed below.

## Inventory (7 files, 7,299 words of source prose)

### RSHE — UK DfE statutory guidance, July 2025

| File | Source URL | Capture method | Paragraphs |
|---|---|---|---|
| `sources/rshe/rshe-foreword.md` | gov.uk PDF (raw.pdf in repo, pp. 1–7) | Verbatim from local PDF read | §1–§23 + §15a–§15g |
| `sources/rshe/rshe-strand-introductions.md` | gov.uk PDF (raw.pdf in repo, pp. 7–9, 11, 20, 25) | Verbatim from local PDF read | §24–§44 |

Local raw PDF: `docs/run-snapshots/2026-04-19-session-4c-2a-secondary-rshe-2025/raw.pdf` (616 KB). DfE document URL: https://assets.publishing.service.gov.uk/media/6970e7e67e827090d02d42e0/Relationships_education_relationships_and_sex_education__RSE__and_health_education__for_intro_1_September_2026_.pdf

### Welsh CfW — Curriculum for Wales, Health and Well-being AoLE

| File | Source URL | Capture method | Paragraphs |
|---|---|---|---|
| `sources/cfw/cfw-what-matters.md` | https://hwb.gov.wales/curriculum-for-wales/health-and-well-being/statements-of-what-matters/ | Verbatim from existing HTML snapshot in repo (run-snapshots/2026-04-19-session-4a-5-wales-cfw-health-wellbeing-sow/), with mid-word line-break artifacts rejoined | §1–§21 |
| `sources/cfw/cfw-four-purposes.md` | https://hwb.gov.wales/curriculum-for-wales/designing-your-curriculum/developing-a-vision-for-curriculum-design/ | Live WebFetch with verbatim-extraction prompt | §1–§5 |
| `sources/cfw/cfw-rse-statutory-principles.md` | https://hwb.gov.wales/curriculum-for-wales/designing-your-curriculum/cross-cutting-themes-for-designing-your-curriculum/ | Live WebFetch with verbatim-extraction prompt; sections "Why is RSE so important?", "What is RSE?", "Developmentally-appropriate learning" | §1–§14 |

### CASEL

| File | Source URL | Capture method | Paragraphs |
|---|---|---|---|
| `sources/casel/casel-framework-definition.md` | https://casel.org/fundamentals-of-sel/what-is-the-casel-framework/ | Live WebFetch with verbatim-extraction prompt | §1–§13 |
| `sources/casel/casel-equity-transformative-sel.md` | https://casel.org/fundamentals-of-sel/how-does-sel-support-educational-equity-and-excellence/ | Live WebFetch with verbatim-extraction prompt | §1–§4 |

CASEL also publishes the SEL Skills Continuum (Pre-K–Adults), already captured in the existing repo at `docs/reference-corpus/casel-sel-continuum/source.md` — referenced for per-grade-band content where Level 2 cards need it; not duplicated here.

## Capture method notes

- **RSHE.** Captured directly from the local PDF in the repo. This is the highest-fidelity source available for the document — the gov.uk-hosted PDF is the authoritative version.

- **Welsh CfW (What Matters).** The existing snapshot is the page text as fetched 2026-04-19 (raw HTML preserved at `raw.html` in the same directory). One transcription decision worth noting: the snapshot's text-extraction broke a few mid-word ("enabl / ing", around the link to "empathy"); these have been silently rejoined here to reflect the prose as published. No words have been added, removed, or paraphrased.

- **Welsh CfW (Four Purposes, RSE statutory).** Captured via live WebFetch with explicit verbatim-extraction and Crown Copyright / OGL v3.0 attribution prompts. The model returned what it identified as verbatim text. Spot-check protocol before final corpus commit: I will draw 3 random claims from each WebFetch-sourced file and verify each against the live page.

- **CASEL.** Same approach as Welsh CfW WebFetches. Same spot-check protocol applies.

## Citation convention

Cite as `[file-slug §N]` — e.g., `[rshe-foreword §1]`, `[cfw-rse-statutory-principles §11]`, `[casel-framework-definition §5]`. The file slug is the filename minus `.md`; the §N is the verbatim paragraph number in the source file. Compound citations: `[rshe-foreword §12, §15b, §16, §19]`.

A Python check at the end of each writing pass walks every citation in the deliverable and confirms the slug+§ resolves to a real paragraph in `sources/`. The check has been run on `centre-of-gravity-briefs.md` — all 26 citations resolve cleanly.

## What is NOT in this manifest

This manifest captures the **philosophical / rationale** layer only. Three categories of content live elsewhere and are referenced from there when needed:

- **RSHE curriculum content** (the "by the end of primary / secondary should know" lists) — already decomposed at `docs/reference-corpus/uk-statutory-rshe/`.
- **Welsh CfW Descriptions of Learning per Progression Step** — already captured at `docs/reference-corpus/welsh-cfw-health-wellbeing/source-ps-descriptions.md`.
- **CASEL SEL Skills Continuum** (per-grade-band skill lists) — already captured at `docs/reference-corpus/casel-sel-continuum/source.md`.

Cards that need to cite specific per-topic content for an external framework will cite from those existing files using a parallel slug convention (e.g., `[rshe-curriculum families-§3]`). The manifest will be extended at Stop 3 (pilot) once that need surfaces — for Stop 1 (centre-of-gravity briefs) and Stop 2 (Level 1 essay), the philosophical layer above is sufficient.
