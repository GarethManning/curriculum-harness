# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v5.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session 4c-5 (developmental scope detection)** — 2026-04-20 — head `25608eb [4c-5] architecture-diagnosis-schema.md`.

`developmental_scope` and `developmental_scope_confidence` detection added to architecture diagnosis. New module `curriculum_harness/reference_authoring/developmental_scope/detect_scope.py`. Curated source_type map covers all 7 harness source types. Content inspection path for `nz_curriculum` (Level-marker scan). Flag emission (`developmental_scope_range_without_bands`) with domain_type metadata and layered pedagogical explanations. Adversarial tests 8/8. Verification against 7 existing sources 7/7. Token cost: trivial (no LLM calls).

Commits this session:
- `c247d43` — developmental scope detection module + adversarial tests (8/8)
- `43dbe93` — verification script — 7 existing sources match expected scope (7/7)
- `25608eb` — architecture-diagnosis-schema.md

Session 4c-4b (prior, for history):
**Session 4c-4b (remaining criterion banks)** — 2026-04-19 — head `00a692c [4c-4b] NZ Social Sciences criterion bank`.

Criterion banks generated for all 4 remaining sources: AP US Gov CED Unit 1, Secondary RSHE 2025, DfE KS3 Maths, NZ Social Sciences. Pre-work committed first (Pass 1 prompt fix for enumerated-example over-decomposition, adversarial Test 9). All 4 pass DAG validation. No enumerated-example violations post-fix. One scope-drift correction (RSHE 2025 crit_0065 removed). NZ SS per-strand LT ID collision discovered and fixed (strand-slug prefixing for multi_strand_per_dir sources). Horizontal spot-check on NZ SS (5 LTs) approved by Gareth Manning 2026-04-19. Total 4c-4b cost: ~$1.62. Combined 7-source cost: ~$2.14.

Commits this session:
- `7651eea` — Pass 1 prompt fix (enumerated-example counter-example) + adversarial Test 9
- `989bd5b` — `scripts/generate_criterion_bank_4c4b.py` (4-source generator)
- `102a97e` — AP US Gov CED Unit 1 criterion bank (42 criteria, DAG pass)
- `489152c` — Secondary RSHE 2025 criterion bank (108 criteria, DAG pass)
- `c6823df` — DfE KS3 Maths criterion bank (69 criteria, 6 strands, DAG pass)
- `00a692c` — NZ Social Sciences criterion bank (115 criteria, 4 strands, DAG pass)

Key results — 4c-4b sources:

| Source | Criteria | Edges | DAG | Corrections | Cost |
|---|---|---|---|---|---|
| AP US Gov CED Unit 1 | 42 | 28 | Pass | None | ~$0.30 |
| Secondary RSHE 2025 | 108 | 42 | Pass | crit_0065 removed (scope drift) | ~$0.52 |
| DfE KS3 Maths | 69 | 64 | Pass | None | ~$0.32 (est) |
| NZ Social Sciences | 115 | 76 | Pass | LT ID collision fix (prefixing) | $0.80 |

All-session totals (4c-4 + 4c-4b — all 7 sources):
- Welsh CfW H&W: 22 / 20 edges / $0.18
- Common Core 7.RP: 16 / 24 edges / $0.12
- Ontario G7 History: 26 / 31 edges / $0.22
- AP US Gov: 42 / 28 edges / ~$0.30
- Secondary RSHE 2025: 108 / 42 edges / ~$0.52
- DfE KS3 Maths: 69 / 64 edges / ~$0.32
- NZ Social Sciences: 115 / 76 edges / $0.80
- **Total: 398 criteria / 285 edges / ~$2.46**

Adversarial tests: 9/9 pass (Tests 1–8 from 4c-4, Test 9 from 4c-4b).

Enumerated-example prompt fix: held on all 4 sources — no enumerated-example violations detected post-fix.

LT-level prerequisite_lts regenerated: AP US Gov (15 LTs), RSHE 2025 (20 LTs), DfE KS3 Maths (20 LTs), NZ SS (30 LTs). 0 lossy cases on all.

Renaming regression: criteria.json → rubrics.json (or unified_criteria.json → unified_rubrics.json) verified OK on all 4 new sources.

NZ SS horizontal spot-check (5 LTs): all 5 approved — correct horizontal-domain decomposition per Rule 4.

**Harness v5 criterion bank milestone: COMPLETE. All 7 reference sources have criterion banks.**

Post-generation corrections log:
- RSHE 2025 crit_0065: scope drift — "STI prevalence, health impacts, treatment facts" not in `cluster_15_lt_01` definition. Removed from criterion_bank.json, edges cleared, DAG re-validated.
- NZ SS LT ID collision: per-strand dirs all use identical LT IDs. Fixed by prefixing with strand slug in `associated_lt_ids` and `all_lts`; prefix stripped when updating per-strand lts.json. Code fix in `generate_criterion_bank_4c4b.py`.

Critical failure pattern (saved to Second Brain): Per-directory multi-strand sources (`multi_strand_per_dir`) need strand-slug-prefixed LT IDs. Without prefixing, all criteria across all strands collapse to the same LT IDs in the decomposition audit.

