# KUD quality report — 2a-secondary-rshe-2025

**Overall:** PASSED

## Summary

- **source_domain:** dispositional
- **inventory_blocks_total:** 249
- **inventory_non_heading_blocks:** 132
- **kud_items_total:** 149
- **halted_blocks_total:** 37
- **halted_severe:** 36
- **halted_unreliable:** 1
- **knowledge_type_distribution:** Type 1=115, Type 2=29, Type 3=5
- **kud_column_distribution:** do_disposition=5, do_skill=29, know=69, understand=46
- **stability_distribution:** classification_unstable=28, stable=121
- **underspecification_distribution:** mild=1, moderate=3, null=145

## Gate results

### `source_coverage` — PASS

all non-severe, non-unreliable inventory blocks produced ≥1 KUD item

### `traceability` — PASS

every KUD item has a valid source_block_id

### `artefact_count_ratio` — PASS

KUD items / expected-yield blocks = 149/96 = 1.552 (denominator excludes 36 severely-underspecified blocks) within dispositional-domain target [0.8, 2.2] (dispositional ceiling is PROVISIONAL per 4b-2; next dispositional source may re-trigger review)

### `type3_distribution` — FLAG

dispositional_content_underrepresented: Type 3 items = 5/149 = 3.4% < expected ≥20% for dispositional domain (informational only)

### `no_compound_unsplit` — PASS

every KUD item carries a single knowledge type with consistent column and route

## Stage: source-native progression structure

- source type: `england_rshe_secondary`
- band count: **1**
- band labels: End of Secondary
- age range hint: ages 11-16 (DfE RSHE statutory guidance; secondary phase = Years 7-11, KS3 + KS4; outcomes framed as 'by the end of secondary school')
- detection confidence: `high`
- detection rationale: DfE RSHE statutory guidance detected (host=assets.publishing.service.gov.uk, path contains 'relationships'). Single-band End-of-Secondary structure (ages 11-16).

## Stage: competency clustering

- clusters: **30**
- overall stability flag: `cluster_unstable`
- diagnostics:
  - cluster_count_differs: counts across runs = [30, 29, 38]
  - cluster_missing_in_run2: canonical clusters [4, 6] have no Jaccard>=0.30 match
  - dominant_type_drift_run2: canonical cluster 10 (Type 2) → run2 cluster 8 (Type 1)
  - cluster_missing_in_run3: canonical clusters [4] have no Jaccard>=0.30 match
  - dominant_type_drift_run3: canonical cluster 3 (Type 1) → run3 cluster 3 (Type 2)
  - dominant_type_drift_run3: canonical cluster 10 (Type 2) → run3 cluster 11 (Type 1)
