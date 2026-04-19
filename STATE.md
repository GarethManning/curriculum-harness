# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v5.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session 4c-1** — 2026-04-19 — head `6247a23 [gen] AP US Gov CED Unit 1 re-run — 4c-1 halts-to-flags`.

Halts-to-flags refactor shipped across the full reference-authoring pipeline. Every pipeline halt (except `artefact_count_ratio` and `ProgressionDetectionError`) now produces flagged output and continues — no silent halts. Rubric generation halts converted to placeholder `Rubric` entries with `quality_gate_failures=["rubric_generation_failed"]`; supporting component skips recorded as flagged `halted_lts` entries. Quality report gains a `## Flags` section listing every flag with: confidence tier (HIGH/MEDIUM/LOW per 4c-1 taxonomy), technical explanation, pedagogical explanation, and (for horizontal domains) a horizontal-domain note. Criterion bank schema sketched at `docs/schemas/criterion-bank-v1.md` (target schema for 4c-4). Pre-work: `docs/plans/curriculum-harness-remaining-build-plan-v3.md` archived to `docs/plans/archive/`. AP US Gov re-run verified DoD: 26 LTs / 26 rubric entries (10 pass + 9 gate-fail + 7 gen-fail placeholders) / 0 silent halts / 50 flags with confidence tiers.

## 2. Verified working

- **Phase 0 acquisition layer — complete.** Five source-type primitives at `curriculum_harness/phases/phase0_acquisition/sequences.py`; manifest schema 0.6.0 at `manifest.py:280`; nine ingestion artefacts under `docs/run-snapshots/` covering all three domain types.
- **Welsh CfW Health & Wellbeing reference — complete.** `docs/reference-corpus/welsh-cfw-health-wellbeing/` carries KUD (33), clusters (9), LTs (20), band statements (11 sets), observation indicators (5 sets), criteria (12 rubrics, 11 gate pass), supporting components (9), progression structure, quality reports, reference review, **five CSVs**. Note: criteria.json predates 4c-1 refactor; rubric gen halts still in halted_lts (not converted to flagged entries). Re-run would extend criteria.json to include flagged placeholders.
- **Common Core 7.RP reference — complete.** `docs/reference-corpus/common-core-g7-rp/` — same pre-4c-1 note as Welsh CfW.
- **Ontario G7 History reference — complete (4b-5).** `docs/reference-corpus/ontario-g7-history/` — same pre-4c-1 note; 4 rubric gen halts in halted_lts would become flagged entries in a re-run.
- **AP US Gov CED Unit 1 reference — complete (4c-1 re-run).** `docs/reference-corpus/ap-usgov-ced-unit1/` carries KUD (67), clusters (14 this run, Haiku), LTs (26; 2 halted clusters), band statements (25 sets), observation indicators (0), criteria (26 rubric entries: 10 pass / 9 gate-fail / 7 gen-fail placeholders, 0 halted_lts), supporting components (9, 17 halted/skipped), progression structure, quality reports with ## Flags (50 flags), **five CSVs (criteria: 26 rows)**.
- **Reference-authoring pipeline v0.6 — halts-to-flags shipped (4c-1).** Key changes in `curriculum_harness/reference_authoring/pipeline/run_pipeline.py` and `gates/criterion_gates.py`: KUD gate fails (non-ratio) continue; cluster_unreliable continues; no-LTs continues with empty stubs; rubric gen halts → flagged Rubric entries; supporting skips recorded as halted_lts entries; `## Flags` section with `_GATE_EXPLANATIONS` (24 gate types), `_confidence_tier()`, `_flags_section_markdown()`.
- **Criterion bank schema v1.** `docs/schemas/criterion-bank-v1.md` — target schema for 4c-4: criterion_id, associated_lt_ids, competency_level_descriptors (five-level), prerequisite_criterion_ids (DAG), source_provenance, schema_version.
- **Phase 4 hard-fail regeneration loop — in place since Session 3c.** `curriculum_harness/phases/phase4_lt_generation.py:1-58` defines `FAIL_SET` and `MAX_REGENERATION_RETRIES = 3`.
- **VALIDITY.md populated.** Seven validator scripts plus `run_all.py` driver in `scripts/validity-gate/`.

