# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v5.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session 4c-4 (anchor sources)** — 2026-04-19 — head `3cd7831 [4c-4] Criterion bank generation and adversarial test scripts`.

Criterion bank produced for three anchor sources: Welsh CfW H&W, Common Core 7.RP, Ontario G7 History. Pre-work committed first (schema docs, decomposition rules, DAG validation rules, hand-curated validation sets). Two-pass generation (decompose+describe per LT, then prerequisite edges whole-bank). Post-generation scope reviews on Welsh and Ontario identified and removed 7 criteria total (4 Ontario, 3 Welsh — over-decomposition and scope drift). All three pass DAG validation and meet the 50% agreement-rate floor.

Commits this session:
- `af22afa` — Pre-work: criterion-bank-v1.md updated (strand field), criterion-decomposition-rules-v1.md, dag-validation-rules-v1.md, hand-curated-prerequisite-edges-v1.md
- `ef8fa15` — Welsh CfW H&W criterion bank (22 criteria, DAG validated)
- `a689bd7` — Common Core 7.RP criterion bank (16 criteria, DAG validated)
- `d8a4d16` — Ontario G7 History criterion bank (26 criteria, DAG validated)
- `3cd7831` — Generation and adversarial test scripts

Key results:
- Welsh CfW H&W: 22 criteria / 14 Type 1+2 LTs / DAG pass / primary agreement 100% (9/9) / secondary 89% / actual cost $0.18
- Common Core 7.RP: 16 criteria / 8 LTs / DAG pass / primary 92% (11/12) / secondary 92% / actual cost $0.12
- Ontario G7 History: 26 criteria / 11 Type 1+2 LTs / DAG pass / primary 100% (12/12) / secondary 92% / actual cost $0.22
- Total actual cost: $0.52 across 3 sources (well under $30 ceiling)
- Adversarial tests: 8/8 pass
- criteria.json → rubrics.json rename: OK on all 3 sources (same keys, counts, gate-fail counts)
- LT-level prerequisite_lts regenerated from criterion bank on all 3 sources; 0 lossy cases

Post-generation scope corrections (not auto-fixed — manual review):
- Welsh: 3 removed (crit_0002/0003 merged into 0001 for enumerated-examples violation; crit_0019 hallucinated content)
- Common Core: 2 orphan criteria had missing prerequisites added manually (crit_0014, crit_0015)
- Ontario: 4 removed (scope drift / conceptual drift per horizontal spot-check); 1 statement fixed (causes removed from recall LT); 1 direct edge added (recall→consequence). Spot-check approved by Gareth Manning.

Recurring pattern: generator consistently over-decomposes recall/explanatory LTs that enumerate examples (e.g. "physical activity, nutrition, sleep"), splitting examples into separate criteria. Decomposition rules correctly prohibit this but prompt does not reliably prevent it. Flag for 4c-4b: tighten Pass 1 prompt with explicit example.

## 2. Verified working

- **Criterion bank — 3 anchor sources complete (4c-4).** Welsh CfW H&W (22 criteria), Common Core 7.RP (16 criteria), Ontario G7 History (26 criteria). Schema v1. DAG validated on all 3. `scripts/generate_criterion_bank.py`, `scripts/test_criterion_bank_adversarial.py`.
- **Criterion bank schema v1 — updated (4c-4).** `docs/schemas/criterion-bank-v1.md` — `strand` field now mandatory; `"single_strand"` sentinel for single-strand sources.
- **Criterion decomposition rules v1 — written (4c-4).** `docs/schemas/criterion-decomposition-rules-v1.md`.
- **DAG validation rules v1 — written (4c-4).** `docs/schemas/dag-validation-rules-v1.md`. Two-level agreement (primary floor 50%, secondary diagnostic).
- **Hand-curated prerequisite edges — approved (4c-4).** `docs/validation/hand-curated-prerequisite-edges-v1.md`. 9 Welsh + 12 Common Core + 12 Ontario edges. Approved by Gareth Manning 2026-04-19.
- **Strand detection module — complete (4c-3a/4c-3b).** `curriculum_harness/reference_authoring/strand/detect_strands.py`. Adversarial suite: 8/8 pass. Ground-truth precision/recall: 1.00/1.00 on DfE KS3 Maths and NZ SS.
- **Multi-strand orchestration + stitching — complete (4c-3b).** `orchestrate.py`, `stitch.py`.
- **Pipeline strand detection wiring — complete (4c-3b).** `run_pipeline.py`.
- **NZ Social Sciences reference corpus (4c-3b).** `docs/reference-corpus/nz-ss-social-sciences-4c3b/`. 4 strands, 326 KUD / 59 LTs / 57 rubrics.
- **DfE KS3 Maths reference corpus (4c-3b).** `docs/reference-corpus/dfe-ks3-maths-4c3b/`. 6 strands, 65 KUD / 29 LTs.
- **Phase 0 acquisition layer — complete.** Five source-type primitives; manifest schema 0.6.0; ten ingestion artefacts.
- **AP US Gov CED Unit 1 reference — complete (4c-1 re-run).** 26 LTs / 26 rubrics / 50 flags.
- **Secondary RSHE 2025 reference — complete (4c-2b).** 149 KUD / 26 clusters / 66 LTs / 62 rubrics.
- **Reference-authoring criterion gates — recalibrated (4c-2b).** OBSERVABLE_VERBS expanded to 44. Adversarial suite: 16/16 pass.
- **Reference-authoring pipeline — Sonnet default (4c-2a).** Token logging complete.
- **Reference-authoring pipeline v0.6 — halts-to-flags shipped (4c-1).**
- **VALIDITY.md populated.** Seven validator scripts plus `run_all.py` driver.

