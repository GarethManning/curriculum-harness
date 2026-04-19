# KUD quality report — 5-ontario-k8-g7-history-pdf

**Overall:** PASSED

## Summary

- **source_domain:** horizontal
- **inventory_blocks_total:** 259
- **inventory_non_heading_blocks:** 259
- **kud_items_total:** 188
- **halted_blocks_total:** 129
- **halted_severe:** 118
- **halted_unreliable:** 11
- **knowledge_type_distribution:** Type 1=62, Type 2=110, Type 3=16
- **kud_column_distribution:** do_disposition=16, do_skill=117, know=51, understand=4
- **stability_distribution:** classification_unstable=84, stable=104
- **underspecification_distribution:** mild=71, moderate=16, null=101

## Gate results

### `source_coverage` — PASS

all non-severe, non-unreliable inventory blocks produced ≥1 KUD item

### `traceability` — PASS

every KUD item has a valid source_block_id

### `artefact_count_ratio` — PASS

KUD items / expected-yield blocks = 188/141 = 1.333 (denominator excludes 118 severely-underspecified blocks) within horizontal-domain target [0.8, 1.5]

### `type3_distribution` — PASS

type3_distribution gate skipped — source is not marked as dispositional-domain

### `no_compound_unsplit` — PASS

every KUD item carries a single knowledge type with consistent column and route

## Stage: source-native progression structure

- source type: `ontario_grade`
- band count: **1**
- band labels: Grade 7
- age range hint: ages 12-13 (Ontario Ministry of Education K-12 schedule)
- detection confidence: `high`
- detection rationale: Source slug '5-ontario-k8-g7-history-pdf' matches Ontario pattern; grade 7 extracted. Single-grade source — band_count=1.

## Stage: competency clustering

- clusters: **11**
- overall stability flag: `cluster_unstable`
- diagnostics:
  - cluster_count_differs: counts across runs = [11, 15]
  - cluster_missing_in_run2: canonical clusters [3, 5, 9] have no Jaccard>=0.30 match
  - membership_drift_run2: 43.09% of items reassigned vs run1 (threshold 20%)
  - dominant_type_drift_run2: canonical cluster 10 (Type 2) → run2 cluster 14 (Type 3)
- per-cluster stability:
  - `cluster_01` (Historical Evidence Analysis and Source Evaluation): stable — 9 items, dkt=Type 2
  - `cluster_02` (Cartographic Analysis and Map Use): stable — 15 items, dkt=Type 1
  - `cluster_03` (Contextual Understanding and Anti-Presentism): stable — 16 items, dkt=Type 3
  - `cluster_04` (Indigenous Experiences and Perspectives in Colonial Canada (1713–1800)): cluster_unstable — 26 items, dkt=Type 2
  - `cluster_05` (Displacement and Forced Migration in Canadian History): stable — 13 items, dkt=Type 2
  - `cluster_06` (Continuity and Change Across Time Periods): cluster_unstable — 5 items, dkt=Type 2
  - `cluster_07` (Multiple Perspectives and Historical Interpretation): stable — 60 items, dkt=Type 2
  - `cluster_08` (Factual Knowledge of Key Events, Treaties, and Policies): stable — 38 items, dkt=Type 1
  - `cluster_09` (Historical Communication and Vocabulary): stable — 3 items, dkt=Type 2
  - `cluster_10` (Fur Trade, Economic Systems, and Social Change): cluster_unstable — 2 items, dkt=Type 2
  - `cluster_11` (Immigration, Settlement, and Community Formation): cluster_unstable — 1 items, dkt=Type 2

## Stage: LT generation

- LTs: **23** (halted clusters: 1)
- knowledge-type split: Type 1=7, Type 2=14, Type 3=2
- LT stability: {'lt_set_unstable': 10, 'stable': 13}
- halted clusters:
  - `cluster_04`: lt_set_unreliable — only 0/3 runs produced parseable output

## Stage: Type 1/2 band statements

- band sets: **21** (halted LTs: 0)
- stability: {'stable': 18, 'band_statements_unstable': 3}

## Stage: Type 3 observation indicators

- indicator sets: **2** (halted LTs: 0)
- stability: {'stable': 2}

## Stage: FOCUS ON placement-rule verification (Ontario)

- **outcome:** `unstable`
- focus_on_items identified: ['blk_0088_item_02', 'blk_0102_item_02', 'blk_0144_item_02', 'blk_0193_item_02', 'blk_0226_item_01', 'blk_0256_item_01', 'blk_0258_item_02']
- agrees (Type 3 Do-Disposition): []
- **disagrees (classifier routed differently — placement rule not silently overridden):**
  - `blk_0102_item_02` classified as do_skill/Type 2: This is an occasion-triggered analytical skill deployed when asked to assess significance of a specific event. The learner must reason through multiple perspectives and recognise that significance is not fixed but contingent on standpoint and context. This is a reasoning task that develops through repeated application, not a sustained orientation. It aligns with Type 2 Do-Skill (reasoning_quality_rubric) and operationalises the FOCUS ON: Historical Significance concept as an occasion-triggered analytical practice.
- **unstable:** ['blk_0088_item_02', 'blk_0144_item_02', 'blk_0193_item_02', 'blk_0226_item_01', 'blk_0256_item_01', 'blk_0258_item_02']

