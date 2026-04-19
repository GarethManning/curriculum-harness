# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v3.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session 4b-5b** — 2026-04-19 — head `ada26da [gen] AP US Gov CED Unit 1 reference corpus + DfE KS3 halt diagnosis (4b-5b)`.

AP US Gov CED Unit 1 produced as the second horizontal reference corpus: 67 KUD items / 13 clusters / 26 LTs / 26 band sets / 0 indicator sets / 15 rubrics (10 gate pass) / 8 supporting components / 5 CSVs. Haiku clustering (67 items < 100 Opus threshold; no escalation). Added AP US Gov and DfE KS3-only curated entries to `detect_progression.py` — AP US Gov halted at progression detection before the fix; DfE text-inspection was producing a wrong multi-KS structure. DfE KS3 Maths halted at `artefact_count_ratio` gate (71/17=4.18, outside [0.8, 2.5]; 90% classification instability) — root cause: full-programme source is scope-mismatched for single-domain reference authoring. Diagnosis artefacts preserved; second hierarchical source gap remains open. Cross-source summary extended to four completed sources.

## 2. Verified working

- **Phase 0 acquisition layer — complete.** Five source-type primitives at `curriculum_harness/phases/phase0_acquisition/sequences.py`; manifest schema 0.6.0 at `manifest.py:280`; nine ingestion artefacts under `docs/run-snapshots/` covering all three domain types. Verified in audit section 1.
- **Welsh CfW Health & Wellbeing reference — complete.** `docs/reference-corpus/welsh-cfw-health-wellbeing/` carries KUD (33), clusters (9), LTs (20), band statements (11 sets), observation indicators (5 sets), criteria (12 rubrics, 11 gate pass), supporting components (9), progression structure, quality reports, reference review, **five CSVs**.
- **Common Core 7.RP reference — complete.** `docs/reference-corpus/common-core-g7-rp/` carries KUD (22), clusters (4), LTs (8), band statements (6 sets), observation indicators (0 — no Type 3 content), criteria (7 rubrics, 6 gate pass), supporting components (4), progression structure, quality reports, reference review, **five CSVs**.
- **Ontario G7 History reference — complete (4b-5).** `docs/reference-corpus/ontario-g7-history/` carries KUD (188), clusters (8 canonical, Opus 4.6), LTs (13; 3 halted clusters), band statements (11 sets), observation indicators (2 sets), criteria (7 rubrics, 6 gate pass, 4 halted), supporting components (6, 0 halts), progression structure, quality reports, reference review, **five CSVs**. Cluster membership drift: 0% (run2) / 9.57% (run3), below the 20% DoD threshold.
- **AP US Gov CED Unit 1 reference — complete (4b-5b).** `docs/reference-corpus/ap-usgov-ced-unit1/` carries KUD (67), clusters (13, Haiku), LTs (26; 1 halted cluster), band statements (26 sets), observation indicators (0 — no Type 3 content), criteria (15 rubrics, 10 gate pass, 11 halted), supporting components (8, 2 halts), progression structure, quality reports, reference review, **five CSVs**. Second horizontal anchor. Cluster stability `cluster_unstable` driven by count differs [13,12,13] and cluster_07 missing in runs 2-3 — not membership drift.
- **Reference-authoring pipeline v0.5 — shipped.** `curriculum_harness/reference_authoring/` carries inventory, KUD classifier/gates, competency clustering, LT generator, band statements, observation indicators, Type 1/2 criterion generator, criterion gates, supporting-components generator, progression detection with jurisdiction lookup (4b-5b: +AP US Gov CED `us_ap_course_unit` and DfE KS3-only `england_nc_ks3_only` entries), and a `pipeline/run_pipeline.py` orchestration entry point. Scripts at `scripts/reference_authoring/`, including `run_cluster_only.py` probe runner.
- **Phase 4 hard-fail regeneration loop — in place since Session 3c.** `curriculum_harness/phases/phase4_lt_generation.py:1-58` defines `FAIL_SET` and `MAX_REGENERATION_RETRIES = 3`; budget-exhausted LTs route to `state["human_review_required"]`, not shipped silently.
- **VALIDITY.md populated.** Seven validator scripts plus `run_all.py` driver in `scripts/validity-gate/`: `validate_source_coverage.py`, `validate_source_faithfulness.py`, `validate_architecture_diagnosis.py`, `validate_exam_block_scope.py`, `validate_lt_surface_form.py`, `validate_regenerate_loop.py`, `validate_lt_criterion_coverage.py`, `validate_prerequisite_dag.py`.
- **Sessions 3a-3d Phase 1/3/4 work landed.** Phase 3 profile-conditional branch (`2e7c5da`), Phase 1 scope stabilisation (`43f4f4a`), Phase 4 regeneration loop (`cfc13f5`), bullet-type tagging (`80bab1b`).

## 3. Verified broken