- per-cluster stability:
  - `cluster_01` (Family Structures and Legal Relationships): stable — 5 items, dkt=Type 1
  - `cluster_02` (Healthy Romantic Relationships): stable — 4 items, dkt=Type 1
  - `cluster_03` (Respectful Relationships and Self-Worth): stable — 6 items, dkt=Type 1
  - `cluster_04` (Addressing Bullying): cluster_unstable — 4 items, dkt=Type 1
  - `cluster_05` (Managing Relationship Endings): cluster_unstable — 1 items, dkt=Type 2
  - `cluster_06` (Recognising Stereotypes and Power Dynamics): stable — 3 items, dkt=Type 1
  - `cluster_07` (Understanding Harmful Sexual Influences): cluster_unstable — 2 items, dkt=Type 1
  - `cluster_08` (Online Safety and Privacy): stable — 6 items, dkt=Type 1
  - `cluster_09` (Managing Digital Content and Image Sharing): stable — 8 items, dkt=Type 1
  - `cluster_10` (Identifying Deepfakes and Harmful Online Content): stable — 7 items, dkt=Type 1
  - `cluster_11` (Recognising Online Abuse and Exploitation): cluster_unstable — 2 items, dkt=Type 2
  - `cluster_12` (Online Scams and Emerging Technology Risks): stable — 7 items, dkt=Type 1
  - `cluster_13` (Consent and Boundaries in Relationships): stable — 4 items, dkt=Type 2
  - `cluster_14` (Assessing Trustworthiness and Personal Safety): stable — 7 items, dkt=Type 2
  - `cluster_15` (Understanding Sexual Harassment and Violence): stable — 3 items, dkt=Type 1
  - `cluster_16` (Understanding Domestic Abuse and Exploitation): stable — 7 items, dkt=Type 1
  - `cluster_17` (Recognising Harmful Sexual Norms and Seeking Support): stable — 2 items, dkt=Type 1
  - `cluster_18` (Healthy Sexual Relationships and Consent): stable — 6 items, dkt=Type 1
  - `cluster_19` (Contraception and Pregnancy Options): stable — 3 items, dkt=Type 1
  - `cluster_20` (Sexual Health and STI Prevention): stable — 7 items, dkt=Type 1
  - `cluster_21` (Emotional Wellbeing and Mental Health Literacy): stable — 8 items, dkt=Type 1
  - `cluster_22` (Substance Use and Mental Health): stable — 3 items, dkt=Type 1
  - `cluster_23` (Digital Wellbeing and Online Harms): stable — 13 items, dkt=Type 1
  - `cluster_24` (Nutrition and Diet-Related Health): stable — 2 items, dkt=Type 1
  - `cluster_25` (Drugs, Alcohol, and Tobacco): stable — 6 items, dkt=Type 1
  - `cluster_26` (Physical Health and Preventive Care): stable — 9 items, dkt=Type 1
  - `cluster_27` (Accessing Healthcare Services): stable — 3 items, dkt=Type 1
  - `cluster_28` (Personal Safety and Risk Management): stable — 4 items, dkt=Type 2
  - `cluster_29` (Weapons, Violence, and Exploitation): stable — 3 items, dkt=Type 1
  - `cluster_30` (Reproductive Health and First Aid): stable — 4 items, dkt=Type 1

## Stage: LT generation

- LTs: **70** (halted clusters: 0)
- knowledge-type split: Type 1=42, Type 2=24, Type 3=4
- LT stability: {'stable': 56, 'lt_set_unstable': 14}

## Stage: Type 1/2 band statements

- band sets: **65** (halted LTs: 1)
- stability: {'stable': 61, 'band_statements_unstable': 4}
- halted:
  - `cluster_05_lt_01`: band_statements_gate_failed — 1 format/quality failures

## Stage: Type 3 observation indicators

- indicator sets: **4** (halted LTs: 0)
- stability: {'stable': 2, 'observation_indicators_unstable': 2}

## Stage: Type 1/2 criterion rubrics

- rubrics: **66** (halted LTs: 0)
- stability: {'stable': 36, 'rubric_unstable': 25, 'rubric_unreliable': 5}
- rubrics with gate failures: 15
- competent-framing judge: 0 fail
- propositional_lt_rubric_thin_flag: 4

### Criterion gate details

**Overall:** HALTED
**Halted by:** `criterion_gates`

## Summary

- **rubrics_total:** 66
- **rubrics_halted_lts:** 0
- **rubrics_with_gate_failures:** 15
- **rubrics_competent_judge_fail:** 0
- **rubrics_propositional_thin_flag:** 4
- **stability_distribution:** rubric_unreliable=5, rubric_unstable=25, stable=36

## Per-LT gate results