## 3. Verified broken

- **English-only Phase 1 cue list.** `curriculum_harness/phases/phase1_ingestion.py:202-245`.
- **Hardcoded GCSE_AQA_EXAM_BLOCK in Phase 4.** `curriculum_harness/phases/phase4_lt_generation.py:132-138`.
- **Phase 5 strand routing.** `curriculum_harness/phases/phase5_formatting.py:70-86`.
- **Phase 3 flag-and-continue for `classification_unreliable`.** Phase 3 still emits items without a regeneration loop.
- **`_lemmatise()` derivational morphology.** `-ful`/`-fully` morphology, hyphen splitting, name/identify coupling. Causes 2 persistent single_construct false positives on RSHE 2025. Scoped to 4c-2c.
- **Criterion bank Pass 1 prompt: enumerated-example over-decomposition.** Generator consistently splits "explain how [A, B, C]" LTs into per-example criteria, violating decomposition Rule 4. Required manual fix on Welsh and would likely recur on 4c-4b sources. Prompt tightening needed before 4c-4b.

## 4. Unverified

- **RSHE 2025 Type 3 rate (3.4%).** Teacher review needed to confirm whether this reflects the source's propositional framing or a classification limitation.
- **Phase 3 consolidation collapse on felvételi.** Observable only in a Phase 3 run output.
- **Reference-authoring gate pass rates for Welsh CfW / Common Core under a fresh re-run.** Not re-verified since 4c-1. Now superseded: rubrics.json is the renamed artefact.
- **AP US Gov rubric flag rate after gate recalibration.** Not yet re-run.
- **4c-4b criterion banks (4 remaining sources).** AP US Gov, Secondary RSHE 2025, DfE KS3 Maths, NZ Social Sciences. Not yet generated.

## 5. Next session

**4c-4b — Criterion bank for remaining 4 sources.** Before running generation, tighten Pass 1 prompt to prevent enumerated-example over-decomposition (add explicit example showing "physical activity, nutrition, sleep → 1 criterion, not 3"). DfE KS3 Maths and NZ Social Sciences are multi-strand — set `strand` field to the strand slug, not `"single_strand"`. RSHE 2025 is predominantly Type 3 — confirm which LTs are Type 1/2 and eligible before generation.

**4c-2c (deferred) — Lemmatiser improvements.** Defer unless teacher review flags the 2 persistent single_construct false positives as blocking.

Invocation:
```
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model sonnet
```

## 6. Open questions

- **Enumerated-example over-decomposition in Pass 1.** Confirmed pattern across Welsh and Ontario. Fix: add explicit counter-example to Pass 1 prompt before 4c-4b. Decomposition rules correctly prohibit this; prompt enforcement is what's needed.
- **RSHE KUD count (149 vs expected 30-55).** Defensible — RSHE bullets contain multiple sub-items. Not a gate failure.
- **LOW confidence tier not seen in any run.** Defined in 4c-1; hasn't fired yet.
- **Ontario LT halts on large Opus clusters.** Carry-forward from 4b-5. Pick up in 4c-7.
- **AP US Gov rubric flag rate after 4c-2b gate recalibration.** Not yet re-run. Pick up in 4c-4b or dedicated session.

---

*Last updated 2026-04-19 at end of Session 4c-4 (anchor sources). Update at end of every session per `docs/process/state-md-discipline.md`.*
