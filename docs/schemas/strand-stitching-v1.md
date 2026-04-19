# Strand-Stitching Schema — v1

**Status:** Authoritative design for Session 4c-3b.
**Date:** 2026-04-19
**Depends on:** `strand-detection` (Session 4c-3a), `criterion-bank-v1.md` (Session 4c-1)

---

## Purpose

When `detect_strands()` identifies a source as multi-strand, the pipeline runs a full reference-authoring sub-run per strand and stitches the outputs into a unified reference corpus. This schema governs how that stitching is performed: how artefacts are identified, how provenance is preserved, how the unified corpus is structured, and what is explicitly deferred.

---

## 1. Artefact identity across strands

**Decision:** Strand-prefix all IDs in the unified corpus.

Every artefact ID in a per-strand sub-run is prefixed with the strand's slug before being written into the unified corpus. The strand slug is derived from the strand name: lowercase, spaces and slashes replaced with hyphens (e.g. "Ratio and proportion" → `ratio-and-proportion`; "Geometry and measures" → `geometry-and-measures`).

| Original per-strand ID | Unified corpus ID |
|---|---|
| `kud_0001` | `number_kud_0001` |
| `cluster_01` | `algebra_cluster_01` |
| `lt_003` | `geometry-and-measures_lt_003` |
| `lt_003` (rubric) | `geometry-and-measures_lt_003` |

**Rationale:** IDs must be globally unique within the unified corpus so downstream consumers (criterion bank, tutoring systems, DAG validators) can reference any artefact unambiguously. The alternatives considered were hierarchical IDs (nested objects) and post-merge regeneration. Hierarchical IDs require downstream schema changes. Post-merge regeneration destroys the traceability chain back to per-strand quality reports. Strand-prefix is the only approach that is backwards-compatible with downstream consumption while preserving traceability.

**Collision detection:** The stitching step asserts that no prefixed ID appears in more than one strand before writing the unified corpus. If a collision occurs (which is impossible under prefix-based scoping but is asserted as a safety check), the stitch fails with an error rather than silently overwriting.

---

## 2. Cross-strand prerequisites

**Decision:** v1 scopes prerequisite edges within a single strand. Cross-strand prerequisite edges are not generated, recorded, or inferred.

**What is lost by this choice:**

Within the DfE KS3 Maths corpus, mathematically necessary cross-strand dependencies exist that the v1 schema does not capture. Concrete examples:

- Algebra criteria for "simplifying expressions" have a genuine mathematical prerequisite in Number criteria for "understanding place value and integer arithmetic". The Number strand must be substantially developed before Algebra fluency is possible.
- Ratio and Proportion criteria for "using multiplicative reasoning" depend on Number criteria for "multiplication and division fluency" — which sits in a different strand.
- Geometry and Measures criteria for "using algebraic methods to solve geometric problems" depend on Algebra criteria — cross-strand in this schema.

**Effect on teacher-facing output:** Teachers using the unified corpus will see stratified prerequisite graphs per strand. The Number strand's DAG will be internally consistent; the Algebra strand's DAG will be internally consistent. But the dependency from Algebra back to Number will not be visible in the prerequisite graph. A teacher building a learning progression from the unified corpus will need to manually understand the cross-strand ordering — the tool will not surface it.

**Why this choice is acceptable for v1:** Cross-strand prerequisites require reasoning about the relationship between two complete strand DAGs, which is an architectural problem that should be built on top of verified within-strand DAGs. Building cross-strand prerequisite edges before verifying within-strand correctness would compound errors. The v1 criterion bank (Session 4c-4) will validate within-strand DAG correctness first.

**What to watch for in NZ Social Sciences (horizontal domain):** NZ Social Sciences strands (History, Civics and Society, Geography, Economic Activity) are pedagogically interconnected — a civics criterion about "understanding democratic systems" legitimately draws on historical knowledge. Within-strand prerequisite scoping may produce obviously incomplete prerequisite graphs for NZ strands. If the NZ run produces prerequisite graphs where important pedagogical connections are absent (i.e. a criterion appears to have no prerequisites when a teacher would expect it to), this should be documented in the quality report as a known v1 limitation rather than treated as a run failure.

**Deferral:** Cross-strand prerequisite edges are deferred to a future session (post-4c-4). Session 4c-4 validates within-strand DAGs; cross-strand linking is the subsequent step.

---

## 3. Provenance

**Decision:** Every artefact in the unified corpus carries a non-empty `strand` field containing the strand's display name (not the slug) as detected by `detect_strands()`.

### What the `strand` field contains

