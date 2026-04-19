# DAG Validation Rules — v1

**Status:** Active. Governs Session 4c-4 criterion bank prerequisite graph validation.
**Date:** 2026-04-19

## Purpose

Prerequisite edges in the criterion bank form a Directed Acyclic Graph (DAG). If the graph contains cycles, self-loops, or bad references, it cannot be used for adaptive sequencing — a tutoring system following the graph would either loop forever or fail to resolve a path. This document defines the validation rules and the behaviour on violation.

All violations are **halt-and-report**. There is no auto-correction. A violation requires human review before the source's criterion bank is accepted.

---

## Rule 1 — Cycle Detection

**Definition:** A cycle exists when criterion A has a prerequisite path (direct or transitive) that leads back to A.

**Detection method:** Run DFS (depth-first search) from every node. Track the recursion stack. If a node already on the stack is encountered during traversal, a cycle is detected.

**Violation response:**
1. Report the full cycle path: `A → B → C → A`
2. Halt generation for this source
3. Do not proceed to the next source
4. Emit a `dag_validation_error` in the quality report with type `cycle` and the full path

**Example of a cycle (reject):**
```
criterion_A prereqs: [criterion_B]
criterion_B prereqs: [criterion_C]
criterion_C prereqs: [criterion_A]   ← closes the cycle
```

Cycle path to report: `criterion_A → criterion_B → criterion_C → criterion_A`

---

## Rule 2 — Self-Loop Detection

**Definition:** A self-loop exists when a criterion lists itself in its own `prerequisite_criterion_ids`.

**Detection method:** For each criterion, check whether its own `criterion_id` appears in its `prerequisite_criterion_ids`.

Self-loops are a degenerate case of a cycle (length 1) and are caught before full DFS to produce a clearer error message.

**Violation response:**
1. Report the criterion ID: `criterion_A has self-loop`
2. Halt generation for this source
3. Emit a `dag_validation_error` with type `self_loop`

**Example (reject):**
```
criterion_id: welsh-cfw-health-wellbeing_crit_0003
prerequisite_criterion_ids: ["welsh-cfw-health-wellbeing_crit_0003"]   ← self-loop
```

---

## Rule 3 — Unresolved ID Detection

**Definition:** An unresolved ID exists when a `prerequisite_criterion_ids` entry references a `criterion_id` that does not exist in the bank being validated.

**Detection method:** Build a set of all `criterion_id` values in the bank. For each criterion, check that every ID in its `prerequisite_criterion_ids` is a member of that set.

**Violation response:**
1. Report the referencing criterion and the missing ID: `criterion_A references missing criterion_X`
2. Halt generation for this source
3. Emit a `dag_validation_error` with type `unresolved_id`

**Common cause:** Criterion generation that emits an ID before that criterion has been assigned its final ID (e.g. an off-by-one in the ID numbering sequence), or a criterion that was planned during decomposition but not generated.

---

## Rule 4 — Cross-Strand Edge Detection

**Definition (v1 scope):** A cross-strand edge exists when a criterion in strand A lists a prerequisite criterion in strand B (different strand slug).

**Detection method:** For each prerequisite edge, compare the `strand` field of the source criterion and the `strand` field of the referenced prerequisite criterion. If they differ, the edge is a cross-strand edge.

**Violation response:**
1. Report the edge: `criterion_A (strand: algebra) → criterion_B (strand: number) — cross-strand edge`
2. Halt generation for this source
3. Emit a `dag_validation_error` with type `cross_strand_edge`

**Rationale for v1 rejection:** Cross-strand prerequisite dependencies are likely real in practice (e.g. number fluency is prerequisite for algebra). However, v1 scope restricts edges to within-strand to keep the DAG manageable and to avoid generating poorly-evidenced cross-strand claims. Cross-strand edges will be a v2 feature when the full multi-source bank exists and cross-strand evidence can be properly curated.

**Single-strand sources:** All criteria in a single-strand source have `strand: "single_strand"`. Cross-strand detection trivially passes for these sources (all criteria share the same strand value).

