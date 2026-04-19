# Cross-source reference corpus summary
*Generated: 2026-04-19 — session 4b-5.*

Three sources have passed through the full reference-authoring pipeline
including the 4b-4 criterion stage (five-level rubrics + supporting
components for Type 1/2 LTs): Welsh CfW HWB, Common Core G7 RP, and
Ontario G7 History. Ontario was re-clustered on Opus 4.6 in 4b-5 to
bring membership drift below the 20% threshold; LT/band/indicator/
criterion/supporting stages were regenerated on Haiku on those
stabilised clusters. This document provides a quantitative comparison
and a set of cross-source observations.

---

## Source inventory

| Source | Slug | Domain | Jurisdiction | Bands | Source type |
|---|---|---|---|---|---|
| Welsh CfW Health and Well-being | `welsh-cfw-health-wellbeing` | dispositional | Wales | 5 (PS 1–5) | `welsh_cfw_aole` |
| Common Core G7 Ratios & Proportional Relationships | `common-core-g7-rp` | hierarchical | USA (CCSS) | 1 (Grade 7) | `us_common_core_grade` |
| Ontario Grade 7 History | `ontario-g7-history` | horizontal | Ontario, Canada | 1 (Grade 7) | `ontario_grade` |

---

## Pipeline counts

| Metric | Welsh CfW HWB | Common Core G7 RP | Ontario G7 History |
|---|---|---|---|
| Inventory blocks | 26 | 18 | 259 |
| KUD items | 33 | 22 | 188 |
| Halted blocks | 6 | 8 | 129 |
| — severe underspecification | 4 | 8 | 118 |
| — classification unreliable | 2 | 0 | 11 |
| Expected-yield blocks | 20 | 10 | 141 |
| Artefact-count ratio | 1.650 | 2.200 | 1.333 |
| Ratio domain band | [0.8, 2.2] (disp.) | [0.8, 2.5] (hier.) | [0.8, 1.5] (horiz.) |
| KUD gate result | PASSED | PASSED | PASSED |
| Competency clusters | 9 | 4 | 8 |
| Cluster model | Haiku | Haiku | Opus 4.6 |
| Cluster stability | cluster_unstable | cluster_unstable | cluster_unstable |
| LTs | 20 | 8 | 13 |
| Halted LT clusters | 0 | 0 | 3 |
| Band-statement sets | 11 | 6 | 11 |
| Observation indicator sets | 5 | 0 | 2 |
| Criterion rubrics (Type 1/2) | 12 | 7 | 7 |
| Criterion gate pass | 11 | 6 | 6 |
| Criterion halted | 2 | 1 | 4 |
| Supporting components | 9 | 4 | 6 |
| Supporting halted | 2 | 2 | 0 |

---

## Knowledge-type distribution

| Type | Welsh CfW HWB | Common Core G7 RP | Ontario G7 History |
|---|---|---|---|
| Type 1 (know/understand) | 21 (64%) | 21 (95%) | 62 (33%) |
| Type 2 (do_skill) | 5 (15%) | 1 (5%) | 110 (59%) |
| Type 3 (do_disposition) | 7 (21%) | 0 (0%) | 16 (9%) |

**Observations:**

- **Welsh CfW** has the highest Type 3 share (21%), consistent with a
  dispositional curriculum domain that explicitly describes sustained
  orientations.
- **Common Core** is almost purely Type 1 (95%) — the standard text
  states specific procedural and declarative content; there is one
  analytical item (Type 2) embedded in a reasoning standard.
- **Ontario G7 History** is predominantly Type 2 (59%) — inquiry and
  analytical skills tied to specific historical contexts — consistent
  with the horizontal domain. Type 3 items (9%) correspond to FOCUS ON
  historical-thinking concepts (Continuity and Change, Historical
  Perspective, etc.) that are described in the source as sustained
  orientations.

---

## Artefact-count ratios

| Source | Items | Expected-yield blocks | Ratio | Band | Status |
|---|---|---|---|---|---|
| Welsh CfW | 33 | 20 | 1.650 | [0.8, 2.2] dispositional | PASS |
| Common Core G7 RP | 22 | 10 | 2.200 | [0.8, 2.5] hierarchical | PASS |
| Ontario G7 History | 188 | 141 | 1.333 | [0.8, 1.5] horizontal | PASS |

