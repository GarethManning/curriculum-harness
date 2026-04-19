# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v3.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session 4b-4** — 2026-04-19 — head `58670ea [docs] Session 4b-4 log and state snapshot`.

Closed out Session 4b-4 by regenerating Common Core 7.RP + Welsh CfW criterion artefacts after syncing the gate `OBSERVABLE_VERBS` list with the generator's `_VERB_BUCKETS`, wiring the criterion + supporting-components components into the reference-authoring pipeline, and shipping CSV exporter + review renderer + cross-source summary updates for criterion artefacts (plus a standalone `run_criteria.py` runner). Two anchor references are fully shipped; Ontario is partial (clustering unstable, criterion bank not yet generated).

## 2. Verified working

- **Phase 0 acquisition layer — complete.** Five source-type primitives at `curriculum_harness/phases/phase0_acquisition/sequences.py`; manifest schema 0.6.0 at `manifest.py:280`; nine ingestion artefacts under `docs/run-snapshots/` covering all three domain types. Verified in audit section 1.
- **Welsh CfW Health & Wellbeing reference — complete.** `docs/reference-corpus/welsh-cfw-health-wellbeing/` carries KUD (33), clusters (9), LTs (20), band statements (11 sets), observation indicators (5 sets), criteria (12 rubrics, 11 gate pass), supporting components (9), progression structure, quality reports, reference review, **five CSVs** (criteria, kud, learning-targets, observation-indicators, supporting-components), and the preserved `_generated-in-error-a-d-version/` subdirectory.
- **Common Core 7.RP reference — complete.** `docs/reference-corpus/common-core-g7-rp/` carries KUD (22), clusters (4), LTs (8), band statements (6 sets), observation indicators (0 — no Type 3 content), criteria (7 rubrics, 6 gate pass), supporting components (4), progression structure, quality reports, reference review, **five CSVs** (the observation-indicators CSV is metadata-only, 8 lines, zero rows).
- **Reference-authoring pipeline v0.5 — shipped.** `curriculum_harness/reference_authoring/` carries inventory, KUD classifier/gates, competency clustering, LT generator, band statements, observation indicators, Type 1/2 criterion generator, criterion gates, supporting-components generator, progression detection with jurisdiction lookup, and a `pipeline/run_pipeline.py` orchestration entry point. Scripts at `scripts/reference_authoring/`.
- **Phase 4 hard-fail regeneration loop — in place since Session 3c.** `curriculum_harness/phases/phase4_lt_generation.py:1-58` defines `FAIL_SET` and `MAX_REGENERATION_RETRIES = 3`; budget-exhausted LTs route to `state["human_review_required"]`, not shipped silently.
- **VALIDITY.md populated.** Seven validator scripts plus `run_all.py` driver in `scripts/validity-gate/`: `validate_source_coverage.py`, `validate_source_faithfulness.py`, `validate_architecture_diagnosis.py`, `validate_exam_block_scope.py`, `validate_lt_surface_form.py`, `validate_regenerate_loop.py`, `validate_lt_criterion_coverage.py`, `validate_prerequisite_dag.py`.
- **Sessions 3a-3d Phase 1/3/4 work landed.** Phase 3 profile-conditional branch (`2e7c5da`), Phase 1 scope stabilisation (`43f4f4a`), Phase 4 regeneration loop (`cfc13f5`), bullet-type tagging (`80bab1b`).

## 3. Verified broken

- **English-only Phase 1 cue list.** `curriculum_harness/phases/phase1_ingestion.py:202-245` — `cues: dict[str, tuple[str, ...]]` is English-only across all five `document_family` branches; `_window_history_grade7` at line 171-188 uses English-only anchors. Hungarian / Welsh-language sources miss every needle.
- **Hardcoded GCSE_AQA_EXAM_BLOCK in Phase 4.** Defined at `curriculum_harness/phases/phase4_lt_generation.py:132-138` and attached unconditionally on any `document_family == "exam_specification"` at line 871. Tracked by `scripts/validity-gate/validate_exam_block_scope.py`.
- **Phase 5 strand routing.** `curriculum_harness/phases/phase5_formatting.py:70-86` implements `_competency_relevance_score` as a pure token-set intersection; `map_lt_to_strand_label` at line 127-149 collapses to zero when LT vocabulary does not share tokens with source strand labels, and falls back on arbitrary ordering among zero-scored candidates.
- **Phase 3 flag-and-continue for `classification_unreliable`.** Unlike Phase 4, Phase 3 still emits items tagged `classification_unreliable` without a regeneration loop. Phase 3's hard-fail equivalent is not yet built.
- **Ontario anchor reference incomplete.** `docs/reference-corpus/ontario-g7-history/` is missing `criteria.json`, `criteria_quality_report.json/.md`, `supporting_components.json`, and the criterion + supporting-components CSVs. Clustering is unstable: 43% membership drift, 11 vs 15 cluster count across runs, overall `cluster_unstable` flag set. Quality report FOCUS ON verification: 0 agree / 1 disagree / 6 unstable.

## 4. Unverified

These are claimed in prior planning / run outputs but not verifiable from code alone under a read-only audit.

- **Phase 3 consolidation collapse on felvételi (32 source bullets → 14 Do-Skills).** Observable only in a Phase 3 run output (`outputs/palya-...`), not in phase source. The per_bullet vs strand_aggregated branching introduced in Session 3b/c was designed to mitigate this pattern; whether the mitigation is fully load-bearing on a fresh felvételi run is unconfirmed.
- **Factorial-notation injection from model priors on felvételi.** Pattern is acknowledged indirectly by the `source_faithfulness.py` module and the `SOURCE_FAITHFULNESS_FAIL_FLAG` wired into Phase 4's `FAIL_SET`; the specific injection is visible only in produced output.
- **Reference-authoring gate pass rates under a fresh run.** On-disk `criteria_quality_report.json` shows 12/11 for Welsh CfW and 7/6 for Common Core; these match the last generation run but are not re-verified.

## 5. Next session

**Session 4b-5 — Ontario re-cluster follow-up** (see `docs/plans/curriculum-harness-remaining-build-plan-v3.md`). Opus. Re-runs Ontario Grade 7 History clustering to bring membership drift below 20%, then runs the Type 1/2 criterion generator and supporting-components generator on stabilised clusters. Produces `criteria.json`, `criteria_quality_report.json/.md`, `supporting_components.json`, updated `competency_clusters.json`, updated `quality_report.md`, updated `_cross-source-summary.md`, and two additional CSVs bringing Ontario to five. Done when Ontario directory matches the shape of Welsh CfW and Common Core.

Invocation:

```
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model opus
```

## 6. Open questions

None at session start. Add entries here as they arise; clear them when resolved.

---

*Populated 2026-04-19 from `docs/audits/state-audit-2026-04-19-v1.md` and `docs/plans/curriculum-harness-remaining-build-plan-v3.md`. Update at end of every session per `docs/process/state-md-discipline.md`.*