### `cluster_01_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_01_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently at the learning target's level of demand without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_02_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently demonstrates the exact capability described in the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_02_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently perform the full capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_03_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated with clear understanding and accurate connections, standing alone as evidence the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_03_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — FAIL (halts): adjacent level pairs with no topic-lemma overlap: [('emerging', 'developing')]
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently and consistently demonstrates the target skill without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_04_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently identifies' and 'explains accurately and comprehensively' without any hedging language or positioning as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_04_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently and effectively demonstrates the capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_05_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — FAIL (halts): levels without observable action verb: ['emerging', 'competent']
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'consistently ends relationships using respectful communication' and stands alone as meeting the learning target without hedging language.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_05_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_06_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently with accurate reasoning, standing alone as evidence the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_06_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently demonstrates the capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_06_lt_03`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently analyses' and 'clear reasoning and accurate connections' without any hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_07_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor directly states the learner can explain the required concept without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_07_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — FAIL (halts): levels without observable action verb: ['developing']
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, directly matching the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_08_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently perform both required capabilities without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_08_lt_03`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently demonstrate the capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_09_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner 'independently explains' the required content, demonstrating complete achievement of the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_09_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently demonstrates the full capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_10_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently explain support resources with accurate detail, demonstrating full achievement of the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_11_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — FAIL (halts): adjacent level pairs with no topic-lemma overlap: [('developing', 'competent')]
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently identify technology-enabled abuse across various contexts, which directly demonstrates meeting the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_11_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently explain the concept without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_11_lt_03`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently identify appropriate support sources, demonstrating complete mastery of the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_12_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — FAIL (halts): Competent descriptor uses deficit hedge-phrasing: ['\\bemerging\\b']
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional_lt_rubric_thin: all four applied levels share one verb bucket; structurally valid but differentiation may be thin (reviewer-confirm)

### `cluster_12_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently at the learning target's level of demand without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_13_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated independently and effectively, with no hedging language or implications of incompleteness.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_13_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently identifies and resists' and 'consistently avoiding', indicating complete mastery of the learning target.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_13_lt_03`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated by stating the learner 'explains how kindness and care requires consideration beyond basic consent' without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_14_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently assesses' using 'appropriate criteria and clear reasoning' without any hedging language or implications of incompleteness.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_15_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — FAIL (halts): adjacent level pairs with no topic-lemma overlap: [('emerging', 'developing')]
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently demonstrates the capability at the exact level specified in the learning target definition.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional_lt_rubric_thin: all four applied levels share one verb bucket; structurally valid but differentiation may be thin (reviewer-confirm)

### `cluster_15_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently with clear reasoning, standing alone as evidence the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional_lt_rubric_thin: all four applied levels share one verb bucket; structurally valid but differentiation may be thin (reviewer-confirm)

### `cluster_16_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently and accurately demonstrates the capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_16_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently explains...accurately and comprehensively' without any hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_17_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_17_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — FAIL (halts): adjacent level pairs with no topic-lemma overlap: [('competent', 'extending')]
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_18_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_18_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor directly states the learner can analyze the required concepts, demonstrating the capability independently without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_19_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated at the learning target's level of demand without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_19_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — FAIL (halts): levels without observable action verb: ['competent']
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently locates' and 'effectively' without any hedging language or implications of incompleteness.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_20_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_20_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently and accurately identify sexual health services, demonstrating complete achievement of the learning target without hedging language or dependency on higher levels.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_21_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently perform all required capabilities without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_22_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently at the learning target's level of demand without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_22_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — FAIL (halts): adjacent level pairs with no topic-lemma overlap: [('developing', 'competent'), ('competent', 'extending')]
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_23_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and consistently, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_23_lt_03`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_24_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently at the learning target's level of demand without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_24_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner 'independently identifies' the required health risks, demonstrating complete achievement of the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional_lt_rubric_thin: all four applied levels share one verb bucket; structurally valid but differentiation may be thin (reviewer-confirm)

### `cluster_25_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and comprehensively, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_25_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and comprehensively, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_26_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, which clearly indicates the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_26_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_27_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently and consistently demonstrates the target capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_27_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_28_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently identifies' and 'applies effectively' without any hedging language or positioning as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_28_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as fully demonstrated with 'independently recognises' and 'consistently applies effective strategies', indicating the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_28_lt_03`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently at the learning target's level of demand without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_29_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and can stand alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_29_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner independently demonstrates the full capability without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: propositional-thin check skipped (not Type 1)

