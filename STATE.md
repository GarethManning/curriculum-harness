# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v5.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session 4c-3b** — 2026-04-19 — head `b722d73 [4c-3b] Fix strand line_end truncation by confirmed-strand boundary recompute`.

Sub-run orchestration and stitching session. Delivered: stitching schema doc (pre-work), orchestration module, stitching module, pipeline entrypoint wired to strand detection (single-strand → existing path; multi-strand → orchestration + stitching; `StrandDetectionUncertain` → exit code 3), integration test suite (6 tests), Welsh CfW H&W structural equivalence regression, DfE KS3 Maths end-to-end run, detect_strands line_end bug fix (Step 3b), partial NZ Social Sciences run (credit exhaustion after History strand).

Commits this session:
- `dc28cf3` — strand-stitching schema v1 (`docs/schemas/strand-stitching-v1.md`)
- `a3e6dfc` — orchestration (`orchestrate.py`), stitching (`stitch.py`), pipeline wiring, 6 integration tests
- `9ad483b` — Welsh CfW H&W structural equivalence confirmed
- `b722d73` — detect_strands line_end bug fix (Step 3b: recompute strand boundaries from confirmed strands)

Key results:
- DfE KS3 Maths: 6 strands (65 unified KUD, 29 LTs) — committed to `docs/reference-corpus/dfe-ks3-maths-4c3b/`
- Welsh CfW H&W regression: single_strand path unchanged, structural equivalence confirmed
- NZ Social Sciences: 4 strands detected correctly post-fix; History run produced 109 KUD / 23 LTs; strands 2–4 hit credit exhaustion mid-run
- Bug found and fixed: `line_end` was set to next *candidate* heading, not next *confirmed* strand — caused NZ strands to be sliced to 5 lines
- All sanity checks passed on partial NZ stitch (History-only)
- Test suite: 14/14 adversarial + integration pass

## 2. Verified working

- **Strand detection module — complete (4c-3a/4c-3b).** `curriculum_harness/reference_authoring/strand/detect_strands.py`. Domain-agnostic structural detector with written specification. Adversarial suite: 8/8 pass. Ground-truth precision/recall: 1.00/1.00 on both DfE KS3 Maths (6 strands) and NZ SS (4 strands). Welsh CfW H&W correctly identified as single-strand (lens-heading detection path). Step 3b bug fix: strand `line_end` now computed from confirmed-strand boundaries, not candidate-heading boundaries.
- **Multi-strand orchestration + stitching — complete (4c-3b).** `orchestrate.py`, `stitch.py`. Per-strand temp snapshots, sub-run invocation via `main(argv)`, unified artefact assembly with strand-slug ID prefixing and strand provenance field. 5 sanity checks. `--sub-run` flag converts `artefact_count_ratio` hard halt to flag (per-strand slices are dense; gate calibrated for full-curriculum docs).
- **Pipeline strand detection wiring — complete (4c-3b).** `run_pipeline.py` calls `detect_strands()` before inventory build. Single-strand → existing path; multi-strand → orchestration + stitch; `StrandDetectionUncertain` → exit code 3. `--sub-run` arg added.
- **DfE KS3 Maths reference corpus (4c-3b).** `docs/reference-corpus/dfe-ks3-maths-4c3b/`. 6 strands, 65 unified KUD items, 29 unified LTs. Strand-prefixed IDs and strand provenance fields on all items.
- **Phase 0 acquisition layer — complete.** Five source-type primitives at `curriculum_harness/phases/phase0_acquisition/sequences.py`; manifest schema 0.6.0 at `manifest.py:280`; ten ingestion artefacts under `docs/run-snapshots/` (nine prior + secondary-rshe-2025) covering all three domain types.
- **Welsh CfW Health & Wellbeing reference — complete.** `docs/reference-corpus/welsh-cfw-health-wellbeing/` — pre-4c-1 note applies (criteria.json predates halts-to-flags refactor).
- **Common Core 7.RP reference — complete.** `docs/reference-corpus/common-core-g7-rp/` — same pre-4c-1 note.
- **Ontario G7 History reference — complete (4b-5).** `docs/reference-corpus/ontario-g7-history/` — same pre-4c-1 note.
- **AP US Gov CED Unit 1 reference — complete (4c-1 re-run).** `docs/reference-corpus/ap-usgov-ced-unit1/` — 26 LTs / 26 rubrics (10 pass / 9 gate-fail / 7 gen-fail) / 50 flags / 5 CSVs.
- **Secondary RSHE 2025 reference — complete (4c-2b).** `docs/reference-corpus/secondary-rshe-2025/` — 149 KUD / 26 clusters / 66 LTs / band sets / 4 obs indicator sets / 62 rubrics (10 gate-fail, 7 gen-fail) / 44 supporting components / 5 CSVs. `england_rshe_secondary` progression type (single-band "End of Secondary", ages 11-16). Gate-calibrated: obs=0, sc=2, comp=1. 2 persistent single_construct false positives (lemmatiser-gap; flagged for teacher review).
- **Reference-authoring criterion gates — recalibrated (4c-2b).** `criterion_gates.py` OBSERVABLE_VERBS expanded to 44 verbs (19 transfer/integration verbs Commit A + 6 additional verbs Fix 1). `_topic_lemmas()` lemmatisation-aware (Commit B). `generate_criteria.py` _VERB_BUCKETS kept in sync. Adversarial suite: 16/16 pass.
- **Reference-authoring pipeline — Sonnet default (4c-2a).** `DEFAULT_MODEL = SONNET_MODEL` in all 7 per-item stages. `--model` flag propagates through to all stages. `--cluster-model` Opus escalation unchanged.
- **Token logging — complete (4c-2a).** `curriculum_harness/_anthropic.py`: `TokenLedger`, `LEDGER`, cost constants (Haiku/Sonnet/Opus).
- **`detect_progression.py` — `england_rshe_secondary` added (4c-2a).** Curated entry for DfE RSHE statutory guidance.
- **Reference-authoring pipeline v0.6 — halts-to-flags shipped (4c-1).** Unchanged from 4c-1.
- **Criterion bank schema v1.** `docs/schemas/criterion-bank-v1.md` — target schema for 4c-4.
- **VALIDITY.md populated.** Seven validator scripts plus `run_all.py` driver in `scripts/validity-gate/`. Methodological lesson added: in-memory gate validation is not a substitute for fresh-run validation.

