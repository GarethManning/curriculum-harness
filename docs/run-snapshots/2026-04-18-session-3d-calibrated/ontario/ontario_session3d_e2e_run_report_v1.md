# Curriculum Harness run report

**Run ID:** ontario_session3d_e2e
**Output directory:** `/Users/garethmanning/Github/curriculum-harness/outputs/ontario-2026-04-18-session-3d-e2e`

## Output-shape discipline (Session 3c)

- **Output mode:** `curriculum`
- KUD / map artefact kind: `kud`
- KUD / map artefact path: `/Users/garethmanning/Github/curriculum-harness/outputs/ontario-2026-04-18-session-3d-e2e/ontario_session3d_e2e_kud_v1.json`
- Curriculum mode: full KUD emitted (know, understand, do_skills, do_dispositions).

## Source language (Session 3c)

- Detected language: `en`
- Signal: {'status': 'measured', 'total_tokens': 10427, 'en_stopword_hits': 4493, 'en_stopword_ratio': 0.4309, 'threshold': 0.05}
- Phase 4 regeneration loop retries all FAIL_SET flags normally.

## Source bullets

- Count: 937
- Artefact: `/Users/garethmanning/Github/curriculum-harness/outputs/ontario-2026-04-18-session-3d-e2e/ontario_session3d_e2e_source_bullets_v1.json`

## Curriculum profile

- document_family: national_framework
- level_model: multi_level_progression
- scoping_strategy: grade_subject_filter
- lt_statement_format (profile output_conventions): i_can
- lt_statement_format (resolved for pipeline): i_can
- recommended_adjacent_radius (product default ±1): 1
- confidence: high
- Profile JSON: `/Users/garethmanning/Github/curriculum-harness/outputs/ontario-2026-04-18-session-3d-e2e/ontario_session3d_e2e_curriculum_profile_v1.json`

_Classification notes:_ Ontario Curriculum Grades 1–8 (2023) is a provincial framework spanning multiple grade levels. Document targets Grade 7 History but encompasses K–8 progression. Contains learning expectations, achievement levels, and assessment guidance but no exam specifications or mark schemes.


## Curriculum coverage (content themes)

_These strands describe topic or period coverage. They are **not** used for learning-target assignment in Phase 5._

- **New France Era Content** (`new-france-period`): Specific historical period content (1713-1800) that serves as curriculum coverage but does not define learning target types.
- **Early Canada Era Content** (`early-canada-period`): Specific historical period content (1800-1850) covering distinct themes and events for curriculum completeness.
- **Indigenous Perspectives Integration** (`indigenous-perspectives`): Thematic focus on First Nations, Métis, and Inuit experiences across both time periods rather than a skill framework.

## Learning targets

- Count by type: 1=5, 2=10, 3=3
- Word count stats: min=12, max=24, mean=15.6
- Items with any validation flag: 17
- Total flags across items: 18
- HE disposition inferred (Phase 4 supplement): 0

## Phase 3 profile-conditional branch (Session 3b)

- Branch selected: **strand_aggregated**
- Input source bullets: 937
- Output KUD items: 18
- Merge events (per_bullet only): 0

## Phase 3 recall filter

- recall_filtered_count: 0

## Source faithfulness flagging (Session 3a)

- Phase 3 KUD items flagged SOURCE_FAITHFULNESS_FAIL: 16
- Phase 4 LTs flagged SOURCE_FAITHFULNESS_FAIL: 17

## Regeneration loop (Session 3c)

- Total LTs that entered regeneration: 18
- LTs that exhausted the retry budget: 17
- Regeneration artefact: `/Users/garethmanning/Github/curriculum-harness/outputs/ontario-2026-04-18-session-3d-e2e/ontario_session3d_e2e_regeneration_events_v1.json`
  - outcome `exhausted_retries`: 17
  - outcome `success@retry_1`: 1

_Human-review entries (budget exhausted):_
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- `(no sb_ids)` → flags: [SOURCE_FAITHFULNESS_FAIL]; outcome: exhausted_retries
- _…and 5 more_

## Flags (unique)

- Learning target flags: ['COMPOUND_TYPE', 'SOURCE_FAITHFULNESS_FAIL']
- Structured LT (Phase 5) flags: ['COMPETENCY_MAPPING_UNCERTAIN', 'COMPOUND_TYPE', 'SOURCE_FAITHFULNESS_FAIL']

## Comparison note

_Reserved for manual comparison against the validation experiment._

## Phase 5 structured output

- Competency groups: 4
- Group LT counts: {'Chronological Knowledge Progression': 5, 'Historical Concepts Thinking': 3, 'Historical Thinking And Inquiry': 7, 'Historical Empathy Development': 3}
- Level columns generated: ['Grade 7']
- COMPETENCY_MAPPING_UNCERTAIN count: 2
- Structured JSON path: `/Users/garethmanning/Github/curriculum-harness/outputs/ontario-2026-04-18-session-3d-e2e/ontario_session3d_e2e_structured_lts_v1.json`
- Structured CSV path: `/Users/garethmanning/Github/curriculum-harness/outputs/ontario-2026-04-18-session-3d-e2e/ontario_session3d_e2e_structured_lts_v1.csv`

## Phase errors
