# Validity

**Project:** Curriculum Harness (package `curriculum_harness`, formerly
`curriculum-decomposer` / `kaku_decomposer`) — LangGraph pipeline that
ingests a curriculum document and emits a KUD map + learning targets.
**Last reviewed:** 2026-04-18 (Session 3c — foundation-moment-2 gates
(LT surface form + regenerate loop) promoted from `pending` to
`implemented` now that Phase 4's hard-fail regeneration loop
(FAIL_SET + bounded retry + `regeneration_events_v1.json` artefact)
is in place. Earlier 2026-04-17 review (Session 2) promoted
foundation-moment-1 gates (a/b/c).
**Next quarterly review:** 2026-07-17.

> **Quarterly review ritual.** On the date above, re-read this file
> end to end. Verify each pending assertion is either (a) still pending
> with a current reason, (b) has been upgraded to an implemented gate
> script, or (c) has been retired as no longer load-bearing. Update
> the last-reviewed date. If any deferred assertion's blocking phase
> has landed, promote it to pending and open a gate-script ticket.

---

## The claim

Curriculum Harness takes a curriculum document (URL — PDF or plain
text), diagnoses its knowledge architecture (document family, level
model, scoping strategy, strands), produces a KUD (Know / Understand /
Do) map, and emits a set of learning targets whose wording is
appropriate to the document family (`i_can` by default, `outcome_statement`
for higher-ed syllabi). Downstream, each learning target will decompose
into a criterion bank with a prerequisite DAG (that phase is not yet
built).

The claim is falsifiable by any of:

- **(a)** A reader of the source document identifies a load-bearing
  content element that has no learning target in the output.
- **(b)** A learning target in the output names a concept, skill, or
  assessment move the source document does not introduce.
- **(c)** The Phase 2 architecture diagnosis (strand names, level
  model, scoping strategy) cannot be justified by pointing at specific
  passages of the source.
- **(d)** Learning targets ship that violate the surface-form contract
  (word count, format, single-construct, no embedded examples) and
  the regenerate loop did not run to fix them.
- **(e)** The `GCSE_AQA_EXAM_BLOCK` prompt fragment is attached to a
  run whose source is not an AQA document.
- **(f)** (When criterion-bank phase lands) a learning target with no
  criteria, or a criterion graph with a cycle.

## The primary-source artefact

For any run, the **source document** cited in the run config is the
primary source. Concretely: `source.url` in the config, the PDF or
HTML fetched from it, and the plain text produced by Phase 1
ingestion.

The machine-readable abstraction over the source is the Phase 1
**`curriculum_profile`** JSON (written to
`outputs/<run>/<runId>_curriculum_profile_v1.json`) plus the Phase 2
**architecture** JSON (`..._architecture_v1.json`). Every downstream
artefact — KUD, learning targets, structured LTs, run report — is
derivative and must answer to the source and these two Phase 1/2
artefacts.

### Have I spent deliberate time with the artefact?

**Partial.** The initial Palya-felvételi run (2026-04-17, config
`configs/palya_felveteli_2026_04_17_v1_0.json`) exercised the pipeline
end-to-end on a real OH topic-list page and produced a review queue
flagged by name in `outputs/palya-felveteli-2026-04-17/REVIEW.md`.
The GCSE AQA, Ontario Grade 7, UK NC, and university-syllabus runs
are smoke-test fixtures. No cross-document audit has been performed
on output faithfulness — that is exactly what foundation moment 1
below is reserved for.

**Commentary vs primary source.** The standing posture is: the source
document is the record. The Phase 2 architecture JSON is a
reading of that record. Where the architecture contradicts the
source, the source wins and the architecture must be regenerated or
patched. Where a learning target contradicts the architecture or the
source, the learning target is wrong.

## Foundation moments

Four abstractions in this project sit directly on the primary source
and each is (or will be) a construct-validity risk:

### 1. Source → output faithfulness

**The pipeline's load-bearing promise.** Learning targets are derived
from the source document. Every load-bearing content element in the
source should appear in at least one learning target; no learning
target should introduce content the source does not support; the
Phase 2 architecture diagnosis should be justifiable from the source.

**Failure mode.** A fluent LLM-generated LT set that looks plausible
but (a) silently drops a strand, or (b) inflates a strand with
material the source does not teach, or (c) imports conventions from a
different curriculum's commentary (e.g. AQA command words applied to
a non-AQA source).

**Gate scripts — status `implemented` (Session 2, 2026-04-17):**
- `scripts/validity-gate/validate_source_coverage.py` — every source
  content element in the Phase 1 `curriculum_profile` + Phase 2
  `architecture` source-proxy corpus traces to ≥1 LT in
  `..._learning_targets_v1.json` at match score ≥ 0.20.
- `scripts/validity-gate/validate_source_faithfulness.py` — no LT
  introduces content unsupported by the source-proxy corpus
  (no-invention check). LTs below threshold are flagged as potentially
  invented. Known test case: the felvételi `factorial` LT (REVIEW.md §2)
  is correctly flagged.
