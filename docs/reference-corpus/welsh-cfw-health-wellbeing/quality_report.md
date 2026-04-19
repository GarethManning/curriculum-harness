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

## Stage: source-native progression structure

- source type: `welsh_cfw_aole`
- band count: **5**
- band labels: Progression Step 1, Progression Step 2, Progression Step 3, Progression Step 4, Progression Step 5
- age range hint: ages 3-16 (Welsh Government Curriculum for Wales overview, statutory under the Curriculum and Assessment (Wales) Act 2021)
- detection confidence: `high`
- detection rationale: URL host hwb.gov.wales with /curriculum-for-wales path — Welsh Curriculum for Wales uses Progression Steps 1-5 across ages 3-16 per Welsh Government statutory specification.

## Stage: competency clustering

- clusters: **9**
- overall stability flag: `cluster_unstable`
- diagnostics:
  - cluster_count_differs: counts across runs = [9, 8, 8]
  - cluster_missing_in_run2: canonical clusters [8] have no Jaccard>=0.30 match
  - cluster_missing_in_run3: canonical clusters [8] have no Jaccard>=0.30 match
- per-cluster stability:
  - `cluster_01` (Physical Health and Well-being): stable — 4 items, dkt=Type 1
  - `cluster_02` (Self-Care and Respect for Self and Others): stable — 2 items, dkt=Type 3
  - `cluster_03` (Mental Health and Emotional Well-being): stable — 3 items, dkt=Type 1
  - `cluster_04` (Communication About Mental Health): stable — 2 items, dkt=Type 2
  - `cluster_05` (Informed Decision-Making): stable — 6 items, dkt=Type 2
  - `cluster_06` (Career Pathway Decision-Making): stable — 1 items, dkt=Type 1
  - `cluster_07` (Understanding Social Influences): stable — 6 items, dkt=Type 1
  - `cluster_08` (Healthy Relationships and Belonging): stable — 7 items, dkt=Type 3
  - `cluster_09` (Recognising and Responding to Unhealthy Relationships): cluster_unstable — 2 items, dkt=Type 2

## Stage: LT generation

- LTs: **20** (halted clusters: 0)
- knowledge-type split: Type 1=8, Type 2=6, Type 3=6
- LT stability: {'stable': 13, 'lt_set_unstable': 7}

## Stage: Type 1/2 band statements

- band sets: **11** (halted LTs: 3)
- stability: {'band_statements_unstable': 5, 'stable': 6}
- halted:
  - `cluster_01_lt_01`: band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Progression Step 1', 'medium'), ('Progression Step 2', 'medium'), ('Progression Step 3', 'medium'), ('Progression Step 4', 'medium'), ('Progression Step 5', 'long')), (('Progression Step 1', 'short'), ('Progression Step 2', 'short'), ('Progression Step 3', 'medium'), ('Progression Step 4', 'medium'), ('Progression Step 5', 'medium')), (('Progression Step 1', 'medium'), ('Progression Step 2', 'medium'), ('Progression Step 3', 'medium'), ('Progression Step 4', 'medium'), ('Progression Step 5', 'medium'))]
  - `cluster_02_lt_02`: band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Progression Step 1', 'medium'), ('Progression Step 2', 'medium'), ('Progression Step 3', 'long'), ('Progression Step 4', 'long'), ('Progression Step 5', 'long')), (('Progression Step 1', 'short'), ('Progression Step 2', 'medium'), ('Progression Step 3', 'medium'), ('Progression Step 4', 'medium'), ('Progression Step 5', 'long')), (('Progression Step 1', 'medium'), ('Progression Step 2', 'medium'), ('Progression Step 3', 'medium'), ('Progression Step 4', 'long'), ('Progression Step 5', 'long'))]
  - `cluster_04_lt_01`: band_statements_gate_failed — 1 format/quality failures

## Stage: Type 3 observation indicators

- indicator sets: **5** (halted LTs: 1)
- stability: {'observation_indicators_unstable': 3, 'stable': 2}
- halted:
  - `cluster_08_lt_02`: observation_indicators_unreliable — no signature reached 2/3 agreement; signatures=[(('Progression Step 1', 3), ('Progression Step 2', 3), ('Progression Step 3', 3), ('Progression Step 4', 3), ('Progression Step 5', 3), ('parents', 3)), (('Progression Step 1', 2), ('Progression Step 2', 2), ('Progression Step 3', 3), ('Progression Step 4', 3), ('Progression Step 5', 3), ('parents', 3)), (('Progression Step 1', 2), ('Progression Step 2', 3), ('Progression Step 3', 3), ('Progression Step 4', 3), ('Progression Step 5', 3), ('parents', 3))]

