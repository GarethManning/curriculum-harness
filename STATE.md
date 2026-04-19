# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v5.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session 4c-3a** — 2026-04-19 — head `b714e7a [4c-3a] Adversarial tests (8/8) + detector refinements`.

Strand detection build session. Delivered: hand-curated ground truth (committed before detection ran), detection module with written specification, adversarial test suite (8/8 pass), verification runs on all three ground-truth sources with perfect precision/recall.

Commits this session:
- `88bfda4` — ground truth document (DfE KS3 Maths: 6 strands; NZ SS: 4 strands; Welsh CfW H&W: single-strand)
- `e05fad8` — detection module (`curriculum_harness/reference_authoring/strand/detect_strands.py`) with spec
- `b714e7a` — adversarial tests (8 cases) + detector refinements (bullet-density window stops at heading candidates; cross-cutting pattern expansions)

Ground-truth precision/recall:
- DfE KS3 Maths: 6 TP, 0 FP, 0 FN (precision=1.00, recall=1.00)
- NZ Curriculum Social Sciences: 4 TP, 0 FP, 0 FN (precision=1.00, recall=1.00)
- Welsh CfW Health & Wellbeing: single_strand (correct)

No flags raised by detector on any ground-truth source. Full test suite: 109 pass, 3 skipped (pre-existing integration skips), 0 fail.

## 2. Verified working

- **Strand detection module — complete (4c-3a).** `curriculum_harness/reference_authoring/strand/detect_strands.py`. Domain-agnostic structural detector with written specification. Adversarial suite: 8/8 pass. Ground-truth precision/recall: 1.00/1.00 on both DfE KS3 Maths (6 strands) and NZ SS (4 strands). Welsh CfW H&W correctly identified as single-strand (lens-heading detection path).
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

**4c-3b — Sub-run orchestration and stitching.** Strand detection is complete and verified. Next step: wire `detect_strands()` into the pipeline so that each detected strand is run as a sub-run through Phases 1-5. Stitch sub-run outputs into a unified reference corpus with strand-level provenance preserved. See `docs/plans/curriculum-harness-remaining-build-plan-v5.md` for full spec.

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
- **Second hierarchical source gap.** DfE KS3 Maths (full programme) failed ratio gate. Scoped re-ingestion (one strand only) needed in 4c-3a.
- **AP US Gov rubric flag rate after 4c-2b gate recalibration.** Not yet re-run. Pick up in 4c-3a or dedicated session.

---

*Last updated 2026-04-19 at end of Session 4c-3a. Update at end of every session per `docs/process/state-md-discipline.md`.*