| Sub-field | Description |
|---|---|
| `strand_name` | Display name as returned by detect_strands (e.g. "Number", "Algebra", "Ratio and proportion") |
| `strand_slug` | Normalised slug used for ID prefixing (e.g. "number", "algebra", "ratio-and-proportion") |
| `detection_confidence` | Float 0.0–1.0 from `StrandResult.confidence` for this strand |

### Which artefacts carry the strand field

All items in the following unified artefacts carry the strand field:
- `unified_kud.json` → each KUDItem
- `unified_competency_clusters.json` → each CompetencyCluster
- `unified_lts.json` → each LearningTarget
- `unified_band_statements.json` → each BandStatementSet
- `unified_observation_indicators.json` → each ObservationIndicatorSet
- `unified_criteria.json` → each Rubric

### Schema update for criterion-bank-v1.md

The criterion bank schema (`docs/schemas/criterion-bank-v1.md`) is extended for multi-strand sources with an optional `strand` field on each criterion entry:

```
strand: {
  strand_name: str,
  strand_slug: str,
  detection_confidence: float
} | null
```

For single-strand sources the field is `null`. For multi-strand sources the field is required and non-null. This is additive and backward-compatible.

---

## 4. Single-strand sources

**Decision:** When `detect_strands()` returns `is_multi_strand=False`, the pipeline runs the existing single-strand path without any orchestration overhead. No stitching step runs. The output directory structure is identical to a single-strand run.

**Branching logic:**
```
detect_strands(content) →
  StrandDetectionUncertain  →  HALT with diagnostic (does not proceed)
  is_multi_strand = False   →  existing path unchanged
  is_multi_strand = True    →  sub-run orchestration + stitching
```

The single-strand path is unchanged — no new code touches the existing pipeline stages when the source is single-strand. This is the regression guarantee for Welsh CfW H&W.

---

## 5. Quality reports

**Per-strand quality reports** (for debugging):
Each strand sub-run produces its own complete `quality_report.md`, `quality_report.json`, `criteria_quality_report.md`, and `criteria_quality_report.json` inside `per_strand/<strand_slug>/`. These are the same format as existing single-strand quality reports. They are the primary diagnostic tool for understanding why a specific strand sub-run failed.

**Unified quality report** (teacher-facing):
A `unified_quality_report.md` at the unified corpus root aggregates:
- Strand detection result (strand names, confidence scores, flags)
- Per-strand artefact counts (KUD items, clusters, LTs, rubrics, supporting components)
- Per-strand gate-fail counts
- Summed unified counts (sum of per-strand KUDs = unified KUD count — verified by the stitcher)
- Per-strand flag summaries (count only; full flag detail is in per-strand reports)

The unified report is the output a teacher-facing curriculum assistant would surface. The per-strand reports remain available for pipeline engineers and curriculum designers who need to trace specific flags.

---

## 6. Unified corpus directory structure

```
<out>/
├── strand_detection.json          (StrandDetectionResult serialised)
├── per_strand/
│   ├── <strand_slug>/             (one per detected strand)
│   │   ├── inventory.json
│   │   ├── kud.json
│   │   ├── progression_structure.json
│   │   ├── quality_report.md
│   │   ├── quality_report.json
│   │   ├── competency_clusters.json
│   │   ├── lts.json
│   │   ├── band_statements.json
│   │   ├── observation_indicators.json
│   │   ├── criteria.json
│   │   ├── criteria_quality_report.md
│   │   ├── criteria_quality_report.json
│   │   └── supporting_components.json
│   └── ...
├── unified_kud.json               (all KUD items, strand-prefixed IDs, strand field)
├── unified_competency_clusters.json
├── unified_lts.json
├── unified_band_statements.json
├── unified_observation_indicators.json
├── unified_criteria.json
├── unified_quality_report.md
└── unified_quality_report.json
```

---

## 7. Sanity checks (required before declaring success)

For any multi-strand run, the following must be verified before the session is declared complete:

1. Every strand has its own subdirectory under `per_strand/`.
2. Every artefact in unified outputs carries a non-empty `strand.strand_name` field.
3. No prefixed artefact IDs collide across strands (collision detection runs at stitch time).
4. Every prerequisite edge in every strand's LT set references an LT within the same strand (validated by checking the lt_id prefix matches the strand slug).
5. Unified quality report aggregated counts equal the sum of per-strand counts (KUD items, clusters, LTs, rubrics, supporting components).

---

*Schema v1 authored 2026-04-19 (Session 4c-3b). This schema governs the stitching implementation for this session.*