Pass 2 truncation pattern: Fixed by scaling `max_tokens = min(8192, max(4096, len(criteria) * 100))`. For banks >60 criteria, a sparsity instruction is added (max ~3 edges per criterion). No truncation after fix.

## 2. Verified working

- **Developmental scope detection — complete (4c-5).** `curriculum_harness/reference_authoring/developmental_scope/detect_scope.py`. `DevelopmentalScopeResult` dataclass + `detect_developmental_scope()` + `make_developmental_scope_flag()`. Adversarial tests 8/8. Verification 7/7. Schema doc at `docs/schemas/architecture-diagnosis-schema.md`.
- **Criterion bank — all 7 sources complete (4c-4 + 4c-4b). HARNESS V5 COMPLETE.**
  - Welsh CfW H&W (22 criteria), Common Core 7.RP (16), Ontario G7 History (26), AP US Gov (42), Secondary RSHE 2025 (108), DfE KS3 Maths (69, 6 strands), NZ Social Sciences (115, 4 strands). Schema v1. DAG validated on all 7.
  - Scripts: `scripts/generate_criterion_bank.py` (anchor sources), `scripts/generate_criterion_bank_4c4b.py` (remaining 4), `scripts/test_criterion_bank_adversarial.py` (9/9 pass).
- **Criterion bank schema v1 — updated (4c-4).** `docs/schemas/criterion-bank-v1.md` — `strand` field mandatory; `"single_strand"` sentinel for single-strand sources.
- **Criterion decomposition rules v1 — written (4c-4).** `docs/schemas/criterion-decomposition-rules-v1.md`.
- **DAG validation rules v1 — written (4c-4).** `docs/schemas/dag-validation-rules-v1.md`.
- **Hand-curated prerequisite edges — approved (4c-4).** `docs/validation/hand-curated-prerequisite-edges-v1.md`. 9 Welsh + 12 Common Core + 12 Ontario edges.
- **Strand detection module — complete (4c-3a/4c-3b).** `curriculum_harness/reference_authoring/strand/detect_strands.py`. 8/8 pass.
- **Multi-strand orchestration + stitching — complete (4c-3b).** `orchestrate.py`, `stitch.py`.
- **Pipeline strand detection wiring — complete (4c-3b).** `run_pipeline.py`.
- **NZ Social Sciences reference corpus (4c-3b).** `docs/reference-corpus/nz-ss-social-sciences-4c3b/`. 4 strands. Criterion bank: 115 criteria / 76 edges. Horizontal spot-check approved.
- **DfE KS3 Maths reference corpus (4c-3b).** `docs/reference-corpus/dfe-ks3-maths-4c3b/`. 6 strands. Criterion bank: 69 criteria / 64 edges.
- **Phase 0 acquisition layer — complete.** Five source-type primitives; manifest schema 0.6.0; ten ingestion artefacts.
- **AP US Gov CED Unit 1 reference — complete (4c-1 re-run).** 26 LTs / 26 rubrics. Criterion bank: 42 criteria / 28 edges.
- **Secondary RSHE 2025 reference — complete (4c-2b).** 149 KUD / 26 clusters / 66 LTs / 62 rubrics. Criterion bank: 108 criteria / 42 edges.
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

## 4. Unverified

- **RSHE 2025 Type 3 rate (3.4%).** Teacher review needed to confirm whether this reflects the source's propositional framing or a classification limitation.
- **Phase 3 consolidation collapse on felvételi.** Observable only in a Phase 3 run output.
- **AP US Gov rubric flag rate after gate recalibration.** Not yet re-run.
- **Reference-authoring gate pass rates for Welsh CfW / Common Core under a fresh re-run.** Not re-verified since 4c-1.

## 5. Next session

**Track 1b — Band decomposer scoping review.** Review scope and approach for the band decomposer tool (single-grade planning from `range_without_bands` sources). The three affected sources (RSHE 2025, DfE KS3 Maths, NZ SS) are now flagged with `developmental_scope_range_without_bands` at detection time. Band decomposer is the next architectural piece.

**4c-2c (deferred) — Lemmatiser improvements.** Fix `-ful`/`-fully` morphology, hyphen splitting, name/identify coupling in `_lemmatise()`. Defer unless teacher review flags the 2 persistent single_construct false positives as blocking.

Invocation:
```
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model sonnet
```

## 6. Open questions

- **LOW confidence tier not seen in any run.** Defined in 4c-1; hasn't fired yet.
- **Ontario LT halts on large Opus clusters.** Carry-forward from 4b-5. Pick up in 4c-7.
- **AP US Gov rubric flag rate after 4c-2b gate recalibration.** Not yet re-run.
- **RSHE KUD count (149 vs expected 30-55).** Defensible — RSHE bullets contain multiple sub-items. Not a gate failure.

---

*Last updated 2026-04-20 at end of Session 4c-5 (developmental scope detection). Update at end of every session per `docs/process/state-md-discipline.md`.*
