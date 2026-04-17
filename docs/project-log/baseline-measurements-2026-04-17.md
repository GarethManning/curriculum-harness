# Baseline measurements — 2026-04-17

First measurements from the three foundation-moment-1 VALIDITY gates
(assertions a/b/c) after their promotion from stubs in Session 2.
All three gates share `eval/source_evidence_matcher.py` as the
underlying primitive.

**Matcher**: pure-Python lexical (lemma Jaccard + char n-gram),
threshold `0.20`. See `eval/source_evidence_matcher.py` docstring for
the full adjacent-mechanism declaration; summary here: no synonyms,
no word-order, no negation, no domain-relevance, English-only.

**Source-proxy corpus construction** (see
`scripts/validity-gate/_run_loader.py`): Phase 1 `curriculum_profile`
text (rationale, source_hints.pages_note, assessment_signals.format)
+ Phase 2 `architecture` text (strand label + values_basis, strand.id,
structural_flaw). For pre-v1.2 runs without `strands[]`, the element
lists are used as fallback.

Commits behind these numbers:
- `02917c3` [docs] create project log file
- `a04aa0e` [judge] add source-evidence matcher and fixture tests
- `b8be9cb` [judge] implement VALIDITY gates a/b/c

---

## Felvételi — `outputs/palya-felveteli-2026-04-17/`

Config: `configs/palya_felveteli_2026_04_17_v1_0.json`
Source: Hungarian topic list (Oktatási Hivatal 8. évf.
central-written maths entrance exam).
Phase 1 profile: `exam_specification`, `single_intended_level`,
`full_document`; Phase 2 architecture: 6 strands (4 hierarchical,
1 horizontal, 1 dispositional).

| Gate | Total | Flagged | Rate |
|---|---:|---:|---|
| source_coverage | 16 source-proxy items | 13 orphaned | coverage **18.8 %** |
| source_faithfulness | 31 LTs | 28 flagged | faithfulness **9.7 %** |
| architecture_diagnosis | 6 strands | 0 unverifiable | verifiability **100 %** |

### Session-brief checkpoint

> The felvételi run's factorial LT should be flagged as potentially
> invented. If it isn't, the no-invention gate is miscalibrated and
> needs fixing before this session ends.