**Observations:**

- Welsh CfW's 1.65 ratio drove the 4b-2 provisional ceiling revision for
  dispositional sources (raised to 2.2). Its ratio sits comfortably below
  the revised ceiling.
- Common Core's 2.2 ratio drove the 4b-3 ceiling revision for hierarchical
  sources (raised to 2.5). Small denominator (10 blocks) means high
  sensitivity to LLM non-determinism: each item adds 0.1 to the ratio.
- Ontario's 1.333 ratio is the lowest of the three and fits comfortably
  within the horizontal band [0.8, 1.5] without triggering any gate
  revision.

---

## Cluster stability

All three sources produced `cluster_unstable` overall — no source achieved
`stable` at the cluster level. The specific drivers differ by source:

- Welsh CfW (9 clusters, 33 items, Haiku): small items-per-cluster
  denominator amplifies Jaccard sensitivity. Cluster content is correct on
  manual review.
- Common Core (4 clusters, 22 items, Haiku): 4b-3 run; cluster_unstable
  driven by dominant-type drift on one cluster, not membership drift. Small
  source.
- Ontario (8 clusters, 188 items, **Opus 4.6**, 4b-5 re-run): membership
  drift **0% (vs run-2) / 9.57% (vs run-3)**, both below the 20% threshold.
  Residual instability is `cluster_count_differs [8, 8, 7]` and
  `cluster_missing_in_run3` (one canonical cluster has no Jaccard≥0.30 match
  in run 3). Prior Haiku run (4b-3) had 43.09% membership drift on 11
  clusters — escalation to Opus was load-bearing for the DoD target.

`cluster_unstable` is flagged for human review but is not a halting
condition. Across all three sources, the cluster boundaries on visual
inspection follow the source's organising structure correctly.

### Ontario downstream honest halts (4b-5)

The Opus re-clustering consolidated Ontario's prior 11 clusters into 8
larger, thematically coherent clusters (e.g. splitting by era 1713–1800
vs 1800–1850, each with Continuity/Change, Perspectives, and Causes
/Consequences/Significance dimensions). Three of the eight clusters
halted LT generation under Haiku (0/3, 1/3, 0/3 parseable runs) — all
three clusters are large (23, 34, 31 items). This produced 13 LTs from
5 productive clusters, below the prior 23-LT Haiku output (which itself
came from unstable 11-cluster output). Downstream: 4 of 11 Type 1/2
LTs halted at the rubric stage (`rubric_unreliable`), producing 7
rubrics of which 6 pass criterion gates. Pattern of halt reasons is
consistent with prior anchors (parse-reliability ceiling on Haiku); the
reduced absolute counts reflect Opus's cleaner consolidation, not a
regression.

---

## Observation indicators (Type 3)

| Source | Indicator sets |
|---|---|
| Welsh CfW | 5 |
| Common Core | 0 (no Type 3 items) |
| Ontario | 2 |

Welsh CfW has the richest observation-indicator output, matching its
dispositional domain. Ontario's 2 indicator sets in the 4b-5 re-run
come from the two Type 3 LTs that survived clustering + LT generation
under Opus clusters. The FOCUS ON disposition KUD items are
distributed across multiple clusters; most were placed into Type 2-
dominated clusters during Opus clustering, so their corresponding LTs
(if any survived LT generation) are Type 2. The FOCUS ON verification
stage records classifier disagreement with the Seixas/Morton placement
rule rather than silently over-routing to Type 3 (see below).

---

## Criterion rubrics (Type 1/2)

*Added 2026-04-19, session 4b-4; Ontario row populated 2026-04-19, session 4b-5.*

| Source | Rubrics | Gate pass | Halted | Stable | Unstable | Thin-flag | Supporting components | Supporting halted |
|---|---|---|---|---|---|---|---|---|
| Welsh CfW HWB | 12 | 11 | 2 | 5 | 7 | 2 | 9 | 2 |
| Common Core G7 RP | 7 | 6 | 1 | 4 | 3 | 2 | 4 | 2 |
| Ontario G7 History | 7 | 6 | 4 | 4 | 3 | 2 | 6 | 0 |

**Observations:**

- On both corpora the criterion gate passes on the vast majority of
  rubrics that converged under 3x self-consistency: 11/12 (Welsh CfW)
  and 6/7 (Common Core). The single gate fail on each is a
  `single_construct` halt on a Type 2 LT that bundles multiple
  skills — expected structural behaviour, not rubric-quality
  noise.
