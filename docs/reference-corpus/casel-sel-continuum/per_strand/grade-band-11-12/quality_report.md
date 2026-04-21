# KUD quality report — strand-grade-band-11-12

**Overall:** HALTED
**Halted by gate:** `artefact_count_ratio`

## Summary

- **source_domain:** dispositional
- **inventory_blocks_total:** 11
- **inventory_non_heading_blocks:** 5
- **kud_items_total:** 0
- **halted_blocks_total:** 5
- **halted_severe:** 0
- **halted_unreliable:** 5
- **knowledge_type_distribution:** (empty)
- **kud_column_distribution:** (empty)
- **stability_distribution:** (empty)
- **underspecification_distribution:** (empty)

## Gate results

### `source_coverage` — PASS

all non-severe, non-unreliable inventory blocks produced ≥1 KUD item

### `traceability` — PASS

every KUD item has a valid source_block_id

### `artefact_count_ratio` — FAIL (halts)

KUD items / expected-yield blocks = 0/5 = 0.000 (denominator excludes 0 severely-underspecified blocks) outside dispositional-domain target band [0.8, 2.2] (dispositional ceiling is PROVISIONAL per 4b-2; next dispositional source may re-trigger review)

### `type3_distribution` — FLAG

dispositional_content_underrepresented: Type 3 items = 0/0 = 0.0% < expected ≥20% for dispositional domain (informational only)

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

- clusters: **0**
- overall stability flag: `cluster_unreliable`
- diagnostics:
  - only 0/3 clustering runs produced valid output
- per-cluster stability:

## Stage: LT generation

- LTs: **0** (halted clusters: 0)
- knowledge-type split: Type 1=0, Type 2=0, Type 3=0
- LT stability: {}

## Stage: Type 1/2 band statements

- band sets: **0** (halted LTs: 0)
- stability: {}

## Stage: Type 3 observation indicators

- indicator sets: **0** (halted LTs: 0)
- stability: {}


## Flags
Total flags: **6**


### `blk_0003` — `classification_unreliable` — **MEDIUM**

**Stage:** KUD classification

**Technical:** The KUD classifier ran 3 times on this source block; fewer than 2/3 runs agreed on the knowledge type (Type 1 / 2 / 3). The block was halted rather than forced into an uncertain classification.

**Pedagogical:** If the classifier can't agree on whether this is declarative knowledge, a skill, or a disposition, the LT derived from it may not accurately reflect the source intent. A teacher should check the original source block and decide the classification manually before using this LT.

### `blk_0005` — `classification_unreliable` — **MEDIUM**

**Stage:** KUD classification

**Technical:** The KUD classifier ran 3 times on this source block; fewer than 2/3 runs agreed on the knowledge type (Type 1 / 2 / 3). The block was halted rather than forced into an uncertain classification.

**Pedagogical:** If the classifier can't agree on whether this is declarative knowledge, a skill, or a disposition, the LT derived from it may not accurately reflect the source intent. A teacher should check the original source block and decide the classification manually before using this LT.

### `blk_0007` — `classification_unreliable` — **MEDIUM**

**Stage:** KUD classification

**Technical:** The KUD classifier ran 3 times on this source block; fewer than 2/3 runs agreed on the knowledge type (Type 1 / 2 / 3). The block was halted rather than forced into an uncertain classification.

**Pedagogical:** If the classifier can't agree on whether this is declarative knowledge, a skill, or a disposition, the LT derived from it may not accurately reflect the source intent. A teacher should check the original source block and decide the classification manually before using this LT.

### `blk_0009` — `classification_unreliable` — **MEDIUM**

**Stage:** KUD classification

**Technical:** The KUD classifier ran 3 times on this source block; fewer than 2/3 runs agreed on the knowledge type (Type 1 / 2 / 3). The block was halted rather than forced into an uncertain classification.

**Pedagogical:** If the classifier can't agree on whether this is declarative knowledge, a skill, or a disposition, the LT derived from it may not accurately reflect the source intent. A teacher should check the original source block and decide the classification manually before using this LT.

### `blk_0011` — `classification_unreliable` — **MEDIUM**

**Stage:** KUD classification

**Technical:** The KUD classifier ran 3 times on this source block; fewer than 2/3 runs agreed on the knowledge type (Type 1 / 2 / 3). The block was halted rather than forced into an uncertain classification.

**Pedagogical:** If the classifier can't agree on whether this is declarative knowledge, a skill, or a disposition, the LT derived from it may not accurately reflect the source intent. A teacher should check the original source block and decide the classification manually before using this LT.

### `competency_clusters` — `cluster_unreliable (only 0/3 clustering runs produced valid output)` — **MEDIUM**

**Stage:** competency clustering

**Technical:** The cluster_unreliable flag means fewer than 2/3 clustering runs agreed on a stable cluster structure. No reliable canonical cluster set could be extracted; the pipeline continues with whatever clusters were produced in the first run.

**Pedagogical:** Without stable clusters, the LTs may not accurately group related competencies. The competency structure visible in these LTs may not reflect the source's actual organisation. Human review of the source material and the resulting LT set is strongly recommended.

