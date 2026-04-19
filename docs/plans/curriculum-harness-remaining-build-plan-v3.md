# Curriculum Harness — remaining build plan, v3

**Date:** 2026-04-19. Supersedes v2 (archived at `docs/plans/archive/curriculum-harness-remaining-build-plan-v2.md`).
**Project repo:** `~/Github/curriculum-harness`.

## Purpose and scope

Forward-looking. This plan tells future sessions *what to build and why*. It does not track live state (see `STATE.md` at repo root) and does not narrate history (see `docs/project-log/harness-log.md`). Sessions should read `STATE.md` first, then consult this plan for the session they are picking up.

## Rationale for v3 (what changed vs v2)

- v2's "first action" list (commit v2, revise the 4b arc plan to drop felvételi) is retired. Live session pick-up lives in `STATE.md`, not in the build plan.
- v2's framing of "Phases 1-5 unchanged since project start" is corrected: Sessions 3a-3d landed substantive Phase 1/3/4 work (see Architectural decisions below). The 4b arc is the window in which Phases 1-5 were not touched, not the project lifetime.
- v2's blanket "flag-and-continue validation" claim is decomposed per-phase: Phase 4 has a hard-fail regeneration loop with human-review routing since Session 3c; Phase 3 still flag-and-continues for `classification_unreliable` items. This shapes which rebuild sub-tasks are open.
- v2's "VALIDITY.md scaffolded but not populated" rebuild item is removed. `VALIDITY.md` is populated and `scripts/validity-gate/` carries seven validators plus a `run_all` driver.
- Session ordering is unchanged but the post-4b arc is split into one priority-naming session (4b-7) plus explicit sub-rebuilds for the already-known bugs (exam-block scope, Phase 5 strand routing, English-only cue list). These can run in parallel with or before the diagnostic-driven rebuild work; they do not wait on 4b-7.
- The "criterion bank as fourth artefact" — currently produced by the reference-authoring pipeline but not yet by the harness — is promoted to its own post-rebuild session.

## Excellence criteria

The finished harness is defined by four verifiable criteria.

1. **Four artefacts produced on every source in the reference corpus.** KUD, learning targets with band statements or observation indicators, supporting components, and a criterion bank with prerequisite structure. Each artefact carries source-traceability metadata. Verifiable by running the harness on Welsh CfW, Common Core 7.RP, Ontario G7 History, DfE KS3 Maths, and AP US Gov Unit 1, and checking that every artefact file is produced.
2. **Harness output stays within grain ratios of the reference output.** Per vision v4.1 and the gate revisions at `docs/plans/session-4b-gate-revisions-v1.md`: KUD 0.8–1.5 per source bullet hierarchical/horizontal, 0.8–2.2 dispositional; LTs 1:1 ±20% with KUD. Verifiable by the 4b-6 comparison pipeline.
3. **No silent injection.** Every harness item has source traceability; items without traceable source are either regenerated, halted to human review, or flagged. Verifiable by `scripts/validity-gate/validate_source_faithfulness.py` and the 4b-6 injection-detection dimension.
4. **Multilingual sources do not break Phase 1.** Hungarian and Welsh-language sources produce scope-filtered output (not empty or crash). Verifiable by running Phase 1 on `palya_felveteli_2026_04_17_v1_0.json` and `wales-cfw-health-wellbeing-sow` and observing non-empty `curriculum_profile` output.

Excellent is not "no errors." Honest halts and flagged instability are features. Excellent is "high-quality output on most sources, flags low-quality output honestly, hands downstream consumers a useful input."

## Architectural decisions (load-bearing, do not re-litigate)

- **Three artefacts serve three audiences (17 April panel consensus).** KUD serves curriculum designers; LTs with bands serve teachers; criterion banks serve downstream AI tutors. Each artefact is authoritative for its audience. The harness must produce all three (plus supporting components) on every source; downstream consumers pick the one they need.
- **Contested domains use curated libraries, not live extraction (15 April decision).** Where a source exists inside a domain with genuinely contested authority (e.g. literature canon, history interpretation), the harness treats the source as one voice among several and pulls comparators from a curated library rather than extracting disputed framings live. This decision applies to horizontal/dispositional domains; hierarchical domains (maths, physics) are unaffected.
- **Source-native progression preserved in harness output.** Welsh CfW uses Progression Steps 1-5; Common Core uses Grade 7; Ontario uses Grade 7; Scottish CfE uses Levels. The harness does not translate between band frameworks. Any-framework translation is a separate Claude skill.
- **Type 3 LTs never get rubrics.** Absolute rule from the LT skill. Type 3 uses observation indicators instead.
- **LT-level generic rubrics, not task-specific.** The harness produces criterion banks per LT; task-specific rubric assembly is downstream.
- **Reference-authoring pipeline is neutral.** It does not consult harness output. References represent what the harness *should* produce; the 4b-6 comparison pipeline measures the gap.
- **Model selection.** Sonnet by default for well-specified execution. Opus when architectural judgement inside the session is load-bearing, or when any single classification / clustering stage exceeds ~100 items. Opus for planning conversations regardless of session model.
- **Sessions 3a-3d context.** Phase 3 gained a profile-conditional branch (`2e7c5da`); Phase 1 scope stabilised (`43f4f4a`); Phase 4 gained a bounded hard-fail regeneration loop with human-review routing (`cfc73c5`); bullet-type tagging was added (`80bab1b`). These are not open work.