- `scripts/validity-gate/validate_architecture_diagnosis.py` — every
  strand label in the architecture traces to an independent source
  corpus item (excluding the strand's own `values_basis`).

All three gates share a common primitive,
`eval/source_evidence_matcher.py`, verified against known-good and
known-bad fixtures (`eval/test_cases/`, `eval/test_matcher.py`, 18/18
assertions passing).

**Known limit — proxy-ceiling.** The matcher reads Phase 1/2 English
output as the source corpus (raw source may be non-English, e.g. the
Hungarian felvételi source). This means the gate measures fidelity
against the pipeline's own rendering of the source, not against the
primary text directly. Baseline measurements in
`docs/project-log/baseline-measurements-2026-04-17.md` document the
precision/recall trade-off; the gate is currently *high-sensitivity,
lower-precision* for runs with thin English proxy content, meaning
faithful LTs can be flagged as invented when their support only
exists in non-English raw source. Upgrade path: per-run
`_source_bullets_v1.json` artefact (not yet produced by the harness).

### 2. Learning-target surface form

**Claim.** Every emitted LT satisfies the surface-form contract in
`ltConstraints` (max word count, single-construct-only, no embedded
examples, format appropriate to `resolve_lt_statement_format`).

**Failure mode.** LTs ship that exceed 25 words, that conjoin two
constructs with "and", that smuggle worked examples into the LT
itself, or that use the wrong stem for the active
`lt_statement_format`.

**Gate scripts — status `implemented` (Session 3c, 2026-04-18):**
- `scripts/validity-gate/validate_lt_surface_form.py` — for each LT
  in the output, checks word count (≤25), format stem
  (`I can ` prefix for `i_can`; first-person rejection for
  `outcome_statement` and `competency_descriptor`), single-construct
  (naive "and"-splitting — acknowledged limit in the gate's
  adjacent-mechanism declaration), and no embedded parenthetical
  examples. FAIL_SET-gated so `POSSIBLE_COMPOUND` and
  `LT_FORMAT_EXPECTATION_MISMATCH` ship as warnings, not failures.
  Cross-references the regeneration-events artefact to identify
  language-bypass cases — those still must pass surface-form (bypass
  only excuses `SOURCE_FAITHFULNESS_FAIL`).
- `scripts/validity-gate/validate_regenerate_loop.py` — reads
  `<runId>_regeneration_events_v1.json` (Session 3c artefact) and
  asserts every LT shipping with FAIL_SET flags has a matching
  regeneration event with one of three outcomes: `success@*`
  (cleaned by retry), `language_bypass_ship_flagged` (English-only
  matcher on non-English source), or `exhausted_retries` /
  `near_identical_retry_abort` (with matching entry in
  `human_review_required`). Un-matched flagged LTs are surfaced as
  gaps.

Phase 4's regeneration loop backs both gates:
`curriculum_harness/phases/phase4_lt_generation.py` defines
`FAIL_SET`, `MAX_REGENERATION_RETRIES = 3`, and the
`_generate_with_regen_loop` state machine. Retries carry prior
attempt + fail flags into the prompt; near-identical retries abort
early (`REGEN_NEAR_IDENTICAL_FLAG`); new flags introduced by a retry
are surfaced (`REGEN_INTRODUCED_NEW_FLAG`).

### 3. Profile-conditional prompt scope

**Claim.** Profile-conditional prompt fragments (e.g. the
`GCSE_AQA_EXAM_BLOCK` command-word / mark-tariff awareness block
added in v1.3 for `exam_specification` sources) are only attached to
runs whose source actually matches the profile they describe.

**Failure mode — known bug.** `GCSE_AQA_EXAM_BLOCK` is currently
gated on `document_family == "exam_specification"`, which matches
felvételi and other non-AQA exam specs equally. AQA command-word
conventions should not be imposed on felvételi-style short-task
papers. This has not yet caused a visible content failure but is a
latent miscalibration.

**Gate script — status `pending`:**
- `scripts/validity-gate/validate_exam_block_scope.py` — for each run,
  assert that `GCSE_AQA_EXAM_BLOCK` was attached iff the source
  jurisdiction / awarding body is AQA (or explicitly AQA-shaped).
  Requires a jurisdiction field on the source config or a Phase 1
  `awarding_body` inference to exist; scaffold records this
  dependency.

### 4. LT → criterion decomposition and prerequisite DAG

**Claim (forward-looking).** When the criterion-bank phase ships,
every LT decomposes to ≥1 criterion in the bank, and prerequisite
edges between criteria form a directed acyclic graph.

**Failure mode.** An LT with no criteria is unassessable. A cycle in
the prerequisite graph makes learning-path generation ill-defined and
will either crash the path solver or silently loop.

**Gate scripts — status `deferred`:**
- `scripts/validity-gate/validate_lt_criterion_coverage.py` — deferred
  until the criterion-bank phase exists.
- `scripts/validity-gate/validate_prerequisite_dag.py` — deferred
  until the criterion-bank phase exists. Will use a topological-sort
  or Tarjan SCC check on the prerequisite edge set.

When the criterion-bank phase is planned, promote both scripts to
`pending` in the same session and add a ground-truth JSON path
(expected: `outputs/<run>/<runId>_criteria_v1.json` or equivalent) to
this section.

## Pre-mortem

Imagining Curriculum Harness has failed catastrophically. Specific
failure modes:

### Silent content drop

A run ingests a source whose Phase 1 extraction misses a whole
section (sidebar, footnote, appendix). Phase 2/3/4 all execute
cleanly on the truncated text. The output looks complete but the KUD
and LTs silently omit a load-bearing strand. A teacher using the
output has no way to know what is missing. **Mitigation:** foundation
moment 1 coverage gate.

### Quiet fabrication

Phase 4 generates an LT whose content is plausible for the subject
but unsupported by the source (e.g. imports an AQA command-word move
into a curriculum that doesn't use it; imports a disciplinary
convention from a sibling course). **Mitigation:** foundation moment
1 faithfulness gate + foundation moment 3 profile-conditional gate.

### Surface-form regression

A prompt edit in Phase 4 loosens the single-construct constraint.
Some runs start emitting "learners can analyse and evaluate…" style
conjoined LTs. Downstream storage keeps them verbatim.
**Mitigation:** foundation moment 2 surface-form gate + the
regenerate loop (which itself has a pending-scripts gate).

### Architecture hallucination

Phase 2 diagnoses a strand model ("Knowledge / Skill / Understanding"
as three strands) that is not how the source document is actually
organised. Downstream KUD and LT generation inherit the wrong
skeleton. The output is internally coherent but structurally
mismapped from the source. **Mitigation:** foundation moment 1
architecture-verifiability gate.

### Cross-source prompt leakage

AQA-specific conventions applied to a non-AQA source (the known
`GCSE_AQA_EXAM_BLOCK` bug). Or, symmetrically, higher-ed
outcome-statement conventions applied to a K-12 source because of a
profile-resolution bug. The output reads as if it's from a different
curricular tradition. **Mitigation:** foundation moment 3 scope gate,
plus unit tests on `resolve_lt_statement_format`.

### Downstream graph corruption (deferred)

Once the criterion-bank phase lands, a prerequisite cycle or a
criterion-less LT corrupts the learning-path solver.
**Mitigation:** foundation moment 4 DAG gate.

## External expert review

The claims made by this pipeline are subject-specific. Foundation
moments warrant review by someone with domain authority over the
source document, not a generic curriculum reviewer. Specifically:

- **Architecture diagnosis (foundation moment 1, architecture
  assertion)** — for any run whose output will be used downstream,
  have a subject-matter reviewer confirm the Phase 2 strand/level
  diagnosis matches how the source is actually organised.
- **Source-faithfulness spot checks** — a reviewer with the source
  open in front of them sampling LTs and asking "is this in the
  source?" is the strongest non-automated check.
- **AQA-block scope** — an AQA-literate reviewer should sign off the
  first run where the block is (intentionally) attached.

**Review queue.** Not yet formalised. The first run to emit a review
queue is `outputs/palya-felveteli-2026-04-17/REVIEW.md` — use that
file as the template when adding per-run queues.

**Quarterly review of this file** (top banner): self-review. The
outside expert is for the foundation moments, not for this file.

## What this project is not doing

The construct-validity limitations we have chosen, and why:

### 1. No gate scripts implemented in this scaffold

This commit stands up `VALIDITY.md` and the `scripts/validity-gate/`
directory with one stub file per assertion. Each stub exits
`NOT_IMPLEMENTED` with an explanation. The gate-runner reports
counts of pending / deferred / implemented scripts but does not
block any run. Promoting a stub to a real check is a separate
per-assertion session.

### 2. No fresh-context critique step (deferred)

The harness design includes a third step where a fresh Claude session
reads the output cold and critiques it against the source. Not in
V0 scope for this project. Revisit when at least one real gate is
green.

### 3. Criterion-bank and prerequisite-DAG gates are deferred, not
   pending

Foundation moment 4 is reserved, not open. The criterion-bank phase
does not yet exist in the pipeline. Attempting to write those gates
now would force premature schema decisions.

### 4. No cross-run corpus

Palya has a `felveteli_corpus.json` that multiple gates read against.
Curriculum Harness runs are one-shot against a single source per
run config. The gates described above read per-run outputs, not a
shared corpus. If a shared corpus emerges later (e.g. a library of
decomposed curricula), this section should be revisited.

### 5. V1 automation of the harness

Per the harness design, V1 (skills + hooks) is deferred until V0
proves valuable on at least one project. Palya is the first V0
project; Curriculum Harness is the second. V1 is still out of
scope.

---

## Meta-note

This file was created at the moment Curriculum Harness had a
mature enough output shape (`curriculum_profile`,
`architecture`, `kud`, `learning_targets`, `structured_lts`,
`run_report`) to make construct-validity assertions meaningful, but
before any of those assertions had been turned into running gate
scripts. The point of committing the scaffold before the checks is
that the claim is what's load-bearing — the code will answer to it.