- **English-only Phase 1 cue list.** `curriculum_harness/phases/phase1_ingestion.py:202-245` — `cues: dict[str, tuple[str, ...]]` is English-only across all five `document_family` branches; `_window_history_grade7` at line 171-188 uses English-only anchors. Hungarian / Welsh-language sources miss every needle.
- **Hardcoded GCSE_AQA_EXAM_BLOCK in Phase 4.** Defined at `curriculum_harness/phases/phase4_lt_generation.py:132-138` and attached unconditionally on any `document_family == "exam_specification"` at line 871. Tracked by `scripts/validity-gate/validate_exam_block_scope.py`.
- **Phase 5 strand routing.** `curriculum_harness/phases/phase5_formatting.py:70-86` implements `_competency_relevance_score` as a pure token-set intersection; `map_lt_to_strand_label` at line 127-149 collapses to zero when LT vocabulary does not share tokens with source strand labels, and falls back on arbitrary ordering among zero-scored candidates.
- **Phase 3 flag-and-continue for `classification_unreliable`.** Unlike Phase 4, Phase 3 still emits items tagged `classification_unreliable` without a regeneration loop. Phase 3's hard-fail equivalent is not yet built.
- **Ontario LT generation halts on large clusters (4b-5).** `lts.json` shows 3 of 8 Opus clusters halted LT generation with `lt_set_unreliable` (0/3, 1/3, 0/3 parseable runs) — all three clusters are large (23, 31, 34 items). Haiku's parse-reliability ceiling for LT generation on large clusters may warrant a per-stage model override analogous to the 4b-5 `--cluster-model` flag; tracked as a rebuild candidate.

## 4. Unverified

These are claimed in prior planning / run outputs but not verifiable from code alone under a read-only audit.

- **Phase 3 consolidation collapse on felvételi (32 source bullets → 14 Do-Skills).** Observable only in a Phase 3 run output (`outputs/palya-...`), not in phase source. The per_bullet vs strand_aggregated branching introduced in Session 3b/c was designed to mitigate this pattern; whether the mitigation is fully load-bearing on a fresh felvételi run is unconfirmed.
- **Factorial-notation injection from model priors on felvételi.** Pattern is acknowledged indirectly by the `source_faithfulness.py` module and the `SOURCE_FAITHFULNESS_FAIL_FLAG` wired into Phase 4's `FAIL_SET`; the specific injection is visible only in produced output.
- **Reference-authoring gate pass rates under a fresh run.** On-disk `criteria_quality_report.json` shows 12/11 for Welsh CfW and 7/6 for Common Core; these match the last generation run but are not re-verified.
- **v3 projections gap is clustering-model-dependent, not systematically high.** AP US Gov (Haiku clustering, 67 items) produced 26 LTs and 15 rubrics — well above Ontario's Opus-clustered 13 LTs / 7 rubrics. The projection gap seen in 4b-5 is driven by Opus clustering producing fewer, larger clusters (some halt LT gen), not by the source type. Haiku-clustered sources track v3's original projections. The unverified note from 4b-5b pre-session is now partially resolved: the pattern is "Opus clustering lowers LT count; Haiku clustering aligns with v3 projections." No revision to v3 projections is warranted for Haiku-clustered sources.

## 5. Next session

**Session 4b-6 — Comparison pipeline** (see `docs/plans/curriculum-harness-remaining-build-plan-v3.md`). Builds the comparison pipeline that takes a harness output and a matching reference output and produces a per-source diagnostic report across four dimensions: structural metrics, semantic comparison (LLM-as-judge), injection detection, negative reference matching. One end-to-end smoke run against Common Core G7 RP (smallest reference with full artefact set). Model: Opus for architectural judgement; Sonnet for pipeline execution.

**Note:** Second hierarchical source gap remains open after 4b-5b. DfE KS3 Maths as ingested failed the ratio gate (full-programme source, not single-strand). A properly scoped re-ingestion (one strand, e.g. Number) is needed before the second hierarchical source can be completed. This can be picked up in parallel with or after 4b-6.

Invocation:

```
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model sonnet
```

## 6. Open questions

- **Ontario LT halts on large Opus clusters.** Opus clustering consolidated Ontario into fewer, larger clusters (23/31/34 items on the halted three); Haiku LT generation failed parse-reliability on all three. Options: (a) add `--lt-model` to pipeline and escalate LT gen to Opus for large-cluster inputs; (b) raise LT generator `DEFAULT_MAX_TOKENS` (currently 3072); (c) split large clusters before LT gen. Pick up in 4b-7.
- **AP US Gov rubric halt rate (42%).** Higher than prior anchors (15–27%). Haiku shows more instability on political-science/constitutional technical vocabulary. Candidate for a `--rubric-model` escalation flag analogous to `--cluster-model`. Triage in 4b-7.
- **`overall_stability_flag == cluster_unstable` is normal, not a DoD failure.** All four completed sources ship `cluster_unstable` for reasons other than membership drift. The v3 DoD targets *membership drift* specifically. Worth a future gate-revision pass.
- **Second hierarchical source gap.** DfE KS3 Maths (full programme) failed ratio gate. A scoped re-ingestion (one strand only) is needed. Candidate: DfE KS3 Maths — Number strand. Can be addressed alongside or after 4b-6.

---

*Last updated 2026-04-19 at end of Session 4b-5b. Update at end of every session per `docs/process/state-md-discipline.md`.*
