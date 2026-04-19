# KUD quality report — 2a-regression-common-core-7rp

**Overall:** PASSED

## Summary

- **source_domain:** hierarchical
- **inventory_blocks_total:** 18
- **inventory_non_heading_blocks:** 18
- **kud_items_total:** 22
- **halted_blocks_total:** 8
- **halted_severe:** 8
- **halted_unreliable:** 0
- **knowledge_type_distribution:** Type 1=21, Type 2=1
- **kud_column_distribution:** do_skill=11, know=4, understand=7
- **stability_distribution:** classification_unstable=9, stable=13
- **underspecification_distribution:** mild=7, null=15

## Gate results

### `source_coverage` — PASS

all non-severe, non-unreliable inventory blocks produced ≥1 KUD item

### `traceability` — PASS

every KUD item has a valid source_block_id

### `artefact_count_ratio` — PASS

KUD items / expected-yield blocks = 22/10 = 2.200 (denominator excludes 8 severely-underspecified blocks) within hierarchical-domain target [0.8, 2.5]

### `type3_distribution` — PASS

type3_distribution gate skipped — source is not marked as dispositional-domain

### `no_compound_unsplit` — PASS

every KUD item carries a single knowledge type with consistent column and route

## Stage: source-native progression structure

- source type: `us_common_core_grade`
- band count: **1**
- band labels: Grade 7
- age range hint: ages 12-13 (Common Core State Standards Initiative; CCSSO grade alignment)
- detection confidence: `high`
- detection rationale: Common Core source detected (host=thecorestandards.org, slug=2a-regression-common-core-7rp); grade 7 extracted. Single-grade source — band_count=1.

## Stage: competency clustering

- clusters: **4**
- overall stability flag: `cluster_unstable`
- diagnostics:
  - dominant_type_drift_run2: canonical cluster 3 (Type 2) → run2 cluster 3 (Type 1)
  - dominant_type_drift_run3: canonical cluster 3 (Type 2) → run3 cluster 3 (Type 1)
- per-cluster stability:
  - `cluster_01` (Computing Unit Rates): stable — 4 items, dkt=Type 1
  - `cluster_02` (Recognizing and Representing Proportional Relationships): stable — 8 items, dkt=Type 1
  - `cluster_03` (Identifying and Using the Constant of Proportionality): stable — 7 items, dkt=Type 1
  - `cluster_04` (Solving Real-World Proportional Relationship Problems): cluster_unstable — 3 items, dkt=Type 2

## Stage: LT generation

- LTs: **8** (halted clusters: 0)
- knowledge-type split: Type 1=6, Type 2=2, Type 3=0
- LT stability: {'stable': 4, 'lt_set_unstable': 4}

## Stage: Type 1/2 band statements

- band sets: **6** (halted LTs: 2)
- stability: {'stable': 5, 'band_statements_unstable': 1}
- halted:
  - `cluster_01_lt_01`: band_statements_gate_failed — 1 format/quality failures
  - `cluster_04_lt_01`: band_statements_gate_failed — 1 format/quality failures

## Stage: Type 3 observation indicators

- indicator sets: **0** (halted LTs: 0)
- stability: {}