## Remaining sessions, in order

### Session 4b-5 — Ontario re-cluster follow-up

**Purpose.** Complete the third anchor reference by re-clustering the Ontario Grade 7 History KUD and running the Type 1/2 criterion generator plus supporting-components generator on stabilised clusters.

**Produces.** `docs/reference-corpus/ontario-g7-history/criteria.json`, `criteria_quality_report.json/.md`, `supporting_components.json`, updated `competency_clusters.json` with lower membership drift, updated `quality_report.md` noting stability figures, updated `_cross-source-summary.md`, a fifth Ontario CSV (criteria) and a sixth (supporting-components) bringing Ontario in line with Welsh CfW and Common Core.

**Definition of done.** Ontario `competency_clusters.json` shows membership drift below 20% across runs (current baseline: 43%); `criteria.json` present with roughly 15–20 Type 1/2 rubrics; `criteria_quality_report.json` summary present; supporting components generated; cross-source summary regenerated; five CSVs in the Ontario directory. Verifiable by file presence and counts.

**Model.** Opus. The 188-item source exposed Sonnet's clustering stability limits in Session 4b-3.

**Dependencies.** None beyond current HEAD.

### Session 4b-5b — Comparator source references

**Purpose.** Produce reference corpora for the two second-instance sources (DfE KS3 Maths, second hierarchical; AP US Gov Unit 1, second horizontal). Load-bearing for the within-domain generalisation claim — until the pipeline behaves on two sources per domain type we don't know whether the first source's shape was anchor or pattern.

**Produces.** Two new directories under `docs/reference-corpus/` (`dfe-ks3-maths/` and `ap-usgov-ced-unit1/`), each with full KUD / clusters / LTs / band statements / observation indicators if applicable / criteria / supporting components / quality reports / reference review / CSV exports. Cross-source summary extended to five sources.

**Definition of done.** Both directories match the shape of `common-core-g7-rp/` (same file set); `_cross-source-summary.md` header reads five sources; quality reports for each source include within-domain comparison notes against the first source in that domain type.

**Model.** Sonnet by default. Opus if either source exceeds 100 items at any classification stage.

**Dependencies.** Ontario follow-up complete (3/3 anchors shipped before second-instance sources begin).

### Session 4b-6 — Comparison pipeline

**Purpose.** Build the comparison pipeline that takes a harness output and a matching reference output and produces a per-source diagnostic report across four dimensions: structural metrics, semantic comparison (LLM-as-judge), injection detection, negative reference matching.

**Produces.** `curriculum_harness/comparison/` module with a documented entry point; a report renderer producing Markdown + JSON diagnostic reports; one end-to-end run against a single source (suggest Common Core — smallest reference with full artefact set) committed as the smoke-test artefact.

**Definition of done.** Running the pipeline on one reference+harness pair produces a report containing all four dimensions; report file lives in a repo location matching the `docs/reference-corpus/<source>/` convention; pipeline has calibration fixtures for the LLM-as-judge dimension (known-match and known-differ pairs) and fails pre-run if calibration does not clear a documented threshold.

**Model.** Opus. Architectural judgement load-bearing — the LLM-as-judge calibration harness and injection-detection heuristic are decisions that cascade into diagnostic quality.

**Dependencies.** At least one complete reference (Welsh CfW or Common Core) already exists; Ontario follow-up preferred but not blocking.

### Session 4b-7 — Diagnostic reports and Phase 1 rebuild priorities

**Purpose.** Run the comparison pipeline against the harness's current output for every source in the reference corpus. Read the diagnostic reports. Name Phase 1 rebuild priorities in order with rationale tied to specific diagnostic findings. This closes the 4b arc.

**Produces.** Five comparison reports (Welsh CfW, Common Core 7.RP, Ontario G7 History, DfE KS3, AP US Gov). A Phase 1 rebuild priority list at `docs/plans/phase1-rebuild-priorities-v1.md` with rationale per priority and rough session count estimate.

**Definition of done.** Five diagnostic reports committed; priorities doc committed; `STATE.md` updated to reflect that 4b is closed and to identify the first rebuild session.

**Model.** Opus for the priority synthesis; Sonnet for running the comparison pipeline on each source (deterministic given the pipeline is already built).

**Dependencies.** 4b-6 (comparison pipeline); 4b-5 and 4b-5b (reference corpora complete for all five sources).

### Session 4c-1a — Phase 1 multilingual cue support

**Purpose.** Extend `curriculum_harness/phases/phase1_ingestion.py:202-245` beyond the English-only `cues` dictionary so Hungarian and Welsh-language sources are scope-filtered rather than dropped.

**Produces.** Extended cue dictionary with Hungarian and Welsh needles; updated `_window_history_grade7` and any other anchor functions with non-English equivalents; a Phase 1 regression test running the felvételi and Welsh CfW Health & Wellbeing sources end-to-end and asserting non-empty `curriculum_profile` output.

