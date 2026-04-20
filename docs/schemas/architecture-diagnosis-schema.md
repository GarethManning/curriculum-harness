# Architecture Diagnosis Schema

**Status:** Active — Session 4c-5 added `developmental_scope` fields.
**Date:** 2026-04-20

---

## Purpose

Architecture diagnosis captures source-level structural properties of a curriculum source. These properties are detected once from the source's metadata and content and propagated into downstream pipeline outputs (LTs, rubrics, criterion banks) as structured metadata and flags.

Architecture diagnosis is **complementary** to progression detection:

| Module | Detects | Stored in |
|---|---|---|
| `detect_progression` | Source's native band framework (Progression Steps, Levels, Grade levels) | `progression_structure.json` |
| `detect_developmental_scope` | Whether the source covers a single developmental point, an explicit multi-band progression, or a multi-year range without internal banding | `DevelopmentalScopeResult` (runtime), flags on LTs/rubrics/criteria |

---

## Fields

### `developmental_scope`

**Type:** `string` — one of `"single_band"`, `"explicit_progression"`, `"range_without_bands"`

**Description:** Whether the source covers a single developmental point, an explicit multi-band progression with per-band expectations, or a developmental range without internal banding.

**Values:**

| Value | Definition | Examples |
|---|---|---|
| `single_band` | Source targets a single grade, course, or equivalent single developmental point | Common Core 7.RP (Grade 7 only), AP US Gov Unit 1 (single unit), Ontario Grade 7 History |
| `explicit_progression` | Source spans multiple developmental levels AND specifies internal bands with expectations at each band | Welsh CfW H&W (Progression Steps 1-5), Scottish CfE (Levels Early through Senior) |
| `range_without_bands` | Source covers a developmental range WITHOUT explicit internal banding within that range | Secondary RSHE 2025 (KS3+KS4 combined terminal outcomes), DfE KS3 Mathematics (Years 7-9 without per-year breakdown), NZ Curriculum Social Sciences (multiple NZ levels without per-level decomposition) |

**Detection logic:** See `curriculum_harness/reference_authoring/developmental_scope/detect_scope.py`.

1. **Curated source_type map (primary, high confidence)** — maps `source_type` strings from `detect_progression` directly to `developmental_scope`. Covers all current harness source types.
2. **Content inspection for `nz_curriculum`** — scans `content_blocks` for `Level N` markers. Present (≥ 2 distinct) → `explicit_progression`. Absent → `range_without_bands`.
3. **General content inspection fallback** — for unknown source types: scans for Year/Level/Grade markers and terminal-outcome language (`"by the end of"`, etc.).

**Why `range_without_bands` ≠ `explicit_progression` for multi-level NZ sources:**

The NZ Curriculum framework has per-level achievement objectives (Levels 1-8). However, specific NZ source documents may ingest content that covers multiple levels without per-level decomposition in the content blocks. The `nz_curriculum` source type is detected from the URL (high confidence), but the actual content may present multi-level material as a single aggregate rather than level-by-level objectives. The content inspection distinguishes these cases.

---

### `developmental_scope_confidence`

**Type:** `string` — one of `"high"`, `"medium"`, `"low"`

**Description:** How reliably the `developmental_scope` classification was determined.

**Values:**

| Value | When assigned |
|---|---|
| `high` | Source type is in the curated map, OR source type is `nz_curriculum` and content inspection is conclusive (≥ 2 Level markers present, or 0 Level markers present) |
| `medium` | Inferred source type (suffix `_inferred`), OR content inspection has partial signals (single ambiguous marker, or Year refs without structured per-year objectives) |
| `low` | Contradictory signals — content contains both per-level decomposition markers AND terminal-outcome language. The emitted flag surfaces the ambiguity rather than asserting the classification |

---

## Flag: `developmental_scope_range_without_bands`

Emitted on LTs, rubrics, and criterion bank outputs for sources where `developmental_scope == "range_without_bands"`.

**Flag fields:**

| Field | Description |
|---|---|
| `flag_type` | `"developmental_scope_range_without_bands"` |
| `confidence_tier` | Matches `developmental_scope_confidence` of the source |
| `domain_type` | `"sequential"` / `"horizontal"` / `"dispositional"` / `"mixed"` — so downstream tools (band decomposer) know what developmental methodology to apply |
| `source_slug` | The source's slug |
| `source_type` | The `source_type` from `detect_progression` |
| `explanation_technical` | Always present. Technical description of the limitation |
| `explanation_pedagogical_cognitive` | Present when `domain_type` is not `"dispositional"`. Explains why single-grade planning needs the band decomposer tool |
| `explanation_pedagogical_dispositional` | Present when `domain_type` is `"dispositional"` or `"mixed"`. Explains why dispositional progression requires teacher judgement alongside banded output |

**Layered explanations:**

*Technical:*
> Source covers a developmental range without explicit source-native bands. Output describes terminal outcomes for the full range, not expectations appropriate to any specific year group within the range.

*Pedagogical (cognitive domains):*
> LTs and rubrics describe what students should achieve by end of range, not what is appropriate for any specific year group within the range. Use the band decomposer tool before using these outputs for single-grade planning.

*Pedagogical (dispositional domains):*
> LTs describe terminal dispositional outcomes. Dispositional progression does not cleanly map to year groups even after band decomposition — teacher judgement is required alongside any banded output from the band decomposer tool.

---

## Scope and constraints

- Detection and flagging only. No developmental decomposition — that is the band decomposer tool.
- Does NOT modify Phase 1-5 pipeline code or `detect_progression`.
- Does NOT retroactively re-process existing reference corpora. Retroactive flagging of the three known `range_without_bands` sources (RSHE 2025, DfE KS3 Maths, NZ SS) is a separate task.
- The flag applies to future pipeline runs.

---

## Ground truth — 7 reference sources (Session 4c-5 verification)

Verified 2026-04-20 against stored `progression_structure.json` + `inventory.json`. No pipeline re-run.

| Source | `source_type` | `developmental_scope` | `developmental_scope_confidence` |
|---|---|---|---|
| Common Core 7.RP | `us_common_core_grade` | `single_band` | `high` |
| Ontario G7 History | `ontario_grade` | `single_band` | `high` |
| AP US Gov Unit 1 | `us_ap_course_unit` | `single_band` | `high` |
| Welsh CfW H&W | `welsh_cfw_aole` | `explicit_progression` | `high` |
| Secondary RSHE 2025 | `england_rshe_secondary` | `range_without_bands` | `high` |
| DfE KS3 Mathematics | `england_nc_ks3_only` | `range_without_bands` | `high` |
| NZ Social Sciences | `nz_curriculum` | `range_without_bands` | `high` |

Verification script: `scripts/verify_developmental_scope_7sources.py`