### `cluster_30_lt_01`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — PASS: every level (except no_evidence) contains an observable action verb
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor declares the capability as demonstrated independently and accurately, standing alone as evidence that the learning target is met.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

### `cluster_30_lt_02`

- **word_limit** — PASS: all five levels within their respective word limits
- **observable_verb** — FAIL (halts): levels without observable action verb: ['competent']
- **single_construct** — PASS: adjacent applied levels share topic-lemma overlap — single construct preserved
- **no_inline_examples** — PASS: no inline examples or banned substrings in any descriptor
- **competent_framing_regex** — PASS: Competent descriptor contains no deficit hedge-phrases
- **competent_framing_judge** — PASS: LLM-as-judge verdict: pass — The descriptor clearly states the learner can independently determine when medical assistance is required, which directly demonstrates meeting the learning target without hedging language or positioning it as incomplete.
- **level_progression** — PASS: adjacent levels preserve progression roles
- **propositional_thin_flag** — PASS: verb-bucket diversity across applied levels — no thin flag

## Stage: supporting components

- components: **37** (halted LTs: 29)
- stability: {'supporting_unstable': 30, 'stable': 7}
- halted:
  - `cluster_02_lt_01`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_02_lt_02`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_05_lt_02`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_06_lt_02`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_07_lt_01`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_08_lt_01`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_18_lt_02`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_20_lt_02`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_23_lt_03`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_26_lt_01`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_27_lt_02`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_28_lt_01`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_28_lt_03`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_30_lt_01`: supporting_unreliable — no structural signature reached 2/3 agreement; signatures=[(('stages', 4), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 4), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 3), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2))), (('stages', 5), ('student_prompts', 3), ('student_rubric_levels', ('no_evidence', 'emerging', 'developing', 'competent', 'extending')), ('self_check_prompts', 2), (('moves', 'no_evidence', 2), ('moves', 'emerging', 2), ('moves', 'developing', 2), ('moves', 'competent', 2)))]
  - `cluster_03_lt_02`: supporting_skipped_gate_fail — rubric has gate failures ['single_construct']; not a stable anchor for supporting materials
  - `cluster_05_lt_01`: supporting_skipped_gate_fail — rubric has gate failures ['observable_verb']; not a stable anchor for supporting materials
  - `cluster_07_lt_02`: supporting_skipped_gate_fail — rubric has gate failures ['observable_verb']; not a stable anchor for supporting materials
  - `cluster_11_lt_01`: supporting_skipped_gate_fail — rubric has gate failures ['single_construct']; not a stable anchor for supporting materials
  - `cluster_12_lt_01`: supporting_skipped_gate_fail — rubric has gate failures ['competent_framing_regex']; not a stable anchor for supporting materials
  - `cluster_15_lt_01`: supporting_skipped_gate_fail — rubric has gate failures ['single_construct']; not a stable anchor for supporting materials
  - `cluster_17_lt_02`: supporting_skipped_gate_fail — rubric has gate failures ['single_construct']; not a stable anchor for supporting materials
  - `cluster_19_lt_02`: supporting_skipped_gate_fail — rubric has gate failures ['observable_verb']; not a stable anchor for supporting materials
  - `cluster_22_lt_02`: supporting_skipped_gate_fail — rubric has gate failures ['single_construct']; not a stable anchor for supporting materials
  - `cluster_30_lt_02`: supporting_skipped_gate_fail — rubric has gate failures ['observable_verb']; not a stable anchor for supporting materials
  - `cluster_08_lt_02`: supporting_skipped_gen_fail — rubric generation failed for cluster_08_lt_02; no content to build from
  - `cluster_10_lt_01`: supporting_skipped_gen_fail — rubric generation failed for cluster_10_lt_01; no content to build from
  - `cluster_14_lt_02`: supporting_skipped_gen_fail — rubric generation failed for cluster_14_lt_02; no content to build from
  - `cluster_21_lt_01`: supporting_skipped_gen_fail — rubric generation failed for cluster_21_lt_01; no content to build from
  - `cluster_23_lt_01`: supporting_skipped_gen_fail — rubric generation failed for cluster_23_lt_01; no content to build from


## Flags
Total flags: **89**


### `blk_0176` — `classification_unreliable` — **MEDIUM**

**Stage:** KUD classification

**Technical:** The KUD classifier ran 3 times on this source block; fewer than 2/3 runs agreed on the knowledge type (Type 1 / 2 / 3). The block was halted rather than forced into an uncertain classification.

**Pedagogical:** If the classifier can't agree on whether this is declarative knowledge, a skill, or a disposition, the LT derived from it may not accurately reflect the source intent. A teacher should check the original source block and decide the classification manually before using this LT.

### `competency_clusters` — `cluster_unstable (cluster_count_differs: counts across runs = [30, 29, 38]; cluster_missing_in_run2: canonical clusters [4, 6] have no Jaccard>=0.30 match; dominant_type_drift_run2: canonical cluster 10 (Type 2) → run2 cluster 8 (Type 1); cluster_missing_in_run3: canonical clusters [4] have no Jaccard>=0.30 match; dominant_type_drift_run3: canonical cluster 3 (Type 1) → run3 cluster 3 (Type 2); dominant_type_drift_run3: canonical cluster 10 (Type 2) → run3 cluster 11 (Type 1))` — **MEDIUM**

**Stage:** competency clustering

**Technical:** The cluster_unstable flag means the clustering model's output varied across runs — cluster count or member assignment differed across 3 self-consistency runs. The canonical cluster set was retained using the majority-vote result, but alternative groupings exist.

**Pedagogical:** Cluster instability means the competency groupings may not be the only reasonable arrangement. A teacher reviewing these LTs should check whether each LT genuinely represents one distinct capability, or whether some LTs could reasonably be grouped differently.

### `cluster_04` — `cluster_unstable` — **MEDIUM**

**Stage:** competency clustering

**Technical:** The cluster_unstable flag means the clustering model's output varied across runs — cluster count or member assignment differed across 3 self-consistency runs. The canonical cluster set was retained using the majority-vote result, but alternative groupings exist.

**Pedagogical:** Cluster instability means the competency groupings may not be the only reasonable arrangement. A teacher reviewing these LTs should check whether each LT genuinely represents one distinct capability, or whether some LTs could reasonably be grouped differently.

### `cluster_05` — `cluster_unstable` — **MEDIUM**

**Stage:** competency clustering

**Technical:** The cluster_unstable flag means the clustering model's output varied across runs — cluster count or member assignment differed across 3 self-consistency runs. The canonical cluster set was retained using the majority-vote result, but alternative groupings exist.

**Pedagogical:** Cluster instability means the competency groupings may not be the only reasonable arrangement. A teacher reviewing these LTs should check whether each LT genuinely represents one distinct capability, or whether some LTs could reasonably be grouped differently.

### `cluster_07` — `cluster_unstable` — **MEDIUM**

**Stage:** competency clustering

**Technical:** The cluster_unstable flag means the clustering model's output varied across runs — cluster count or member assignment differed across 3 self-consistency runs. The canonical cluster set was retained using the majority-vote result, but alternative groupings exist.

**Pedagogical:** Cluster instability means the competency groupings may not be the only reasonable arrangement. A teacher reviewing these LTs should check whether each LT genuinely represents one distinct capability, or whether some LTs could reasonably be grouped differently.

### `cluster_11` — `cluster_unstable` — **MEDIUM**

**Stage:** competency clustering

**Technical:** The cluster_unstable flag means the clustering model's output varied across runs — cluster count or member assignment differed across 3 self-consistency runs. The canonical cluster set was retained using the majority-vote result, but alternative groupings exist.

**Pedagogical:** Cluster instability means the competency groupings may not be the only reasonable arrangement. A teacher reviewing these LTs should check whether each LT genuinely represents one distinct capability, or whether some LTs could reasonably be grouped differently.

### `cluster_06_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_06_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_06_lt_03` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_10_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_10_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_14_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_14_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_14_lt_03` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_16_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_16_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_19_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_19_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_25_lt_01` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_25_lt_02` — `lt_set_unstable` — **MEDIUM**