## 3. Verified broken

- **English-only Phase 1 cue list.** `curriculum_harness/phases/phase1_ingestion.py:202-245` — English-only across all five `document_family` branches.
- **Hardcoded GCSE_AQA_EXAM_BLOCK in Phase 4.** `curriculum_harness/phases/phase4_lt_generation.py:132-138`, attached unconditionally on `document_family == "exam_specification"`.
- **Phase 5 strand routing.** `curriculum_harness/phases/phase5_formatting.py:70-86` — token-set intersection collapses to zero on LT vocabulary mismatch.
- **Phase 3 flag-and-continue for `classification_unreliable`.** Phase 3 still emits items tagged `classification_unreliable` without a regeneration loop.
- **Welsh/Common Core/Ontario criteria.json predate 4c-1.** Rubric gen halts in these sources remain in `halted_lts` (not converted to flagged placeholder entries). A re-run with `--resume-from-kud` on any of these sources would bring them up to the new format. Not a correctness issue for current state — existing rubrics and LTs are unaffected.

## 4. Unverified

- **Phase 3 consolidation collapse on felvételi (32 source bullets → 14 Do-Skills).** Observable only in a Phase 3 run output, not verifiable from code alone.
- **Factorial-notation injection from model priors on felvételi.** Acknowledged indirectly by `source_faithfulness.py`; visible only in produced output.
- **Reference-authoring gate pass rates for Welsh CfW / Common Core under a fresh re-run.** On-disk criteria_quality_report.json matches last generation run but is not re-verified in 4c-1.
- **AP US Gov cluster count variance.** Previous run: 13 clusters (1 halted). 4c-1 re-run: 14 clusters (2 halted). Both produce 26 LTs. Haiku clustering is stochastic at this corpus size — count varies run-to-run within normal range.

## 5. Next session

**Session 4c-2 — Horizontal-domain gate recalibration** (see `docs/plans/curriculum-harness-remaining-build-plan-v5.md`). The `single_construct` and `observable_verb` gates halt (now: flag) on legitimate horizontal-domain output. Recalibrate both for horizontal domains without weakening them for hierarchical. Held-out test set: Common Core 7.RP (hierarchical), Ontario G7 History (horizontal). Tune against AP US Gov and Welsh CfW. Model: Sonnet.

Invocation:
```
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model sonnet
```

## 6. Open questions

- **LOW confidence tier not seen in AP US Gov re-run.** 50 flags total: 3 HIGH, 47 MEDIUM, 0 LOW. LOW requires multiple gate failures AND unstable rubric — no rubric in this run met both conditions simultaneously. The tier is defined and will fire on future sources; no action needed.
- **Welsh/Common Core/Ontario not re-run.** The 4c-1 refactor changes output format (rubric gen halts → flagged entries). These sources still have pre-refactor criteria.json. Re-run not required for 4c-1 DoD but will be needed if 4c-2 or 4c-4 needs their output in the new format.
- **Ontario LT halts on large Opus clusters.** Carry-forward from 4b-5: 3 halted clusters (large, 23/31/34 items). Pick up in 4c-7 or as a `--lt-model` escalation flag.
- **Second hierarchical source gap.** DfE KS3 Maths (full programme) failed ratio gate. Scoped re-ingestion (one strand only, e.g. Number) needed. Pick up in 4c-3a.
- **AP US Gov rubric flag rate (62% flagged in re-run: 16/26).** Higher than prior anchors. Haiku instability on political-science vocabulary persists; gate recalibration in 4c-2 may reduce false-positive flags.

---

*Last updated 2026-04-19 at end of Session 4c-1. Update at end of every session per `docs/process/state-md-discipline.md`.*
