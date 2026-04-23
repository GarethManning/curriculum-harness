# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v5.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session REAL-3 (Unified wellbeing data files)** — 2026-04-23 — head `826d6bb feat: unified wellbeing data files + build script for all 19 LTs`.

Built two machine-readable artefacts from the expanded 19-LT REAL Wellbeing Framework (criterion-bank-v2.json, KUD session files) using a deterministic Python build script.

- `scripts/build_unified_wellbeing.py` — loads criterion-bank-v2.json, hardcoded KUD (know/understand/do) for all 19 LTs from three KUD session files, builds per-(lt_id, band) lookups and emits both output files.
- `docs/reference-corpus/real-wellbeing/unified-wellbeing-data.json` — full per-LT/per-band data: know, understand, do arrays, criterion_ids, prerequisite_lt_ids, observation_indicators (T3 LTs only).
- `docs/reference-corpus/real-wellbeing/wellbeing-index.json` — slim one-entry-per-LT index with competency, knowledge_type, compound flag, band_range, summary.
- KUD source documents (Sessions 1–3, ScopeAndSequence, Critique) also committed.

Step 5 verification: all 5 checks PASS — 19 LTs, all 169 criterion_ids valid, all 6 T3 LTs have observation_indicators in every band, no missing do fields, all 8 competency groups (C1–C8) in index.