**Definition of done.** Running Phase 1 on `configs/palya_felveteli_2026_04_17_v1_0.json` produces non-empty curriculum profile; same for a Welsh-language source; new test in `tests/` passes; `validate_source_coverage.py` run against both sources passes.

**Model.** Sonnet. Well-specified execution; no architectural judgement.

**Dependencies.** 4b-7 priorities may reorder this against other rebuild tasks; pick up when 4b-7 calls it.

### Session 4c-1b — Phase 4 GCSE_AQA_EXAM_BLOCK scoping fix

**Purpose.** Fix the known bug at `curriculum_harness/phases/phase4_lt_generation.py:132-138` and the unconditional attachment at line 871 so `GCSE_AQA_EXAM_BLOCK` is applied only when the source is an AQA GCSE exam specification, not any `document_family == "exam_specification"`. Tracked by `scripts/validity-gate/validate_exam_block_scope.py`.

**Produces.** Conditional attachment logic in Phase 4; updated docstring; `validate_exam_block_scope.py` passes against both an AQA source and a non-AQA exam-specification source.

**Definition of done.** The validator passes against a non-AQA exam-spec fixture; Phase 4 regression on AQA source unchanged.

**Model.** Sonnet.

**Dependencies.** None; can be done in parallel with 4c-1a.

### Session 4c-1c — Phase 5 strand routing fix

**Purpose.** Replace the token-overlap heuristic at `curriculum_harness/phases/phase5_formatting.py:70-149` with a strand-routing approach that does not collapse to zero when LT vocabulary does not share tokens with source strand labels.

**Produces.** Revised `_competency_relevance_score` or replacement; per-source strand-routing regression tests; documentation of the new heuristic in the Phase 5 docstring.

**Definition of done.** Phase 5 routes LTs to the correct strand on at least three sources where the current heuristic mis-routes (candidate: Welsh CfW, Ontario G7 History, AP US Gov — flagged where current output exposes the bug).

**Model.** Sonnet for the implementation; Opus for the routing strategy design conversation before implementation.

**Dependencies.** 4b-7 priorities may identify additional strand-routing failure modes; pick up when 4b-7 calls it.

### Session 4c-2 — Phase 3 hard-fail on classification_unreliable

**Purpose.** Tighten Phase 3 KUD generation so items tagged `classification_unreliable` trigger a bounded regeneration loop (mirroring Phase 4's pattern from Session 3c) rather than being emitted and flagged.

**Produces.** Regeneration loop around the Phase 3 self-consistency resolution; items that exhaust the retry budget routed to `state["human_review_required"]`; updated VALIDITY gate to assert no `classification_unreliable` items ship.

**Definition of done.** Running Phase 3 on a source that produces classification_unreliable items under the current code now produces either regenerated-stable items or human-review entries, never shipped-unstable items. VALIDITY gate asserts this.

**Model.** Sonnet.

**Dependencies.** 4b-7 priorities should confirm this is still the right shape after diagnostic review.

### Session 4c-3 — Criterion bank phase added to harness

**Purpose.** Add a criterion-generation phase to the harness so it produces the fourth artefact (criterion bank with prerequisite structure). The reference-authoring pipeline's `criterion_generator` is the target shape.

**Produces.** New harness phase (numbering TBD — likely Phase 4b or Phase 6); prerequisite DAG computation; `validate_lt_criterion_coverage.py` and `validate_prerequisite_dag.py` wired against the new phase; end-to-end harness output on Welsh CfW / Common Core / Ontario / DfE KS3 / AP US Gov includes criterion banks.

**Definition of done.** Harness on any reference-corpus source emits a criterion bank file with prerequisite structure; gate validators pass; VALIDITY.md updated.

**Model.** Opus. Architectural judgement load-bearing (where the phase slots in, what the prerequisite DAG API looks like, what the gate shape is).

**Dependencies.** 4c-1a/b/c and 4c-2 complete so the upstream phases are producing clean input.

## Housekeeping

- `docs/plans/session-4b-arc-plan-v3.md` still references Hungarian felvételi at line 22 as the exam-spec companion. The 2026-04-19 scope change drops felvételi from the 4b arc (it becomes a post-rebuild validation target, not a reference-authoring target). A small docs-only commit to remove that line from the arc plan is not scheduled as a session but should be picked up opportunistically.

## References

- Live state and next session: `STATE.md` (repo root).
- Historical log: `docs/project-log/harness-log.md`.
- Read-only audit template: `docs/audits/state-audit-2026-04-19-v1.md`.
- Gate revision history: `docs/plans/session-4b-gate-revisions-v1.md`.
- Panel personas and operating discipline: `docs/plans/archive/curriculum-harness-remaining-build-plan-v2.md` (sections "Personas used in panel reviews" and "Operating discipline"). These are stable; v3 does not recapitulate them.
- Failure patterns: Second Brain (note field `failure-pattern`).
- State discipline: `docs/process/state-md-discipline.md`.

---

*v3 generated 2026-04-19. Next update expected after 4b-7 closes, when post-rebuild priorities can be re-grounded in diagnostic findings.*