## 3. Verified broken

- **English-only Phase 1 cue list.** `curriculum_harness/phases/phase1_ingestion.py:202-245`.
- **Hardcoded GCSE_AQA_EXAM_BLOCK in Phase 4.** `curriculum_harness/phases/phase4_lt_generation.py:132-138`.
- **Phase 5 strand routing.** `curriculum_harness/phases/phase5_formatting.py:70-86`.
- **Phase 3 flag-and-continue for `classification_unreliable`.** Phase 3 still emits items without a regeneration loop.
- **Welsh/Common Core/Ontario criteria.json predate 4c-1.** Rubric gen halts remain in `halted_lts`. Re-run not required but would update format.
- **`_lemmatise()` derivational morphology.** `-ful`/`-fully` morphology, hyphen splitting, name/identify coupling not resolved. Causes 2 persistent single_construct false positives on RSHE 2025. Scoped to 4c-2c.

## 4. Unverified

- **RSHE 2025 Type 3 rate (3.4%).** RSHE uses propositional framing ("pupils should know that...") for outcomes that are pedagogically dispositional. Whether 3.4% is a classification limitation or genuinely reflects the source's framing is unresolved. Teacher review needed to assess.
- **Phase 3 consolidation collapse on felvételi.** Observable only in a Phase 3 run output.
- **Reference-authoring gate pass rates for Welsh CfW / Common Core under a fresh re-run.** Not re-verified since 4c-1.
- **AP US Gov rubric flag rate after gate recalibration.** 4c-2b gate improvements not yet applied to an AP US Gov re-run. Expected improvement; not verified.

## 5. Next session

**4c-3b completion — NZ Social Sciences full re-run.** Session ran out of API credits after History strand. Re-run NZ Social Sciences from snapshot `docs/run-snapshots/2026-04-18-session-4a-3-nz-curriculum` once credits are topped up. Verify: 4 strands, unified corpus sanity checks all pass, within-strand prerequisite scoping assessment for horizontal domain.

Command:
```
python -m curriculum_harness.reference_authoring.pipeline.run_pipeline \
  --snapshot docs/run-snapshots/2026-04-18-session-4a-3-nz-curriculum \
  --out /tmp/nz-social-sciences-4c3b \
  --domain horizontal
```

After NZ run: copy results to `docs/reference-corpus/nz-ss-social-sciences-4c3b/`, commit, then proceed to **4c-4** (criterion bank / cross-source aggregation).

**4c-2c (deferred) — Lemmatiser improvements.** `-ful`/`-fully` morphology, hyphen splitting, name/identify coupling. Defer unless teacher review flags the 2 persistent single_construct false positives as blocking.

Invocation:
```
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model sonnet
```

## 6. Open questions

- **RSHE KUD count (149 vs expected 30-55).** The briefed expectation was 30-55 items post-filtering. Actual: 149. The higher count is defensible — RSHE numbered bullets contain multiple distinct "should know" sub-items; the classifier correctly splits them. Not a gate failure but worth noting for future sources with similarly verbose numbered lists.
- **LOW confidence tier not seen in any run.** Defined in 4c-1; hasn't fired yet. Requires multiple gate failures AND unstable rubric simultaneously.
- **Welsh/Common Core/Ontario not re-run.** Pre-4c-1 criteria.json format. Re-run needed if 4c-4 requires their output in new format.
- **Ontario LT halts on large Opus clusters.** Carry-forward from 4b-5. Pick up in 4c-7.
- **Second hierarchical source gap — resolved (4c-3b).** DfE KS3 Maths 6-strand run complete via `--sub-run` flag that converts ratio gate from hard halt to flag. Reference corpus at `docs/reference-corpus/dfe-ks3-maths-4c3b/`.
- **AP US Gov rubric flag rate after 4c-2b gate recalibration.** Not yet re-run. Pick up in 4c-3a or dedicated session.

---

*Last updated 2026-04-19 at end of Session 4c-3b. Update at end of every session per `docs/process/state-md-discipline.md`.*