LT 1.3 type: treated as T2 (criterion bank primary source; KUD Session 1's T3 label overridden per PROMPT_STANDARDS.md).

---

**Session CW-3 (Five-framework neutral matrix crosswalk v3)** — 2026-04-21 — head `abf3202 feat: CW-3 five-framework neutral matrix crosswalk v3`.

Applied curriculum-crosswalk skill v2.0 to produce framework-neutral matrix across all five frameworks. 23 themes × 6 bands = 138 matrix rows. 52 rows where REAL = "—" (gap detection working). Confirmed structural REAL gaps: T15 (Personal Identity, A–F), T22 (Growth Mindset, A–F), T16 (Family Diversity, A–F), T18 (Bullying/Anti-Discrimination, A–F), T17 (Online Safety, A–B and D; partial C and E only). Confirmed REAL distinctive strengths: T12 (Wellbeing Science A–F), T13 (Health Evidence Literacy A–F), T14 (Metacognition A–F), T04 (Focused Attention A–F — unique Band F content). 4 theme_grouping_flags. 10 PLC questions in convergence document.

Outputs: `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v3-matrix.md`, `...-matrix.csv`, `...-summary.csv`, `...-convergence.md`. v1 and v2 files retained unchanged.

---

**Session CW-2b (Circle Solutions + CASEL Band F pipeline re-runs; 5-framework crosswalk v2)** — 2026-04-21 — head `740f22e fix: CW-2b complete pipeline runs for Circle Solutions and CASEL; regenerate five-framework crosswalk v2`.

Circle Solutions: full pipeline re-run for all 4 year-level strands after API credit exhaustion in CW-2. 124 KUD items, 104 LTs (v1 manual: 112/48). Band-tagged v2 written. v1 archived to `_manual-archive/`. detect_progression.py fixed: per-strand inventory has `source_slug=strand-year-X` (no "circle-solutions" in slug); added `source_reference` matching on "cowie-myers" to detect correctly.

CASEL: grade-band-11-12 pipeline re-run restores Band F (halt was `call_or_parse_failed` from API exhaustion, not genuine T2/T3 ambiguity — prior STATE was incorrect). 28 KUD items, 14 LTs. Unified KUD/LTS updated (175→203 items, 79→93 LTs). Band-tagged CASEL v2 written.

5-framework crosswalk v2: `real-wellbeing-x-all-frameworks-v2.md` + `.csv`. 83 convergence rows (v1: 71), updated CS quotes to pipeline LT definitions throughout, 8 new CASEL Band F convergence rows, 2 new CS Band F rows (dehumanization/systemic empathy; social justice action). Verification: (a) CS pipeline-generated ✓ (b) CASEL Band F 28 KUD/14 LTs ✓ (c) both in v2 crosswalk ✓ (d) CSV 83 rows > 71 ✓.

---

**Session CW-2 (CASEL × Circle Solutions install, band-tag, and 5-framework crosswalk)** — 2026-04-21 — head `115421f [CW-2] CASEL × Circle Solutions install, band-tag, and 5-framework crosswalk`.

CASEL SEL Skills Continuum (January 2023): full harness pipeline run (multi-strand, 7 grade bands). 175 KUD items, 79 LTs, Bands A–E (Band F = 0, pipeline halt: 5 grade-band-11-12 blocks `classification_unreliable`). `band-tagged-casel-v1.json`: all fields, source_voice_preserved=true, band_confidence=high throughout.

Circle Solutions SEL Framework (Cowie & Myers 2016): pipeline bypassed due to API credit exhaustion during Year 2 KUD classification. Manually constructed from source verbatim: 112 KUD items, 48 LTs, 4 year levels. Year 2→Bands A/B (ambig, medium confidence), Year 6→Band C (high), Year 9→Bands D/E (ambig, medium), Year 12→Band F (high). API credit requires top-up before Circle Solutions can be run through the full harness pipeline.

Harness infrastructure: `detect_progression.py` — added `casel_sel_grade_band` and `circle_solutions_sel` source types; `detect_scope.py` — registered both as `explicit_progression` (high).

5-framework crosswalk: `real-wellbeing-x-all-frameworks-v1.md` — 71 convergent pairs (~38 high, ~27 apparent-only), 13 divergence topics, 5 unique-content clusters, 12 PLC questions. `real-wellbeing-x-all-frameworks-v1.csv` — 71 rows. Self-check (5 criteria) passed before commit. Commit `115421f`.

---

**Session CW-1 (REAL wellbeing × RSHE × Welsh CfW crosswalk v1)** — 2026-04-20 — head `2f92161 feat: CW-1 REAL wellbeing x RSHE x Welsh CfW crosswalk v1`.

PLC-ready crosswalk document produced from three band-tagged JSON inputs (REAL 84 items, RSHE 279 items, CfW 136 items). Full five-section output: 30 convergent pairs (11 high confidence, 19 apparent-only), 7 divergence topics with band-gap annotations, three unique-content subsections with verbatim quotes, 5 sequencing-difference prose analyses, 10 substantive PLC questions. All Band E/F cells marked "draft — teacher review pending" throughout. Self-check (5 criteria) passed before write.

Output: `docs/reference-corpus/crosswalks/real-wellbeing-x-rshe-x-cfw-v1.md` — commit `2f92161`.

---

**Session REAL-2a (REAL wellbeing framework — Band E/F extension + band-tagged JSON v1)** — 2026-04-20 — head `d60fd2b feat: REAL wellbeing framework extended to bands E-F; band-tagged JSON v1`.

Extended the REAL School Budapest wellbeing framework (14 LTs) from Bands A–D to Bands E and F, applying the six progression levers (independence, complexity, scope, precision, reasoning, transfer) consistently across all competencies. Produced full band-tagged JSON (84 items, 14 LTs × 6 bands). All verification checks PASS. Review gate completed (all 14 LT E/F Do statements confirmed) before JSON production.

Key results:
- source.md (Bands A–D, 14 LTs, 326 lines) ingested from ~/Downloads
- source-extended-ef.md: 14 LTs × 2 bands (E/F) authored from source
- band-tagged-real-wellbeing-v1.json: 84 items, all fields present, 4 teacher_review_flag=true (LT 3.2/4.1/4.2/5.2 Band D — source-flagged)
- Verification: 84 items ✓, all required fields ✓, band counts 14×6 ✓, 4 required flags exact match ✓

**Session HR-2c (Welsh CfW re-run on per-PS source + BT-3b band translation)** — 2026-04-20 — head `8f07fd5 feat: HR-2c re-run Welsh CfW on per-PS source; BT-3b band-tagged v2`.

Full pipeline re-run using `welsh-cfw-hwb-descriptions-of-learning.md` (per-PS descriptions of learning) as source, replacing the flat "Statements of what matters" source from BT-3. Source preprocessed to all-caps What Matters headings (depth 1) and numbered PS headings (depth 2), so inventory builder correctly tracks heading_path for every bullet. Pipeline cost: ~$6.36.

Key results:
- KUD items: 136 (T1=44, T2=58, T3=34) — vs 33 in BT-3 run on flat source
- LTs: 45 (T1=9, T2=21, T3=15)
- Rubrics: 30 (0 halted)
- Architecture: `welsh_cfw_aole`, 5 bands PS1–PS5, `developmental_scope: explicit_progression`
- All KUD items carry `source_block_id` referencing specific PS section via `heading_path` ✓

Band translation BT-3b:
- PS→REAL mapping applied per canonical table: PS1→A, PS2→B/C, PS3→C/D, PS4→D/E, PS5→E/F
- Confidence: **100% medium** (0% low — vs 97% low in BT-3). Major improvement.
- 19 PS1 items → Band A (unambiguous), 117 PS2-PS5 items → 2-band spans (medium, ambiguous)
- Output: `docs/reference-corpus/welsh-cfw-health-wellbeing/band-tagged-cfw-v2.json`
- Pre-HR2c artefacts archived to `_pre-hr2c-archive/`

---

**Session BT-3 (REAL Band Translation — Welsh CfW Health & Wellbeing)** — 2026-04-20 — head `a45ae3f feat: BT-3 band-tagged Welsh CfW output v1`.

REAL Band Translation skill applied to Welsh CfW Health & Wellbeing AoLE. Band-tagged artefact produced and committed. 33 KUD items and 20 LTs tagged. All verification checks PASS. Key finding: Welsh CfW "Statements of what matters" has no per-item Progression Step labels — canonical PS→REAL mapping table was not applicable per item. All 32 non-career items default to Bands A–E (low confidence, teacher_review_flag true). 1 career-pathway item narrowed to Bands D–E by content inference (medium confidence). Skill generalises to Welsh CfW source type, but produces a "flat framework" result rather than a per-PS mapped result. To get PS-level mapping, Welsh CfW achievement outcomes documents (one per PS) would be needed as a separate source pass.

Output: `docs/reference-corpus/welsh-cfw-health-wellbeing/band-tagged-cfw-v1.json` (now archived to `_pre-hr2c-archive/`)

REAL Band Translation skill applied to Welsh CfW Health & Wellbeing AoLE. Band-tagged artefact produced and committed. 33 KUD items and 20 LTs tagged. All verification checks PASS. Key finding: Welsh CfW "Statements of what matters" has no per-item Progression Step labels — canonical PS→REAL mapping table was not applicable per item. All 32 non-career items default to Bands A–E (low confidence, teacher_review_flag true). 1 career-pathway item narrowed to Bands D–E by content inference (medium confidence). Skill generalises to Welsh CfW source type, but produces a "flat framework" result rather than a per-PS mapped result. To get PS-level mapping, Welsh CfW achievement outcomes documents (one per PS) would be needed as a separate source pass.

Output: `docs/reference-corpus/welsh-cfw-health-wellbeing/band-tagged-cfw-v1.json`

---

**Session BT-2 (REAL Band Translation — RSHE)** — 2026-04-20 — head `7ecb8c3 feat: BT-2 band-tagged RSHE output v1`.

REAL Band Translation skill applied to UK statutory RSHE reference corpus. Band-tagged artefact produced and committed. 279 KUD items and 44 LTs tagged. End of Primary → Bands A–C (medium confidence, teacher_review_flag). End of Secondary → Bands C–E (medium confidence, teacher_review_flag). 20 cross-band LTs (spanning both source phases) → Bands A–E (low confidence). All 4 verification checks PASS. Adversarial spot-check: 5/5 defensible.

Output: `docs/reference-corpus/uk-statutory-rshe/band-tagged-rshe-v1.json`

---

**Session HR-1b (UK statutory RSHE cleanup — 3 fixes)** — 2026-04-20 — head `ee61a2a [HR-1b Fix 3] Rubric retry`.

Three cleanup fixes applied to `uk-statutory-rshe` corpus and harness infrastructure:

| Fix | File | Change |
|---|---|---|
| Fix 1 — type3_distribution gate | `kud_gates.py`, `run_pipeline.py`, `docs/threshold-revisions.md` | Source-type-aware thresholds: national_statutory_curriculum→5%, horizontal_dispositional→15%, default→20%. Pipeline loads architecture-diagnosis.json for context. |
| Fix 2a — e-drop regex bug | `generate_band_statements.py` | `\brecognize(ing)\b` didn't match "recognizing". Fixed with `stem(e[sd]?|ing)` pattern for e-ending verbs. Added `express` to OBSERVABLE_VERBS. |
| Fix 2b — compound construct | `generate_band_statements.py` | Documented limitation: gate checks verb presence but not single-construct. "express...while recognizing" passes. Fix belongs at LT authoring time. |
| Fix 3 — unreliable rubrics | rubrics.json, criteria.json, criterion_bank.json | 5 rubric_unreliable LTs retried at temperature=0.2. All 5 resolved: 4 stable, 1 rubric_unstable. Criterion bank: 84→86 criteria. |

Artefact update — `uk-statutory-rshe`:
- band_statements.json: 33→34 sets (cluster_06_lt_01 promoted from halted; statement was valid, halt was a validator bug)
- rubrics.json / criteria.json: 34 rubrics, 0 halted (was: 5 unreliable stubs)
- criterion_bank.json: 86 criteria, DAG PASS (was: 84 criteria — 5 LTs had no levels)

Commits this session:
- `f330cbb` — Fix 1: type3_distribution gate source-type-aware thresholds + docs/threshold-revisions.md
- `ed298c7` — Fix 2: e-drop regex + express verb + cluster_06_lt_01 promotion
- `ee61a2a` — Fix 3: rubric retry (5 LTs) + criterion bank regeneration

**Session HR-1 (UK statutory RSHE full programme)** — 2026-04-20 — head `5b61bb6 [HR-1] uk-statutory-rshe reference corpus — pipeline run complete`.

Full reference corpus produced for DfE statutory RSHE July 2025 (full programme: primary relationships education + primary health + secondary RSE + secondary health). 9th reference corpus. New `source_type: national_statutory_curriculum`, new `progression_structure: england_rshe_full` (2-band). Architecture disagreement resolved: session brief expected KS1-4 (4 bands); actual document structure is 2-phase (End of Primary / End of Secondary) — confirmed by Gareth, implemented as Option A. Pipeline cost: ~$12.00 ($11.42 pipeline + $0.57 criterion bank).

Commits this session:
- `6b5568b` — uk-statutory-rshe source acquisition + progression detection (detect_progression.py updated)
- `5b61bb6` — uk-statutory-rshe full pipeline artefacts + criterion bank

Key results — HR-1:

| Artefact | Result |
|---|---|
| Architecture diagnosis | national_statutory_curriculum, horizontal_dispositional_mixed, 2-band (End of Primary / End of Secondary) |
| KUD items | 279 (T1=195, T2=67, T3=17) |
| KUD gates | source_coverage PASS, traceability PASS, artefact_count_ratio PASS, type3_distribution FAIL (informational — 6.1% T3; RSHE is propositionally framed), no_compound_unsplit PASS |
| Clusters | 19 |
| LTs | 44 (T1=15, T2=19, T3=10), 1 halted cluster |
| Band statements | 33 sets (28 stable, 5 unstable 2/3), 1 halted (no_observable_verb) |
| Observation indicators | 10 sets (8 stable, 2 unstable) |
| Rubrics | 34 total, 26 pass, 8 gate failures (5 generation-unreliable, 3 semantic) |
| Supporting components | 18 |
| Criteria (criterion bank) | 84 |
| Prerequisite edges | 27 |
| DAG | PASS (no cycles, self-loops, unresolved IDs) |
| Over-decomposition flag | cluster_16_lt_01 (6 criteria — confirmed legitimate, distinct RSHE health topics) |
| Session cost | ~$12.00 |

**Prior session REAL-1 (REAL School Budapest wellbeing framework)** — 2026-04-20 — head `7459132 [REAL-1] generate_real_wellbeing.py`.

Full reference corpus produced for REAL School Budapest's internal wellbeing framework (7 competencies, 14 LTs, Bands A–D). New `source_type: internal_school_framework`. Architecture diagnosis, KUD classification (161 items), LT gate-check (14/14 pass), criterion bank (107 criteria, 247 edges, DAG PASS). This is the 8th reference corpus, first internal-school-framework source. Pass 2 edge generation switched to deterministic (LLM JSON too large for 107 criteria). Gate verb check improved with morphological normalisation. Session cost: ~$0.97.

Commits this session:
- `ba31f43` — source.md ingested (REAL-1 pre-work)
- `3e00f23` — architecture-diagnosis.json
- `a0ab671` — KUD classification + LT gate-check
- `21ca944` — criterion-bank.json (107 criteria, 247 edges, DAG PASS)
- `68fe0bd` — quality-report.json + readable-output/
- `7459132` — generate_real_wellbeing.py

Key results — REAL-1:

| Artefact | Result |
|---|---|
| Architecture diagnosis | internal_school_framework, explicit_progression, horizontal_dispositional |
| KUD items | 161 (146 source-derived, 15 AI-inferred) |
| LT gate | 14/14 pass, 7 warnings |
| Band gate | 0 failures, 4 warnings |
| Criteria (T1) | 9 |
| Criteria (T2) | 78 |
| Criteria (T3/obs) | 20 |
| Total criteria | 107 |
| Prerequisite edges | 247 |
| DAG | PASS (no cycles, self-loops, or unresolved IDs) |
| Session cost | ~$0.97 |

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

- **Unified wellbeing data files — complete (REAL-3).** `docs/reference-corpus/real-wellbeing/unified-wellbeing-data.json` (all 19 LTs, full KUD + criterion_ids + observation_indicators per band) and `wellbeing-index.json` (slim LT index). Build script: `scripts/build_unified_wellbeing.py`. Verification: 19 LTs ✓, 169 valid criterion_ids ✓, T3 obs indicators in all bands ✓, no missing do fields ✓, all C1–C8 ✓. Commit `826d6bb`.
- **5-framework neutral matrix crosswalk v3 — complete (CW-3).** `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v3-matrix.md` + `.csv` + `summary.csv` + `convergence.md`. 23 themes, 138 matrix rows, 52 REAL gap rows. skill v2.0 applied. Commit `abf3202`.
- **5-framework crosswalk v2 — complete (CW-2b).** `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v2.md` + `.csv`. 83 convergent pairs, 14 divergence topics, 5 unique-content clusters, 5 PLC questions. CSV: 83 rows. CASEL Band F and CS pipeline-generated v2 both present. Commit `740f22e`.
- **CASEL SEL band-tagged artefact v2 — complete (CW-2b).** `docs/reference-corpus/casel-sel-continuum/band-tagged-casel-v2.json`. 203 KUD items + 93 LTs, Bands A–F. Band F: 28 KUD items, 14 LTs (restored after API credit re-run). All required fields, source_voice_preserved=true.
- **Circle Solutions SEL band-tagged artefact v2 — complete (CW-2b).** `docs/reference-corpus/circle-solutions-sel/band-tagged-circle-solutions-v2.json`. 124 KUD items + 104 LTs, 4 year levels, pipeline-generated. Year 2→Bands A/B (ambig, medium confidence), Year 6→Band C (high), Year 9→Bands D/E (ambig, medium), Year 12→Band F (high). v1 manual archived to `_manual-archive/`.
- **5-framework crosswalk v1 — complete (CW-2).** `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v1.md` + `.csv`. 71 convergent pairs. Superseded by v2 but retained for reference. Commit `115421f`.
- **REAL × RSHE × Welsh CfW crosswalk v1 — complete (CW-1).** `docs/reference-corpus/crosswalks/real-wellbeing-x-rshe-x-cfw-v1.md`. PLC-ready Markdown. 30 convergent pairs (11 high, 19 apparent-only), 7 divergence topics, unique-content and sequencing sections, 10 PLC questions. Commit `2f92161`.
- **Welsh CfW Health & Wellbeing band-tagged artefact v2 — complete (HR-2c + BT-3b).** `docs/reference-corpus/welsh-cfw-health-wellbeing/band-tagged-cfw-v2.json`. 136 KUD items + 45 LTs tagged. 100% medium confidence (0% low). PS→REAL canonical mapping applied. 19 PS1 items → Band A (unambiguous); PS2–PS5 → 2-band spans. source_voice_preserved: true on all items. architecture-diagnosis.json present with developmental_scope: explicit_progression. Pre-HR2c artefacts in `_pre-hr2c-archive/`.
- **UK statutory RSHE band-tagged artefact — complete (BT-2).** `docs/reference-corpus/uk-statutory-rshe/band-tagged-rshe-v1.json`. 279 KUD items + 44 LTs tagged with REAL bands. End of Primary → [A,B,C], End of Secondary → [C,D,E], cross-band LTs → [A,B,C,D,E]. All verification checks PASS. source_voice_preserved: true on all 279 items.
- **UK statutory RSHE reference corpus — complete (HR-1 + HR-1b).** `docs/reference-corpus/uk-statutory-rshe/`. DfE July 2025 statutory RSHE, full programme. 19 clusters / 44 LTs / 2 bands (End of Primary + End of Secondary). source.md, architecture-diagnosis.json, inventory.json, kud.json (279 items), lts.json, band_statements.json (34 sets, 0 halted), observation_indicators.json (10 sets), rubrics.json (34 rubrics, 0 halted), criterion_bank.json (86 criteria / DAG PASS), quality_report.json, readable-output/. New source_type: `england_rshe_full` in detect_progression.py. Session cost: HR-1 ~$12.00 + HR-1b ~$0.40 rubric retries.
- **REAL wellbeing framework band-tagged JSON v1 — complete (REAL-2a).** `docs/reference-corpus/real-wellbeing/band-tagged-real-wellbeing-v1.json`. 84 items (14 LTs × 6 bands A–F). All high confidence, no ambiguity. 4 teacher_review_flag=true on source-flagged cells. source-extended-ef.md carries Bands E/F authored content. Commit d60fd2b.
- **REAL School Budapest reference corpus — complete (REAL-1).** `docs/reference-corpus/real-wellbeing-2026-04/`. 7 competencies / 14 LTs / 4 bands. architecture-diagnosis.json, kud-by-competency-by-band.json, lt-by-band.json, criterion-bank.json (107 criteria / 247 edges), quality-report.json, readable-output/. DAG PASS. Generator: `scripts/generate_real_wellbeing.py`. New source_type: `internal_school_framework`. Deterministic edge generation (Pass 2). Morphological verb normalisation for gate checks.
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

**QA phase — REAL wellbeing framework.** The criterion bank and unified data file have known quality problems identified 2026-04-23. The QA phase must complete before any programme guide or dashboard work begins. Steps in strict order:

1. Review Prompt 1 output (generic descriptor rewrite — Opus session complete 2026-04-23). Read printed sample entries and confirm descriptors are criterion-specific and register-consistent. [GATE — human sign-off required]
2. Run Prompt 2 Phase 1: decomposition audit. Produces decomposition-candidates.md only. No file modifications.
3. Review decomposition-candidates.md and approve proposed splits. [GATE — human sign-off required]
4. Run Prompt 2 Phase 2: execute approved decompositions (Opus).
5. Fix flat prerequisite structure: audit all 19 LTs for prerequisite_lt_ids that don't hold at early bands. Fix band-by-band (Sonnet).
6. Panel review all 19 KUD charts: five-persona panel, Opus, chat session. Any LT below 88 requires revision. [GATE — human sign-off required]
7. Factual accuracy check: LT 6.1 neuroscience content, with web search.
8. Review T3 observation indicators for LTs 1.1, 1.2, 3.2, 7.2, 8.3 — five-persona panel. [GATE — human sign-off required]
9. Rebuild unified-wellbeing-data.json and wellbeing-index.json from all corrected sources (Sonnet).
10. Final cross-artefact consistency check: criterion IDs, entry counts, DAG, T3 indicators, schema versions. [GATE — human sign-off required]

Invocation:
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model sonnet

## 6. Open questions

- **LOW confidence tier not seen in any run.** Defined in 4c-1; hasn't fired yet.
- **Ontario LT halts on large Opus clusters.** Carry-forward from 4b-5. Pick up in 4c-7.
- **AP US Gov rubric flag rate after 4c-2b gate recalibration.** Not yet re-run.
- **RSHE KUD count (149 vs expected 30-55).** Defensible — RSHE bullets contain multiple sub-items. Not a gate failure.

---

*Last updated 2026-04-23 — Two panel-flagged descriptor fixes applied to crit_0041 and crit_0023. Descriptor QA gate passed (panel score 89/100). Next: Prompt 2 Phase 1 decomposition audit. Update at end of every session per `docs/process/state-md-discipline.md`.*
