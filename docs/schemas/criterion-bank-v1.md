# Criterion Bank Schema — v1

**Status:** Updated for Session 4c-4. `strand` field added as mandatory.
**Date:** 2026-04-19 (updated 2026-04-19)

## Purpose

The criterion bank is the fourth artefact of the reference-authoring pipeline. It is the shared substrate that criterion-referencing downstream sessions (tutoring systems, adaptive feedback, curriculum alignment tools) consume. Rubric rendering (five-level / four-level / single-point / mastery-binary / alternative vocabulary) is configurable downstream, not hardcoded in the harness.

Each entry in the bank is one criterion — a single, observable claim about what a learner can do at a defined competency level, attached to one or more LTs and embedded in a prerequisite structure.

---

## Fields

### `criterion_id`

**Type:** `string`

Unique identifier for this criterion within the source's bank. Format: `{source_slug}_crit_{n:04d}`, e.g. `welsh-cfw-health-wellbeing_crit_0001`.

**Rationale:** Criterion IDs must be stable across sessions so downstream DAG consumers and tutoring system integrations can reference specific criteria. The source-slug prefix prevents collisions across multi-source banks.

---

### `associated_lt_ids`

**Type:** `array[string]` — one or more LT IDs this criterion attaches to.

One criterion may be shared across two LTs when the underlying capability overlaps (e.g. a "describe" criterion that applies to both a declarative and a reasoning LT in the same competency cluster). In practice, most criteria attach to exactly one LT.

**Rationale:** LT-level attachment keeps the criterion bank composable. A tutoring system can query by LT and retrieve all relevant criteria without knowing the full bank structure.

---

### `competency_level_descriptors`

**Type:** `object` with five required string fields:

| Field | Description |
|---|---|
| `no_evidence` | The student shows no attempt or awareness of this criterion. |
| `emerging` | The student shows partial or prompted engagement with this criterion. |
| `developing` | The student engages with the criterion but with gaps, inconsistencies, or reliance on support. |
| `competent` | The student meets this criterion fully and independently. Competent is always framed as success, never as "acceptable-but-deficient". |
| `extending` | The student exceeds the criterion — deeper, more nuanced, or more transferable than competent. |

**Rationale:** The five-level default (No Evidence / Emerging / Developing / Competent / Extending) is the harness default schema. Downstream rendering layers may collapse to four levels, translate to alternative vocabulary (e.g. Beginning / Developing / Proficient / Extending), or use single-point or mastery-binary formats. The harness always stores all five to keep the bank fully expressive.

---

### `prerequisite_criterion_ids`

**Type:** `array[string]` — zero or more criterion IDs within the same source's bank that must be demonstrated before this criterion can be meaningfully assessed.

An empty array indicates no prerequisite within the bank. Cross-source prerequisites are not recorded here.

**Rationale:** Prerequisites form a directed acyclic graph (DAG) across criteria. The DAG enables adaptive sequencing: a tutoring system can determine which criteria to address first for a given learner. Session 4c-4 will validate that no cycles exist in this DAG. The prerequisite edge here is criterion-to-criterion (more granular than the LT-level prerequisite edges already on `Rubric.prerequisite_edges`).

---

### Edge type semantics — `within_lt_band`

Prerequisite edges carry an `edge_type` field on `prerequisite_edges_detail`. The `within_lt_band` value has **two distinct meanings depending on the LT type of the edge endpoints**, and applying the wrong reading during review produces spurious removal flags.

- **T1 and T2 LTs:** `within_lt_band` is a **strict skill prerequisite**. Band N+1 cannot be demonstrated without Band N being secured first — the Band N+1 observable requires the Band N capacity as a building block. An edge is semantically correct only if the downstream criterion literally depends on the upstream skill or knowledge being in place.

- **T3 LTs:** `within_lt_band` is **developmental staging**, not a gated task dependency. Band N+1 represents a more mature expression of the same underlying disposition — it presupposes the developmental ground of Band N (the earlier-band dispositional move having become available to the student) but does not require Band N to have been evidenced first in order for Band N+1 evidence to count. Dispositions do not gate on prior-band performance the way skills do; they deepen and integrate across bands.

**Consequence for review:** do not remove a T3 `within_lt_band` edge on the basis that the Band N+1 observable is "achievable without demonstrating Band N". That test applies to T1/T2 strict prerequisites; under T3 developmental-staging semantics, the edge is correct even when each band's observable can in principle be evidenced independently. If a T3 Band N+1 observable is genuinely unrelated to the Band N developmental ground, the issue is a KUD-chart defect upstream of the edge, not an edge-semantics defect — flag at chart level, not by edge removal.

**Rationale:** Every T3 LT is required by schema convention to carry an unbroken A→B→C→D→E→F within-band chain. Removing T3 staging edges under the T1/T2 strict-prerequisite test breaks that chain. The distinction is load-bearing for reviewers, validators, and any downstream tool that inspects edge correctness — a schema-reader must encounter it here rather than relying on separate review-convention documentation. (Originally codified in `PROMPT_STANDARDS.md` on 2026-04-23; propagated here so schema consumers do not miss it.)

---

### `source_provenance`

**Type:** `string`

Which KUD item or source bullet this criterion traces back to. Format: the `item_id` from the source's KUD (e.g. `kud_042`), optionally with a human-readable description of the source bullet for review purposes.

**Rationale:** Traceability to the source document is a hard requirement for the harness. A criterion that cannot be traced to a specific KUD item is not a reference criterion — it may be a prior injection. `source_provenance` allows a reviewer to open the KUD and verify the criterion accurately represents the source content.

---

### `strand`

**Type:** `string` — mandatory.

The strand this criterion belongs to. For multi-strand sources (e.g. DfE KS3 Maths, NZ Social Sciences), this is the strand slug (e.g. `"number"`, `"history"`). For single-strand sources (e.g. Welsh CfW H&W, Common Core 7.RP, Ontario G7 History), set to `"single_strand"`.

**Rationale:** Consistent shape across all sources — consumers do not need a null-check or a branch for single-strand sources. `"single_strand"` is an explicit sentinel that signals the source has no strand division, not that the field was omitted. Required for DAG validation: cross-strand prerequisite edges are rejected in v1 scope (within-strand only).

---

### `schema_version`

**Type:** `string` — always `"v1"` for entries conforming to this schema.

**Rationale:** Schema versioning allows downstream consumers to detect and handle breaking changes. Session 4c-4 will produce `schema_version: "v1"`. Future schema revisions increment this field.

---

## Notes

- This schema is what Session 4c-4 will produce. Session 4c-1 sketches it so that the flag explanations surfaced during 4c-1 can reference what downstream sessions will consume.
- The criterion bank is distinct from the `criteria.json` artefact already produced by the pipeline. `criteria.json` carries `Rubric` objects — five-level rubrics with gate-annotated stability metadata. The criterion bank is a flatter, more portable format suitable for tutoring system ingestion.
- The `Rubric` → criterion bank conversion will be built in Session 4c-4. This schema is the target format.
- Type 3 LTs (observation indicators) are not included in the criterion bank v1. Type 3 assessment is multi-informant; the criterion bank covers Type 1 (rubric_with_clear_criteria) and Type 2 (reasoning_quality_rubric) LTs only.

---

*Schema v1 sketched 2026-04-19 (Session 4c-1). `strand` field added as mandatory 2026-04-19 (Session 4c-4 pre-work). Session 4c-4 produces criterion banks conforming to this schema for anchor sources; 4c-4b for remaining sources.*
