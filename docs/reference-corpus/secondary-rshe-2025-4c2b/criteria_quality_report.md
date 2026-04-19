# Criterion quality report — 2a-secondary-rshe-2025

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

