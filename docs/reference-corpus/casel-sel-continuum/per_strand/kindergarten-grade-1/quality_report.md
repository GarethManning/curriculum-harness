# KUD quality report — strand-kindergarten-grade-1

**Overall:** HALTED
**Halted by gate:** `artefact_count_ratio`

## Summary

- **source_domain:** dispositional
- **inventory_blocks_total:** 11
- **inventory_non_heading_blocks:** 5
- **kud_items_total:** 29
- **halted_blocks_total:** 0
- **halted_severe:** 0
- **halted_unreliable:** 0
- **knowledge_type_distribution:** Type 1=9, Type 2=12, Type 3=8
- **kud_column_distribution:** do_disposition=8, do_skill=14, know=5, understand=2
- **stability_distribution:** classification_unstable=11, stable=18
- **underspecification_distribution:** null=29

## Gate results

### `source_coverage` — PASS

all non-severe, non-unreliable inventory blocks produced ≥1 KUD item

### `traceability` — PASS

every KUD item has a valid source_block_id

### `artefact_count_ratio` — FAIL (halts)

KUD items / expected-yield blocks = 29/5 = 5.800 (denominator excludes 0 severely-underspecified blocks) outside dispositional-domain target band [0.8, 2.2] (dispositional ceiling is PROVISIONAL per 4b-2; next dispositional source may re-trigger review)

### `type3_distribution` — PASS

Type 3 items = 8/29 = 27.6% (≥20% expected for dispositional domain)

### `no_compound_unsplit` — PASS

every KUD item carries a single knowledge type with consistent column and route

## Stage: source-native progression structure

- source type: `casel_sel_grade_band`
- band count: **7**
- band labels: Pre-Kindergarten, Kindergarten-Grade 1, Grade Band 2-3, Grade Band 4-5, Grade Band 6-8, Grade Band 9-10, Grade Band 11-12
- age range hint: ages 3-18 (CASEL SEL Skills Continuum 2023; Pre-K through Grade 11-12; Adults band excluded as out of K-12 curriculum scope)
- detection confidence: `high`
- detection rationale: CASEL source detected (host=drc.casel.org). 7-band structure: Pre-Kindergarten through Grade Band 11-12 (Adults excluded).

## Stage: competency clustering

- clusters: **5**
- overall stability flag: `stable`
- per-cluster stability:
  - `cluster_01` (Self-Awareness): stable — 5 items, dkt=Type 1
  - `cluster_02` (Self-Management): stable — 6 items, dkt=Type 2
  - `cluster_03` (Social Awareness): stable — 6 items, dkt=Type 1
  - `cluster_04` (Relationship Skills): stable — 6 items, dkt=Type 3
  - `cluster_05` (Responsible Decision-Making): stable — 6 items, dkt=Type 2

## Stage: LT generation

- LTs: **15** (halted clusters: 0)
- knowledge-type split: Type 1=3, Type 2=7, Type 3=5
- LT stability: {'stable': 15}

## Stage: Type 1/2 band statements

- band sets: **3** (halted LTs: 7)
- stability: {'stable': 2, 'band_statements_unstable': 1}
- halted:
  - `cluster_01_lt_02`: band_statements_gate_failed — 2 format/quality failures
  - `cluster_02_lt_01`: band_statements_gate_failed — 2 format/quality failures
  - `cluster_02_lt_02`: band_statements_gate_failed — 1 format/quality failures
  - `cluster_03_lt_02`: band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium')), (('Pre-Kindergarten', 'long'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'long'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'long'), ('Grade Band 9-10', 'long'), ('Grade Band 11-12', 'long')), (('Pre-Kindergarten', 'long'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'long'), ('Grade Band 11-12', 'long'))]
  - `cluster_04_lt_01`: band_statements_gate_failed — 2 format/quality failures
  - `cluster_05_lt_01`: band_statements_gate_failed — 1 format/quality failures
  - `cluster_05_lt_03`: band_statements_gate_failed — 7 format/quality failures

## Stage: Type 3 observation indicators

- indicator sets: **5** (halted LTs: 0)
- stability: {'stable': 4, 'observation_indicators_unstable': 1}


## Flags
Total flags: **8**


### `cluster_01_lt_02` — `band_statements_unreliable — 2 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_02_lt_01` — `band_statements_unreliable — 2 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_02_lt_02` — `band_statements_unreliable — 1 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_03_lt_02` — `band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium')), (('Pre-Kindergarten', 'long'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'long'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'long'), ('Grade Band 9-10', 'long'), ('Grade Band 11-12', 'long')), (('Pre-Kindergarten', 'long'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'long'), ('Grade Band 11-12', 'long'))]` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_04_lt_01` — `band_statements_unreliable — 2 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_05_lt_01` — `band_statements_unreliable — 1 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_05_lt_03` — `band_statements_unreliable — 7 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_03_lt_01` — `band_statements_unstable` — **MEDIUM**

**Stage:** band statements

**Technical:** Band statement generation reached 2/3 agreement but not 3/3 stability. The majority-vote statements were retained.

**Pedagogical:** The band-level statements may be rephrased differently in alternative valid runs. The substance is stable but specific wording should be reviewed by a teacher before use.