**Stage:** LT generation

**Technical:** The LT generator reached 2/3 agreement on a majority signature, but not 3/3 stability. The LT set was retained using the majority result.

**Pedagogical:** The learning targets in this set are the most consistent description produced, but alternative valid descriptions exist. A teacher reviewing these LTs should be aware that the boundaries between LTs may have shifted in different runs.

### `cluster_05_lt_01` — `band_statements_unreliable — 1 format/quality failures` — **MEDIUM**

**Stage:** band statements

**Technical:** The band statement generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature. No band statements were produced for this LT.

**Pedagogical:** Without band statements, teachers cannot use this LT to assess learners across the source's progression bands. The content may need manual authoring of band-level descriptors.

### `cluster_10_lt_01` — `band_statements_unstable` — **MEDIUM**

**Stage:** band statements

**Technical:** Band statement generation reached 2/3 agreement but not 3/3 stability. The majority-vote statements were retained.

**Pedagogical:** The band-level statements may be rephrased differently in alternative valid runs. The substance is stable but specific wording should be reviewed by a teacher before use.

### `cluster_12_lt_02` — `band_statements_unstable` — **MEDIUM**

**Stage:** band statements

**Technical:** Band statement generation reached 2/3 agreement but not 3/3 stability. The majority-vote statements were retained.

