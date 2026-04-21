# KUD quality report — strand-grade-band-9-10

**Overall:** HALTED
**Halted by gate:** `artefact_count_ratio`

## Summary

- **source_domain:** dispositional
- **inventory_blocks_total:** 11
- **inventory_non_heading_blocks:** 5
- **kud_items_total:** 28
- **halted_blocks_total:** 0
- **halted_severe:** 0
- **halted_unreliable:** 0
- **knowledge_type_distribution:** Type 1=1, Type 2=20, Type 3=7
- **kud_column_distribution:** do_disposition=7, do_skill=20, understand=1
- **stability_distribution:** classification_unstable=6, stable=22
- **underspecification_distribution:** null=28

## Gate results

### `source_coverage` — PASS

all non-severe, non-unreliable inventory blocks produced ≥1 KUD item

### `traceability` — PASS

every KUD item has a valid source_block_id

### `artefact_count_ratio` — FAIL (halts)

KUD items / expected-yield blocks = 28/5 = 5.600 (denominator excludes 0 severely-underspecified blocks) outside dispositional-domain target band [0.8, 2.2] (dispositional ceiling is PROVISIONAL per 4b-2; next dispositional source may re-trigger review)

### `type3_distribution` — PASS

Type 3 items = 7/28 = 25.0% (≥20% expected for dispositional domain)

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
  - `cluster_01` (Self-Awareness): stable — 5 items, dkt=Type 2
  - `cluster_02` (Self-Management): stable — 6 items, dkt=Type 2
  - `cluster_03` (Social Awareness): stable — 6 items, dkt=Type 3
  - `cluster_04` (Relationship Skills): stable — 5 items, dkt=Type 2
  - `cluster_05` (Responsible Decision-Making): stable — 6 items, dkt=Type 2

## Stage: LT generation

- LTs: **13** (halted clusters: 0)
- knowledge-type split: Type 1=0, Type 2=9, Type 3=4
- LT stability: {'stable': 8, 'lt_set_unstable': 5}

## Stage: Type 1/2 band statements

- band sets: **4** (halted LTs: 5)
- stability: {'band_statements_unstable': 2, 'stable': 2}
- halted:
  - `cluster_01_lt_02`: band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'long'), ('Grade Band 11-12', 'long')), (('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'long')), (('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium'))]
  - `cluster_01_lt_03`: band_statements_gate_failed — 2 format/quality failures
  - `cluster_04_lt_01`: band_statements_gate_failed — 4 format/quality failures
  - `cluster_04_lt_02`: band_statements_gate_failed — 1 format/quality failures
  - `cluster_05_lt_01`: band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium')), (('Pre-Kindergarten', 'short'), ('Kindergarten-Grade 1', 'short'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium')), (('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'long'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'long'))]

## Stage: Type 3 observation indicators

- indicator sets: **4** (halted LTs: 0)
- stability: {'stable': 3, 'observation_indicators_unstable': 1}


## Flags
Total flags: **12**


### `cluster_03_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_03_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_03_lt_03` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_05_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_05_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_01_lt_02` — `band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'long'), ('Grade Band 11-12', 'long')), (('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'long')), (('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium'))]` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_01_lt_03` — `band_statements_unreliable — 2 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_04_lt_01` — `band_statements_unreliable — 4 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_04_lt_02` — `band_statements_unreliable — 1 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_05_lt_01` — `band_statements_unreliable — no word-count-class signature reached 2/3 agreement; signatures=[(('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium')), (('Pre-Kindergarten', 'short'), ('Kindergarten-Grade 1', 'short'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'medium'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'medium')), (('Pre-Kindergarten', 'medium'), ('Kindergarten-Grade 1', 'medium'), ('Grade Band 2-3', 'medium'), ('Grade Band 4-5', 'medium'), ('Grade Band 6-8', 'long'), ('Grade Band 9-10', 'medium'), ('Grade Band 11-12', 'long'))]` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_01_lt_01` — `band_statements_unstable` — **MEDIUM**

**Stage:** band statements

**Technical:** Band statement generation reached 2/3 agreement but not 3/3 stability. The majority-vote statements were retained.

**Pedagogical:** The band-level statements may be rephrased differently in alternative valid runs. The substance is stable but specific wording should be reviewed by a teacher before use.

### `cluster_03_lt_01` — `band_statements_unstable` — **MEDIUM**

**Stage:** band statements

**Technical:** Band statement generation reached 2/3 agreement but not 3/3 stability. The majority-vote statements were retained.

**Pedagogical:** The band-level statements may be rephrased differently in alternative valid runs. The substance is stable but specific wording should be reviewed by a teacher before use.