**Result: CONFIRMED.** LT index 0 (`"I can calculate factorials and
apply counting principles to solve mathematical problems."`) scored
**0.136** against its best source-proxy match
(`architecture.strands[4].label+values_basis` —
"Mathematical Reasoning and Problem Solving. Cross-cutting skills of
logical reasoning..."). Below threshold; flagged as potentially
invented.

### LTs that cleared threshold (3 of 31)

- LT3 (0.200): *"I can identify the correct number system for given
  numbers using membership criteria."* → matches `strands[0].label+
  values_basis` on generic `number` / `system`.
- LT12 (0.273): *"I can analyse how mathematical patterns connect
  across different content areas to construct logical reasoning"* →
  matches `strands[4].label+values_basis`.
- LT27 (0.222): *"I can construct mathematical arguments that connect
  claims to evidence through logical reasoning."* → matches
  `strands[4].label+values_basis`.

### Interpretation — high sensitivity, lower precision

The 28/31 faithfulness-flag rate is *not* evidence that 28 LTs are
truly invented. It is evidence that the English source-proxy corpus
for this run is too thin to match most LTs:

- 13 of 16 proxy items are themselves below-threshold (as coverage
  reports), meaning the proxy items also don't have strong lexical
  overlap with each other or with the LT set. The proxy is sparse.
- The raw source is Hungarian; the matcher is English-only
  (adjacent mechanism #4). The Phase 1/2 English rendering captures
  the top-level strand labels but not the source's bullet-level
  content vocabulary (e.g. the Hungarian bullet
  *"Összetett számok prímtényezős felbontása, osztó, többszörös,
  legnagyobb közös osztó, legkisebb közös többszörös"* exists in the
  raw source; its English trace only survives as
  `strands[0].label+values_basis` which is too generic to match
  LT18 *"I can find prime factorizations..."*).

**True-positive signal preserved.** The `factorial` LT is genuinely
invented (REVIEW.md §2 and Session 1 Q5.1) and this gate correctly
flags it. The gate is therefore useful as a *sensitivity* signal —
any LT flagged here deserves human review, but a flag is not proof
of invention.

**Upgrade path.** A per-run `_source_bullets_v1.json` artefact
(produced by a Phase 1.5 step that preserves a structured list of the
source's content bullets, ideally post-translation for non-English
sources) would raise precision sharply. Not on any session's roadmap
yet.

### Coverage orphans

All 13 orphans (including `curriculum_profile.rationale` and all
`strands[].label+values_basis` combos) scored below 0.20 against the
LT set. This is the mirror of the faithfulness finding: with a thin
English proxy, the generic strand labels don't lexically match the
more-specific LT statements well.

### Architecture diagnosis — all 6 strands verifiable

Each strand label matched at least one independent proxy item (the
values_basis of OTHER strands, structural_flaw, or profile.rationale)
above 0.20. Means the six strands at least cross-reference each other
at the lexical level; does not mean they are faithful to the source —
only that the strand set is internally coherent.

---

## Ontario — `outputs/ontario_grade7_history/`

Note: session brief specified `outputs/ontario_grade7_history_v1/`.
That directory contains only structured LTs; the full Phase 1–4
bundle lives at `outputs/ontario_grade7_history/` under pre-v1.2
naming (no runId prefix, no curriculum_profile, legacy architecture
shape with no `strands[]`). Baseline was run against
`ontario_grade7_history/`.

Source: English (Ontario Grade 7 social-studies / history expectations).
Phase 2 architecture: 4 hierarchical + 5 horizontal + 4 dispositional
*elements* (legacy element lists; no `strands[]`).

| Gate | Total | Flagged | Rate |
|---|---:|---:|---|
| source_coverage | 14 source-proxy items | 14 orphaned | coverage **0.0 %** |
| source_faithfulness | 22 LTs | 22 flagged | faithfulness **0.0 %** |
| architecture_diagnosis | 13 strands | 0 unverifiable | verifiability **100 %** |

### Interpretation

Ontario is a pre-v1.2 run. Its Phase 2 architecture has no `strands[]`
field and no `values_basis` strings — only the short element labels
(3–4 words each) plus a `structural_flaw` sentence. The total
source-proxy corpus is 14 short labels. Even though the raw source
is English (so the proxy-ceiling adjacent mechanism doesn't apply),
the corpus is so sparse that no LT clears threshold. Coverage 0 % and
faithfulness 0 % both track the same cause: not enough proxy text to
match against.

**Architecture diagnosis at 100 %** because the 13 labels share
vocabulary with each other (e.g. `Historical Empathy` and
`Historical Inquiry` share "historical") — internal coherence only.

### Takeaway for older runs

Pre-v1.2 runs give an unreliable baseline. Re-running the Ontario
config under the current v1.2+ harness — which emits `strands[]` with
`values_basis` — would produce a more meaningful baseline. Not
scheduled in this session.

---

## Threshold calibration

The 0.20 threshold was chosen against `eval/test_cases/` fixtures
(known-good matches land 0.43–1.0; known-bad invented-LT and orphan
cases land 0.03–0.08). The fixtures test separation on short,
content-similar bullet-vs-LT pairings. Real proxy corpora — as this
baseline shows — produce a narrower distribution centred below
threshold, because the proxy is strand-level rather than bullet-level.

**Do not move the threshold without re-running these baselines.**
Baseline-to-baseline comparability requires a stable threshold; if a
future session tightens or relaxes it, re-measure both runs and
append a dated follow-up to this file (don't overwrite).

---

## What Session 3+ can do to improve precision

In rough priority order:

1. **Harness emits `_source_bullets_v1.json`** per run. Phase 1 already
   has access to the raw source text; a small pre-chunking step that
   writes a structured bullet list (translated if non-English) would
   unlock per-bullet coverage and faithfulness matching. The most
   impactful change.
2. **Per-run threshold override.** Runs with very thin proxy corpora
   could be marked as such and evaluated at a different threshold, or
   skipped for faithfulness entirely (coverage only).
3. **Embedding similarity fallback.** When lexical Jaccard produces a
   below-threshold score, a fallback embedding check could rescue
   semantic matches that share no lemmas (synonyms/paraphrase). Adds
   PyTorch dependency; flagged on the Session 2 decision record as
   deferred.
4. **Hungarian matcher**. A second matcher that reads Hungarian and
   can score the Hungarian raw source against translated LT text (or
   the reverse). Requires a Hungarian lemmatiser and stopword list.
   Only useful if Hungarian runs become a regular baseline.
