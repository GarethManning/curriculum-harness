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