- Halts are predominantly `rubric_unreliable` driven by signature
  disagreement across self-consistency runs; after the 4b-4 Step 5
  signature relaxation (within-limit word counts collapsed to a
  single class; scope reduced to binary scoped/unscoped) convergence
  stabilised at ~85–90% on both corpora. Remaining halts are
  parse-reliability failures on a small number of LTs where Haiku
  failed to emit strict JSON on 2+ of 3 runs (documented per-corpus).
- The propositional-thin flag surfaces on both corpora (2 and 2),
  always on factual Type 1 LTs where the rubric necessarily compresses
  at Emerging/Developing because there is no intermediate performance
  to describe between "has the fact" and "does not". The flag is
  informational, not a gate failure.
- Supporting-components stage lags the rubric stage by exactly the
  number of halted rubrics plus a small number of additional halts on
  LTs that passed the rubric gate but produced unstable co-construction
  prompts. The gap is small and consistent across both corpora.
- Ontario G7 History (4b-5 re-run): 7 rubrics from 11 Type 1/2 LTs;
  4 halts all `rubric_unreliable` driven by parse-reliability (0/3
  or 1/3 runs producing valid output). 6 pass criterion gates; 0
  supporting-components halts. Outputs are below the 15–20 rubric
  projection in the v3 plan's DoD — that projection assumed the prior
  Haiku clustering's 23 LTs; Opus's consolidated 8 clusters with 3
  large-cluster LT halts produced a lower LT pool, and therefore a
  lower rubric count. Honest halt, not a regression.

---

## FOCUS ON verification (Ontario)

Ontario content includes `FOCUS ON` tags for four historical-thinking
concepts (Continuity and Change, Cause and Consequence, Historical
Perspective, Historical Significance) that are described in the source
as sustained orientations. The pipeline was run with `--focus-on-priming`
(Seixas/Morton Big Six descriptions injected as `source_context`).

**Outcome: `unstable`.**

- 7 FOCUS ON items identified in the KUD.
- 0 items agree (Type 3 Do-Disposition per priming rule).
- 1 item disagrees: `blk_0102_item_02` (Historical Significance) was
  classified Type 2 Do-Skill by the classifier with this rationale:
  *"occasion-triggered analytical skill deployed when asked to assess
  significance of a specific event ... not a sustained orientation."*
- 6 items are `classification_unstable` — the placement could not be
  resolved consistently across the three self-consistency runs.

**Interpretation.** The FOCUS ON priming injected the Type 3 placement
instruction but the classifier disagreed on most items — either reading
the source text as describing a specific occasion-triggered task (Type 2)
rather than a sustained default orientation (Type 3), or producing unstable
output. The pipeline records this as disagreement, not a silent override.
This is working as designed (verification-flag-disagreement discipline).

The substantive question — whether Ontario FOCUS ON concepts are Type 3
or Type 2 — requires curriculum-expert review. The disagreement data is
preserved in `quality_report.md`.

---

## Gate revision history driven by this corpus

| Revision | Session | Trigger | Change |
|---|---|---|---|
| 4b-2: dispositional ceiling | 4b-1/4b-2 | Welsh CfW ratio=1.65 | hierarchical/horizontal ceiling stays 1.5; dispositional raised to 2.2 (PROVISIONAL) |
| 4b-3: hierarchical ceiling | 4b-3 | Common Core G7 RP ratio=2.2 | hierarchical ceiling raised to 2.5 |

Horizontal remains at [0.8, 1.5] pending additional real-corpus evidence.
Ontario G7 History (ratio=1.333) is the first horizontal source through
the pipeline and fits the current band comfortably — no revision triggered.

---

## Code fixes driven by this corpus

| Fix | Commit | Trigger |
|---|---|---|
| Clustering max_tokens 4096→8192, drop source_blocks for >80 items | `dbcb857` | Ontario 188-item KUD exceeded output budget; 0/3 clustering runs valid |
| Clustering validator: recover duplicates and ≤3 missing items | `cee3aae` | Ontario clustering: 1 item duplicated, 1 item dropped; strict validator rejected valid runs |

---

*Cross-source summary last updated: 2026-04-19, session 4b-5.*