**Pedagogical:** The band-level statements may be rephrased differently in alternative valid runs. The substance is stable but specific wording should be reviewed by a teacher before use.

### `cluster_22_lt_01` — `band_statements_unstable` — **MEDIUM**

**Stage:** band statements

**Technical:** Band statement generation reached 2/3 agreement but not 3/3 stability. The majority-vote statements were retained.

**Pedagogical:** The band-level statements may be rephrased differently in alternative valid runs. The substance is stable but specific wording should be reviewed by a teacher before use.

### `cluster_24_lt_01` — `band_statements_unstable` — **MEDIUM**

**Stage:** band statements

**Technical:** Band statement generation reached 2/3 agreement but not 3/3 stability. The majority-vote statements were retained.

**Pedagogical:** The band-level statements may be rephrased differently in alternative valid runs. The substance is stable but specific wording should be reviewed by a teacher before use.

### `cluster_03_lt_01` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_03_lt_02` — `single_construct` — **HIGH**

**Stage:** criterion rubrics

**Technical:** The single_construct gate checks that adjacent applied levels (Emerging, Developing, Competent, Extending) share at least one topic-lemma. No topic-lemma overlap between adjacent levels is a signal that the rubric may be describing two different things across the progression.

**Pedagogical:** A rubric where adjacent levels use entirely different vocabulary may be assessing different capabilities at different levels, rather than the same capability at different depths. A teacher reviewing this rubric should check whether the construct is genuinely the same across all levels.

### `cluster_04_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_05_lt_01` — `observable_verb` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The observable_verb gate checks that each applied level descriptor contains at least one verb from the observable-action-verb list (identify, describe, compare, explain, analyse, evaluate, apply, etc.). No observable verb means the level cannot be reliably assessed.

**Pedagogical:** A rubric level with no observable action verb describes a state of being rather than a demonstrable performance. Teachers need observable verbs to assess whether a learner has met each level — without them, the assessment criteria become subjective.

### `cluster_06_lt_01` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_06_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_07_lt_02` — `observable_verb` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The observable_verb gate checks that each applied level descriptor contains at least one verb from the observable-action-verb list (identify, describe, compare, explain, analyse, evaluate, apply, etc.). No observable verb means the level cannot be reliably assessed.

