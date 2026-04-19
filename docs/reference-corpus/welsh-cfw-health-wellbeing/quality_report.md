# KUD quality report — wales-cfw-health-wellbeing-sow

**Overall:** PASSED

## Summary

- **source_domain:** dispositional
- **inventory_blocks_total:** 26
- **inventory_non_heading_blocks:** 24
- **kud_items_total:** 33
- **halted_blocks_total:** 6
- **halted_severe:** 4
- **halted_unreliable:** 2
- **knowledge_type_distribution:** Type 1=21, Type 2=5, Type 3=7
- **kud_column_distribution:** do_disposition=7, do_skill=7, know=1, understand=18
- **stability_distribution:** classification_unstable=17, stable=16
- **underspecification_distribution:** mild=6, moderate=20, null=7

## Gate results

### `source_coverage` — PASS

all non-severe, non-unreliable inventory blocks produced ≥1 KUD item

### `traceability` — PASS

every KUD item has a valid source_block_id

### `artefact_count_ratio` — PASS

KUD items / expected-yield blocks = 33/20 = 1.650 (denominator excludes 4 severely-underspecified blocks) within dispositional-domain target [0.8, 2.2] (dispositional ceiling is PROVISIONAL per 4b-2; next dispositional source may re-trigger review)

### `type3_distribution` — PASS

Type 3 items = 7/33 = 21.2% (≥20% expected for dispositional domain)

### `no_compound_unsplit` — PASS

every KUD item carries a single knowledge type with consistent column and route

## Stage: competency clustering

- clusters: **8**
- overall stability flag: `cluster_unstable`
- diagnostics:
  - cluster_count_differs: counts across runs = [8, 6, 8]
  - cluster_missing_in_run2: canonical clusters [3, 5] have no Jaccard>=0.30 match
  - dominant_type_drift_run2: canonical cluster 4 (Type 1) → run2 cluster 3 (Type 2)
  - dominant_type_drift_run3: canonical cluster 4 (Type 1) → run3 cluster 4 (Type 2)
- per-cluster stability:
  - `cluster_01` (Physical Health and Well-being): stable — 4 items, dkt=Type 1
  - `cluster_02` (Self-Care and Respect for Self and Others): stable — 2 items, dkt=Type 3
  - `cluster_03` (Emotional Awareness and Regulation): stable — 3 items, dkt=Type 1
  - `cluster_04` (Communication About Mental Health): cluster_unstable — 2 items, dkt=Type 2
  - `cluster_05` (Informed Decision-Making): cluster_unstable — 6 items, dkt=Type 1
  - `cluster_06` (Career Pathway Planning): cluster_unstable — 1 items, dkt=Type 1
  - `cluster_07` (Understanding Social Influences): stable — 6 items, dkt=Type 1
  - `cluster_08` (Healthy Relationships): stable — 9 items, dkt=Type 3

## Stage: LT generation

- LTs: **19** (halted clusters: 0)
- knowledge-type split: Type 1=8, Type 2=4, Type 3=7
- LT stability: {'stable': 14, 'lt_set_unstable': 5}

## Stage: Type 1/2 band statements

- band sets: **12** (halted LTs: 0)
- stability: {'band_statements_unstable': 8, 'stable': 4}

## Stage: Type 3 observation indicators

- indicator sets: **7** (halted LTs: 0)
- stability: {'stable': 7}