---

## Rule 5 — Agreement Rate Floor

**Definition:** The agreement rate is the proportion of hand-curated "known-true" prerequisite edges (from the validation set) that are recovered in the generated criterion bank, mapped from LT-level to criterion-level via `associated_lt_ids`.

**Mapping procedure:**
1. For each hand-curated LT-level edge (LT_A prerequisite-to LT_B):
2. Find all criteria with `associated_lt_ids` containing LT_A → call this set `crit_A_set`
3. Find all criteria with `associated_lt_ids` containing LT_B → call this set `crit_B_set`
4. The edge is **recovered** if at least one criterion in `crit_A_set` appears in the `prerequisite_criterion_ids` of at least one criterion in `crit_B_set`
5. Agreement rate = recovered edges / total hand-curated edges

**Two-level reporting (per Gareth Manning, 2026-04-19):**

- **Primary agreement rate (floor applies):** The edge exists — at least one criterion-level edge recovers the hand-curated LT-level edge via `associated_lt_ids` mapping, regardless of `reasoning_tag`. 50% floor applies. Below floor → halt and report.
- **Secondary agreement rate (diagnostic only):** The edge exists AND the `reasoning_tag` on the generated edge matches the hand-curated tag. No floor. Reported for calibration purposes — tracks whether the generator's ontological vs. pedagogical classification aligns with curator judgement.

**Floor:** 50% on primary agreement rate only. If primary falls below 50% for any anchor source, halt and report before proceeding to the next source.

**Violation response:**
1. Report both agreement rates and the list of unrecovered edges (primary)
2. Halt generation for this source if primary < 50%
3. Do not proceed to the next source on halt

**Note:** The agreement rate is a floor check, not a target. A rate of 100% is not expected — the generated bank may encode prerequisite structure at a finer grain than the hand-curated LT-level edges. The floor exists to detect gross failures: if fewer than half of the known-true structural relationships appear in the generated bank, the decomposition or prerequisite generation is likely systematically wrong. Secondary agreement rate below 50% is diagnostic — it suggests systematic tag misclassification but does not halt generation.

---

## Validation execution order

Run in this order per source. Stop on first failure:

1. Self-loop detection (fast scan, O(n))
2. Unresolved ID detection (set membership check, O(n))
3. Cross-strand edge detection (field comparison, O(e) where e = edge count)
4. Cycle detection (DFS, O(n + e))
5. Agreement rate calculation (mapping + edge recovery check)

This order prioritises cheap checks first and surfaces structural errors before the more expensive graph traversal.

---

## Output format

DAG validation results are reported in `criterion_bank_quality_report.json` under the key `dag_validation`:

```json
{
  "dag_validation": {
    "passed": true,
    "errors": [],
    "primary_agreement_rate": 0.83,
    "secondary_agreement_rate": 0.67,
    "hand_curated_edges_total": 12,
    "primary_edges_recovered": 10,
    "secondary_edges_recovered": 8,
    "unrecovered_edges": [
      {
        "lt_a": "cluster_04_lt_01",
        "lt_b": "cluster_04_lt_02",
        "rationale": "no criterion in crit_A_set found in prerequisite_criterion_ids of any criterion in crit_B_set"
      }
    ],
    "tag_mismatch_edges": [
      {
        "lt_a": "cluster_05_lt_01",
        "lt_b": "cluster_05_lt_02",
        "curated_tag": "ontological_prerequisite",
        "generated_tag": "pedagogical_sequencing"
      }
    ]
  }
}
```

On failure, `"passed": false` and `"errors"` contains one or more entries of the form:

```json
{
  "type": "cycle | self_loop | unresolved_id | cross_strand_edge | agreement_rate_below_floor",
  "detail": "human-readable description",
  "path": ["criterion_A", "criterion_B", "criterion_C", "criterion_A"]
}
```

---

*Rules v1 written 2026-04-19 (Session 4c-4 pre-work). Governs anchor source generation: Welsh CfW H&W, Common Core 7.RP, Ontario G7 History.*