**Pedagogical:** A rubric level with no observable action verb describes a state of being rather than a demonstrable performance. Teachers need observable verbs to assess whether a learner has met each level — without them, the assessment criteria become subjective.

### `cluster_09_lt_01` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_09_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_10_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_11_lt_01` — `single_construct` — **HIGH**

**Stage:** criterion rubrics

**Technical:** The single_construct gate checks that adjacent applied levels (Emerging, Developing, Competent, Extending) share at least one topic-lemma. No topic-lemma overlap between adjacent levels is a signal that the rubric may be describing two different things across the progression.

**Pedagogical:** A rubric where adjacent levels use entirely different vocabulary may be assessing different capabilities at different levels, rather than the same capability at different depths. A teacher reviewing this rubric should check whether the construct is genuinely the same across all levels.

### `cluster_11_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_12_lt_01` — `competent_framing_regex` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The competent_framing_regex gate checks the Competent descriptor for deficit hedge-phrases (e.g. 'with limited', 'not yet', 'struggles to', 'approaching', 'but fails'). One or more such phrases were found.

**Pedagogical:** Deficit language in the Competent descriptor sends learners the wrong message: that 'meeting expectations' means being almost-but-not-quite adequate. Competent should describe what learners CAN do, not what they cannot.

### `cluster_13_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_14_lt_01` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_15_lt_01` — `single_construct` — **HIGH**

**Stage:** criterion rubrics

**Technical:** The single_construct gate checks that adjacent applied levels (Emerging, Developing, Competent, Extending) share at least one topic-lemma. No topic-lemma overlap between adjacent levels is a signal that the rubric may be describing two different things across the progression.

**Pedagogical:** A rubric where adjacent levels use entirely different vocabulary may be assessing different capabilities at different levels, rather than the same capability at different depths. A teacher reviewing this rubric should check whether the construct is genuinely the same across all levels.

### `cluster_15_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_17_lt_02` — `single_construct` — **HIGH**

**Stage:** criterion rubrics

**Technical:** The single_construct gate checks that adjacent applied levels (Emerging, Developing, Competent, Extending) share at least one topic-lemma. No topic-lemma overlap between adjacent levels is a signal that the rubric may be describing two different things across the progression.

**Pedagogical:** A rubric where adjacent levels use entirely different vocabulary may be assessing different capabilities at different levels, rather than the same capability at different depths. A teacher reviewing this rubric should check whether the construct is genuinely the same across all levels.

### `cluster_18_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_19_lt_02` — `observable_verb` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The observable_verb gate checks that each applied level descriptor contains at least one verb from the observable-action-verb list (identify, describe, compare, explain, analyse, evaluate, apply, etc.). No observable verb means the level cannot be reliably assessed.

**Pedagogical:** A rubric level with no observable action verb describes a state of being rather than a demonstrable performance. Teachers need observable verbs to assess whether a learner has met each level — without them, the assessment criteria become subjective.

### `cluster_20_lt_01` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_20_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_21_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_22_lt_02` — `single_construct` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The single_construct gate checks that adjacent applied levels (Emerging, Developing, Competent, Extending) share at least one topic-lemma. No topic-lemma overlap between adjacent levels is a signal that the rubric may be describing two different things across the progression.

**Pedagogical:** A rubric where adjacent levels use entirely different vocabulary may be assessing different capabilities at different levels, rather than the same capability at different depths. A teacher reviewing this rubric should check whether the construct is genuinely the same across all levels.

### `cluster_23_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_23_lt_03` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_24_lt_01` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_24_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_25_lt_02` — `gate_unknown` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_30_lt_02` — `observable_verb` — **HIGH**

**Stage:** criterion rubrics

**Technical:** The observable_verb gate checks that each applied level descriptor contains at least one verb from the observable-action-verb list (identify, describe, compare, explain, analyse, evaluate, apply, etc.). No observable verb means the level cannot be reliably assessed.

**Pedagogical:** A rubric level with no observable action verb describes a state of being rather than a demonstrable performance. Teachers need observable verbs to assess whether a learner has met each level — without them, the assessment criteria become subjective.

### `cluster_08_lt_02` — `rubric_generation_failed` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_10_lt_01` — `rubric_generation_failed` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_14_lt_02` — `rubric_generation_failed` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_21_lt_01` — `rubric_generation_failed` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_23_lt_01` — `rubric_generation_failed` — **MEDIUM**

**Stage:** criterion rubrics

**Technical:** The rubric generator ran 3 times; fewer than 2/3 runs produced parseable output with a consistent level-signature. No rubric was produced for this LT. This entry is a placeholder flag — no descriptor text is available.

**Pedagogical:** Without a rubric, this LT cannot be used for criterion-referenced assessment. The LT exists in the output and represents a real competency from the source; a teacher can author a rubric manually using the LT name and definition as the starting point.

### `cluster_02_lt_01` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_02_lt_02` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_05_lt_02` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_06_lt_02` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_07_lt_01` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_08_lt_01` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_18_lt_02` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_20_lt_02` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_23_lt_03` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_26_lt_01` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_27_lt_02` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_28_lt_01` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_28_lt_03` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_30_lt_01` — `supporting_unreliable` — **MEDIUM**

**Stage:** supporting components

**Technical:** The supporting components generator (co-construction plan, student rubric, feedback guide) ran 3 times; fewer than 2/3 runs produced parseable output with a consistent signature.

**Pedagogical:** The supporting materials help teachers introduce the rubric to students and give actionable feedback. Without stable supporting components, teachers will need to author these materials manually.

### `cluster_03_lt_02` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_05_lt_01` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_07_lt_02` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_11_lt_01` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_12_lt_01` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_15_lt_01` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_17_lt_02` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_19_lt_02` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_22_lt_02` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_30_lt_02` — `supporting_skipped_gate_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric failed one or more semantic quality gates. A rubric with gate failures is not a stable anchor for co-construction materials.

**Pedagogical:** The rubric for this LT has known quality issues (listed under the rubric's gate failures). Generating student-facing materials from a flawed rubric risks amplifying those issues. Resolve the rubric quality flags before generating supporting components.

### `cluster_08_lt_02` — `supporting_skipped_gen_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric generator itself failed (rubric_generation_failed). There is no rubric content to base co-construction materials on.

**Pedagogical:** No rubric was produced for this LT, so supporting materials cannot be generated. A teacher would need to author a rubric manually first.

### `cluster_10_lt_01` — `supporting_skipped_gen_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric generator itself failed (rubric_generation_failed). There is no rubric content to base co-construction materials on.

**Pedagogical:** No rubric was produced for this LT, so supporting materials cannot be generated. A teacher would need to author a rubric manually first.

### `cluster_14_lt_02` — `supporting_skipped_gen_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric generator itself failed (rubric_generation_failed). There is no rubric content to base co-construction materials on.

**Pedagogical:** No rubric was produced for this LT, so supporting materials cannot be generated. A teacher would need to author a rubric manually first.

### `cluster_21_lt_01` — `supporting_skipped_gen_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric generator itself failed (rubric_generation_failed). There is no rubric content to base co-construction materials on.

**Pedagogical:** No rubric was produced for this LT, so supporting materials cannot be generated. A teacher would need to author a rubric manually first.

### `cluster_23_lt_01` — `supporting_skipped_gen_fail` — **MEDIUM**

**Stage:** supporting components

**Technical:** Supporting components were not generated for this LT because the rubric generator itself failed (rubric_generation_failed). There is no rubric content to base co-construction materials on.

**Pedagogical:** No rubric was produced for this LT, so supporting materials cannot be generated. A teacher would need to author a rubric manually first.

