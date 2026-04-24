# STATE.md — Curriculum Harness

Live state register. Updated at the end of every Claude Code session. Distinct from `docs/plans/curriculum-harness-remaining-build-plan-v5.md` (forward-looking) and `docs/project-log/harness-log.md` (historical). See `docs/process/state-md-discipline.md` for update protocol.

## 1. Last session

**Session REAL-10 (Phase 1 — crosswalk v4 refresh against 21-LT framework)** — 2026-04-24 — COMMITTED `8acd20b`.

Phase 1 crosswalk refresh v4 produced. Framework-neutral matrix, summary CSV, and convergence document covering the current 21 REAL LTs against RSHE, Welsh CfW, CASEL, and Circle Solutions. Seven LTs new since v3 integrated (LT 1.3, 4.3, 4.4, 4.5, 8.1, 8.2, 8.3). Three gap changes. 84 LT × framework pairs labelled. v3 preserved as historical record.

- **real-wellbeing-x-all-frameworks-v4-matrix.md** — `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v4-matrix.md`. 403 lines. 23-theme structure inherited from v3. Change log at top documents v3→v4 changes. Skill_flags and theme_grouping_flags updated. New "Per-LT alignment forms" section at bottom (84 pairs).
- **real-wellbeing-x-all-frameworks-v4-summary.csv** — `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v4-summary.csv`. 24 rows (23 themes + header), 16 columns. Added REAL_primary_LTs and v3_to_v4_change columns.
- **real-wellbeing-x-all-frameworks-v4-convergence.md** — `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v4-convergence.md`. 232 lines. Five-section structure (convergence / divergence / unique / sequencing / PLC questions) preserved from v3. New convergence subsection for v4-specific content. Bidirectional gap summary added.
- **Three gap changes:** T15 (Personal Identity) closed by LT 1.3 (A–F); T18 (Bullying/Anti-Discrimination) closed by LT 4.3 (A–F); T17 (Online Safety/Digital Wellbeing) flipped from partial gap to distinctive strength via LT 8.1 + LT 8.2 + LT 8.3 (A–F).
- **84 LT × framework pairs labelled** using four alignment forms: 19 `aligned-with-reciprocal-treatment`, 42 `partial-alignment`, 0 `reversed`, 23 `absent`. The `reversed` form was available but no pair qualified in this pass; closest candidates classified as `partial-alignment` with grain difference stated.
- **Spot-check:** Gareth manually verified five randomly-selected alignment statements against their source texts. 5/5 held.
- **REAL gaps preserved:** T22 (Growth Mindset — LT 7.2 adjacent but not identical), T16 (Family Diversity — out of scope by design), T19 (Physical Activity — PE delivery context), T20 (Nutrition — LT 3.1 brief integration only), T03 Bands A–B, T21 Bands A–B.
- **Convention changes (documented in change log):** per-LT alignment-form labels (new in v4); bidirectional gap flagging made explicit; blanket *(draft)* markers on Bands E–F dropped post QA Step 6 PASS (LT 4.2 Band D/F teacher-review flag retained).
- **Current state:** 21 LTs, 269 criteria, 267 unified-data edges. Preflight 12/12 PASS. Crosswalk v4 committed at `8acd20b`.
- **This session did NOT:** run panel review on v4 artefacts; modify any criterion bank, unified data, KUD, or skill files; modify v3 crosswalk files (preserved as historical record).

---

**Session REAL-9d (Phase 0.3 — panel-review skill v1.0.0 → v1.0.1 deployed to claude-education-skills)** — 2026-04-24 — COMMITTED.

Built and deployed the panel-review skill (v1.0.0, then v1.0.1 cleanup) at `skills/professional-learning/panel-review/SKILL.md` in the claude-education-skills repo. Seven-role depersonalised panel, sequential-isolation mode. Reviews five artefact types: KUD, criterion bank, LT definition, crosswalk, scope-and-sequence (with documented panel-weakness caveat). Gate rule: mean_overall ≥ 88 AND no role mean < 70. Worked example produced mean 88.25 with sceptic at 66.67 — FAIL verdict via the floor rule, validating that the rule catches what it's designed to catch. Skill count 113 → 114. v1.0.1 cleanup removed school-specific references to keep the skill domain-agnostic for the public skills library.

- **panel-review skill v1.0.0** — `skills/professional-learning/panel-review/SKILL.md` in claude-education-skills repo. Commit `72e2c77`. Seven roles: Lead Curriculum Designer, Assessment Specialist, Pedagogical Theory Expert, Practitioner (classroom teacher), Sceptic, Equity & Inclusion Lens, Subject Expert. Sequential-isolation mode: each role's review conducted in a separate conversational segment to prevent cross-contamination. Five supported artefact types: KUD chart, criterion bank, LT definition, crosswalk, scope-and-sequence.
- **panel-review skill v1.0.1** — follow-up commit in claude-education-skills removing school-specific references. Removed REAL School Budapest naming from worked examples and prompt text to keep skill domain-agnostic for the public skills library.
- **Gate rule:** mean_overall ≥ 88 AND no role mean < 70 (floor rule). Both conditions must pass independently.
- **Worked example result:** mean_overall 88.25, sceptic role 66.67 → FAIL verdict via floor rule. Validates that the floor rule catches role-level failures even when the mean passes.
- **Panel-weakness caveat documented:** scope-and-sequence reviews are subject to reduced panel validity given the panel's lack of implementation context. Documented in skill.
- **Skill count:** 113 → 114.
- **PROMPT_STANDARDS.md interim note closed:** "Interim note on panel mode" section updated to record Phase 0.3 as shipped in sequential-isolation mode. Prior caveat removed as of 24 April 2026.
- **Current state:** 21 LTs, 269 criteria, 267 unified-data edges. Preflight 12/12 PASS. Panel-review skill deployed, not yet verified against real artefacts.
- **This session did NOT:** invoke the panel-review skill on any real REAL Wellbeing artefact (Phase 0.3 verification); validate the 88 threshold (Phase 0.5); implement full parallel-API mode; modify any criterion bank, unified data, or KUD files.

---

**Session REAL-9c (Phase 0.2 Pass B — preflight 8→12 checks + PROMPT_STANDARDS gate criteria, specificity rule, gate-failure procedure)** — 2026-04-24 — COMMITTED.

Extended preflight from 8 to 12 checks (criterion-to-LT integrity, LT-to-criterion integrity, orphan detection, criterion-level prerequisite DAG). Added four new sections to PROMPT_STANDARDS.md: preflight session-start discipline, specificity rule, named gate criteria (four gates), gate-failure procedure (three-cycle). Interim notes documented for shared-context panel mode (until Phase 0.3) and 88 threshold (until Phase 0.5).

- **scripts/preflight.py — extended to 12 checks.** New Check 9 (criterion→LT referential integrity: every `associated_lt_ids` entry resolves in unified data; lt_type matches unified knowledge_type where populated). New Check 10 (LT→criterion referential integrity: every `criterion_ids` reference in unified-data bands resolves in the criterion bank). New Check 11 (orphan detection, both directions: criteria with no valid LT refs; LTs with zero criteria associating back). New Check 12 (criterion-level prerequisite edge integrity + DAG validity over `prerequisite_criterion_ids`). Check 3 relabelled "DAG validity, unified" to disambiguate from Check 12. Output format updated; OVERALL aggregates all 12.
- **PROMPT_STANDARDS.md — four new sections appended.** "Preflight as session-start discipline" (unskippable; every session runs preflight first and pastes full output into the session report; twelve checks enumerated). "Specificity rule" (blind-band identification test; Adjacency and Observable-behaviour sub-tests; five-random-criterion measurement procedure for Gate 2). "Named gate criteria" (Gate 1 KUD→criteria invokes kud-chart-author Checks 1–6; Gate 2 criteria→unified; Gate 3 unified→artefact; Gate 4 artefact→publication; interim note on shared-context panel mode removed when Phase 0.3 ships; note on 88 threshold validated or recalibrated when Phase 0.5 ships). "Gate-failure procedure" (three-cycle escalation: targeted revision → expanded-scope revision → methodology review).
- **Preflight 12/12 PASS** on 269 criteria / 21 LTs / 267 unified-data edges / 523 criterion-level prereq edges. Check 9: 269/269 refs valid, 0 broken. Check 10: 21/21 LTs with all refs valid, 269/269 band→criterion refs valid. Check 11: 0 criterion orphans, 0 LT orphans. Check 12: 523/523 edges valid, DAG OK. First end-to-end verification that the criterion bank and unified data are mutually referentially consistent at both directions; no broken refs or orphans surfaced.
- **Current state:** 21 LTs, 269 criteria, 267 unified-data edges, 523 criterion-bank prereq edges. Preflight 12/12 PASS. Commit: `6d1b174`.
- **This session did NOT:** implement independent panel mode (Phase 0.3); draft teacher validation protocol (Phase 0.4); validate the 88 threshold (Phase 0.5); modify any skill files; modify the kud-chart-author skill's Check 1–6 definitions (they are canonical; PROMPT_STANDARDS.md references them, does not redefine them).

---

**Session REAL-9b (Phase 0.1C — deprecate generate_real_wellbeing.py to scripts/legacy/)** — 2026-04-24 — COMMITTED.

Deprecated `scripts/generate_real_wellbeing.py` — confirmed legacy by investigation (wrong output path `real-wellbeing-2026-04/` vs live `real-wellbeing/`, schema v1 vs live v2, missing T3 observation fields, not wired to any pipeline, last run REAL-1 2026-04-20). Moved to `scripts/legacy/` with README. Preflight Check 6 scoped to exclude `scripts/legacy/`. Preflight 8/8 PASS.

- **scripts/legacy/generate_real_wellbeing.py** — archived from `scripts/generate_real_wellbeing.py` via `git mv` (history preserved). Archived notice block added after existing docstring. Import of `band_constants` will fail from new location by design — not runnable without path surgery and schema migration.
- **scripts/legacy/README.md** — explains archival rationale, preflight exemption, and per-file deprecation notes. Documents last run (REAL-1, 2026-04-20) and archive date (REAL-9b, 2026-04-24).
- **scripts/preflight.py Check 6** — `check_no_inline_band_labels()` now skips any path with `"legacy"` in its parts. Comment added explaining the exemption. Check 6 PASS confirmed.
- **Current state:** 21 LTs, 269 criteria, 267 unified-data edges. Preflight 8/8 PASS. Commit: `6ec0825`.
- **This session did NOT:** delete the script (archival, not deletion); modify `scripts/build_criterion_bank_v2.py` (still active); add preflight integration checks 9–12 (Phase 0.2 Pass B); touch PROMPT_STANDARDS.md (Phase 0.2 Pass B); attempt to make the legacy script runnable from its new location.

---

**Session REAL-9a (Phase 0.1 + Phase 0.1B — canonical band convention, preflight, bug fixes)** — 2026-04-24 — COMMITTED.

Phase 0.1 (commit cbaaccc) established canonical band convention as single machine-readable source at `band-conventions.json`; `band_constants.py` loader exposes it to all scripts; `preflight.py` runs session-start checks; 11 files reconciled to canonical band labels. Phase 0.1B (this commit) closes two bugs and extends preflight from six to eight checks.

- **band-conventions.json** — `docs/reference-corpus/real-wellbeing/band-conventions.json`. Canonical REAL band metadata. Six bands A–F. Bands E and F: grade-only identifiers, no Dragon names, ages_approx null. Phase 0.1, commit cbaaccc.
- **band_constants.py** — `scripts/band_constants.py`. Loads BAND_META, BAND_LABELS, VALID_BAND_LETTERS from band-conventions.json at import time. Raises ImportError if missing or malformed. Phase 0.1, commit cbaaccc.
- **preflight.py — extended to 8 checks (Phase 0.1B).** `scripts/preflight.py`. Checks 1–6 from Phase 0.1; Checks 7 (unified data band_label walk) and 8 (band-conventions.json self-check) added in Phase 0.1B. All 8 PASS. Exit 0 on all-pass, 1 on any fail.
- **LT 4.4 KUD v2 — Band E/F age ranges fixed (Phase 0.1B).** `docs/reference-corpus/real-wellbeing/LT_4_4_KUD_v2_20260423.md`. Non-canonical age ranges "14–16" (Band E) and "16–18" (Band F) removed from Band Statements table and section headers; replaced with canonical grade-level identifiers "G9–10" and "G11–12". Change log entry added.
- **generate_real_wellbeing.py — BANDS list fixed (Phase 0.1B).** `scripts/generate_real_wellbeing.py`. `BANDS = ["A", "B", "C", "D"]` replaced with `BANDS = sorted(BAND_META.keys())`. Hardcoded `* 4` band-count in diagnostic print replaced with `* len(BANDS)`. Previously would have silently skipped Bands E and F if invoked.
- **Check 7 (unified data bands)** — walks all band_label fields in unified data JSON, asserts canonical. Unified data has zero band_label fields; PASS with note.
- **Check 8 (canonical self-check)** — loads band-conventions.json directly, asserts version/source_of_truth/6-band structure. PASS.
- **Current state (post-Phase 0.1B):** 21 LTs, 269 criteria, 267 unified-data edges (523 criterion-bank edges), all 8 preflight checks PASS.
- **This session did NOT:** Phase 0.2 (named gate criteria and gate-failure procedure in PROMPT_STANDARDS.md); uk_years field; CASEL/Circle prose fixes; markdown prose in live docs; archived bank versions.

---

**Session REAL-8e (LT 4.5 observation exemplar library — Bands D and F)** — 2026-04-24 — COMMITTED.

Authored observation exemplar library for LT 4.5 — Emotional Self-Management in Practice — covering Band D (three criteria) and Band F (four criteria). Seven exemplar sections, each with authentic observation vignettes, confusable-behaviour anchors, absence indicators, and observer-calibration notes. Bands A, B, C, E deferred to v2.

- **LT_4_5_exemplar_library_v1_20260424.md** — `docs/reference-corpus/real-wellbeing/LT_4_5_exemplar_library_v1_20260424.md`. Bands D and F. Seven criteria: crit_0319–crit_0321 (Band D), crit_0325–crit_0328 (Band F). Format matches T3 observation protocol appendices (LT 7.2 Band F and LT 8.3 Band F). School-agnostic; age-appropriate to G7–8 (Band D) and G11–12 (Band F). 6,436 words.
- **Priority calibration emphases:** crit_0321 distinguishes student-initiated repair from teacher-brokered acknowledgement (timing + specificity of self-acknowledgement); crit_0326 distinguishes relationship-motivated repair from consequence-motivated repair (timing relative to consequence + framing of forward step — hardest Band F calibration call); crit_0328 applies partial-evidence protocol explicitly — components 1–3 typically met before component 4; a student may legitimately meet 1, 2, or 3 without yet meeting 4.
- **Cross-band Section 3** added: two recurring calibration patterns across Band D and Band F — authenticity vs performance of authenticity; student-under-stress vs student presentation.
- **Outstanding commissions unchanged:** extend T3 observation protocol to include LT 4.5 cross-references (next session); emotional-activation safeguarding protocol; exemplar library v2 (Bands A, B, C, E).
- **This session did NOT:** push to remote; extend T3_observation_protocol_20260423.md itself; author Bands A/B/C/E exemplars; run panel review on exemplar library; modify any existing file.

---

**Session REAL-8d (LT 4.5 unified data integration — v6)** — 2026-04-24 — COMMITTED.

Integrated LT 4.5 — Emotional Self-Management in Practice — into the unified wellbeing data, producing `unified-wellbeing-data-v6.json` and `wellbeing-index-v6.json`. All 10 verification checks PASS. Framework now at 21 LTs.

- **unified-wellbeing-data-v6.json** — `docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v6.json`. 21 LTs (was 20), 269 criteria, 523 edges. lt_4_5 inserted after lt_4_4 in C4 competency group.
- **wellbeing-index-v6.json** — `docs/reference-corpus/real-wellbeing/wellbeing-index-v6.json`. 21 LT index entries. lt_4_5 index entry present.
- **build_unified_wellbeing_v6.py** — `scripts/build_unified_wellbeing_v6.py`. Build script for v6 outputs.
- **lt_4_5 criterion coverage** — 16 criterion_ids (crit_0313–crit_0328) resolved from criterion-bank-v5_1.json. All 6 bands (A–F) populated. T3 observation_indicators populated in all bands (8–16 indicators per band). All 10 verification checks PASS.
- **KUD v4 consolidated index left untouched** — covers 19 LTs (1.1–8.3). LT 4.4 and LT 4.5 live in separate KUD files. unified-wellbeing-data-v6.json is the canonical framework-wide view for all 21 LTs.
- **REAL-8b/REAL-8c STATE.md correction** — criterion-bank-v5.json was committed at d42a6ec and criterion-bank-v5_1.json at 21702f6; the STATE.md snapshot at a65b5fe predated both commits and incorrectly recorded REAL-8b as "NOT COMMITTED".
- **This session did NOT:** run panel review on LT 4.5 KUD or criterion bank; author observation exemplar library for LT 4.5 (Band D rupture-and-repair; Band F pattern-articulation); produce the emotional activation safeguarding protocol; author the programme guide; update the T3 observation protocol to include LT 4.5.

---

**Session REAL-8c (criterion-bank-v5_1 band label reconciliation)** — 2026-04-24 — COMMITTED `21702f6`.

Applied canonical band_label values to all 16 LT 4.5 entries in criterion-bank-v5.json, producing `criterion-bank-v5_1.json`. All band_labels confirmed canonical. DAG PASS. Criterion count and edge count unchanged.

- **criterion-bank-v5_1.json** — `docs/reference-corpus/real-wellbeing/criterion-bank-v5_1.json`. 269 criteria, 523 edges, DAG PASS. All band_labels canonical. criterion-bank-v5.json unchanged.
- **This session did NOT:** commit STATE.md; integrate into unified-wellbeing-data; author observation exemplar library.

---

**Session REAL-8b (LT 4.5 criterion bank generation)** — 2026-04-24 — COMMITTED `d42a6ec`.

Generated 16 T3 criterion bank entries for LT 4.5 — Emotional Self-Management in Practice — producing `criterion-bank-v5.json`. All post-generation verification checks PASS. DAG PASS.

- **criterion-bank-v5.json** — `docs/reference-corpus/real-wellbeing/criterion-bank-v5.json`. 269 criteria (253 v4_1 + 16 new), 523 total edges, DAG PASS. criterion-bank-v4_1.json unchanged.
- **16 new LT 4.5 T3 criteria** — IDs `crit_0313`–`crit_0328`. Bands A–F. All `lt_type: "Type 3"`. All T3 fields (observation_indicators, confusable_behaviours, absence_indicators, conversation_prompts) present and criterion-specific.
- **Band split:** A×2, B×2, C×2, D×3, E×3, F×4 — matching KUD v2 Check A table. All within-band components are parallel (no edges between co-band components).
- **17 new edges** — 14 `within_lt_band` (strand-matched developmental staging across bands) + 3 `cross_lt_source_stated` (crit_0306→crit_0320: LT 4.4 Band D framework → LT 4.5 Band D window-aware help-seeking; crit_0306→crit_0324: habit formation → strategy adaptation; crit_0311→crit_0326: LT 4.4 Band F Know item 3 relational repair → LT 4.5 Band F repair initiation).
- **Cross-LT edge correction:** The session summary said crit_0312→0326. Corrected to crit_0311→0326: kud_lt_4_4_F_know_03 (relational repair) is covered by crit_0311, not crit_0312 (which covers Band F Do only).
- **Canonical band labels** applied to all 16 new criteria.
- **comp_4 strand count** updated to 82 (was 66; LT 4.5 adds 16).
- **This session did NOT:** integrate into unified-wellbeing-data or wellbeing-index; run panel review on LT 4.5; author observation exemplar library for LT 4.5 (required: Band D rupture-and-repair exemplars; Band F pattern-articulation exemplars).

---

**Session REAL-8a (KUD v4 band label correction + commit)** — 2026-04-24 — COMMITTED `027b4c1`.

Corrected all non-canonical band labels across `REAL_Wellbeing_KUD_v3_20260423.md` to canonical grade-level convention, producing `REAL_Wellbeing_KUD_v4_20260424.md`. Committed v4 + LT_4_5_KUD_v2_20260423.md together.

- **REAL_Wellbeing_KUD_v4_20260424.md** — committed. Identical KUD content to v3; band labels corrected throughout. 163,949 bytes. 11/11 post-fix verification checks PASS.
- **LT_4_5_KUD_v2_20260423.md** — committed. KUD chart for LT 4.5 (Emotional Self-Management in Practice), T3 dispositional, Bands A–F.
- **Label changes applied:** consolidated index mapping line; band-scope lines with and without Dragon names; LT 4.2 partial B–F scope; LT 8.2 partial C–F scope; Part 1 band statement headers; Dragon-naming footnote; one authoring note age reference.
- **Canonical convention confirmed:** Band A — Water + Air Dragons — K–2 (approx ages 5–7); B — Earth Dragons — G3–4 (approx ages 8–10); C — Fire Dragons — G5–6 (approx ages 10–12); D — Metal + Light Dragons — G7–8 (approx ages 12–13); E — G9–10; F — G11–12. Metal and Light are both at Band D. Bands E and F have no Dragon names.
- **This session did NOT:** modify v3 (unchanged); touch any other file; commit STATE.md separately.

---

**Session REAL-7 (LT 4.4 commit + unified data v5 integration)** — 2026-04-23 — COMMITTED.

Committed criterion-bank-v4_1.json and LT_4_4_KUD_v2_20260423.md; rebuilt unified data and index at v5; updated STATE.md.

- **LT 4.4 — Emotional Development & Relationships** — now committed and integrated. 20th LT in the REAL Wellbeing Framework (Competency 4 now has four LTs: 4.1, 4.2, 4.3, 4.4).
- **criterion-bank-v4_1.json** — committed. 253 criteria, 506 edges, DAG PASS.
- **LT_4_4_KUD_v2_20260423.md** — committed. KUD v2 incorporating five-persona panel review changes (Band D Know items 4–5 populated; Band E Know item 2 expanded; Band F Know item 1 reframed).
- **unified-wellbeing-data-v5.json** — committed. 20 LTs, all 253 criteria referenced, 0 orphan criterion refs. LT 4.4 inserted after lt_4_3 in correct C4 competency position.
- **wellbeing-index-v5.json** — committed. 20 LT entries. lt_4_4 index entry present.
- **build_unified_wellbeing_v5.py** — committed. Build script for v5 outputs.
- **Note on LT count:** session brief specified "19 LTs in v5" — this was a counting error. v4 already had 19 LTs; adding lt_4_4 yields 20. The 20 LT count is correct.
- **Outstanding Competency 4 design commissions (deferred, not blocking):** (1) LT 4.5 — T3 companion LT for dispositional emotional self-management (Claxton panel flag; no T3 assessable content for mood regulation in C4 currently). (2) Emotional activation safeguarding protocol — for scenario tasks involving attraction, rejection, loss; to be produced with safeguarding lead and Circle Solutions programme.
- **This session did NOT:** apply no_evidence descriptor specificity polish; expand competent descriptor qualitative content; review cross-band strand-based edges; produce safeguarding protocol; author LT 4.5; run panel review on any other artefact.

---

**Session REAL-6b (LT 4.4 criterion bank targeted fix — v4_1)** — 2026-04-23 — NOT COMMITTED.

Applied three panel-flagged fixes to LT 4.4 entries from criterion-bank-v4.json, producing `criterion-bank-v4_1.json`. v4.json unchanged.

- **criterion-bank-v4_1.json** — `docs/reference-corpus/real-wellbeing/criterion-bank-v4_1.json`. 253 criteria (unchanged), 506 total edges (down from 515 — 9 parallel-component edges removed), DAG PASS.
- **FIX 1 — 9 parallel within-band edges removed.** These edges incorrectly modelled Band parallel-components as sequential prerequisites. Removed: crit_0298→0299, crit_0300→0301, crit_0302→0303, crit_0304→0305, crit_0305→0306, crit_0307→0308, crit_0308→0309, crit_0310→0311, crit_0311→0312. Kept (cross-band and cross-LT): 0299→0300, 0301→0302, 0054→0302, 0303→0304, 0057→0304, 0306→0307, 0309→0310. LT 4.4 edge count: 16→7.
- **FIX 2 — crit_0310 extending descriptor updated.** New text: "I use three or more frameworks and, for at least one (e.g. attachment theory), distinguish empirical core from contested interpretations and popularised distortions — explaining what each framework illuminates and obscures in this case." (236 chars). criterion_statement unchanged.
- **FIX 3 — crit_0306 extending descriptor updated.** New text: "I apply one course framework coherently to the experience and consistently distinguish empirical, interpretive, and normative claims throughout — noting which claims I hold most tentatively and why." (198 chars). criterion_statement unchanged.
- **This session did NOT:** commit; integrate into unified-wellbeing-data or wellbeing-index; apply no_evidence descriptor specificity polish; expand competent descriptor qualitative content; review cross-band strand-based edges; author T3 companion LT; produce safeguarding protocol.

---

**Session REAL-6 (LT 4.4 criterion bank generation)** — 2026-04-23 — NOT COMMITTED (awaiting panel review gate).

Generated criterion bank entries for LT 4.4 — Emotional Development & Relationships — producing `criterion-bank-v4.json`. All three panel requirements honoured. No integration into unified data; no commit. File ready for human review.

- **criterion-bank-v4.json** — `docs/reference-corpus/real-wellbeing/criterion-bank-v4.json`. 253 criteria (238 v3 + 15 new LT 4.4 entries), 515 total edges (499 v3 + 16 new), DAG PASS. criterion-bank-v3.json unchanged (MD5 verified).
- **15 new LT 4.4 criteria** — IDs `crit_0298`–`crit_0312`. Bands A–F. All Type 2. All descriptors ≤250 chars (validated). Specificity rule applied to every descriptor.
- **16 new edges** — 14 `within_lt_band` (linear A→B→C→D→E→F chain) + 2 `cross_lt_source_stated` (LT 4.2 Band C `crit_0054` → LT 4.4 Band C `crit_0302`; LT 4.2 Band D `crit_0057` → LT 4.4 Band D `crit_0304`).
- **Requirement 1 (Band D three-component split) HONOURED.** `crit_0304`: biological explanation accuracy (PFC/amygdala + attraction/rejection/loss neurobiology). `crit_0305`: healthy/unhealthy pattern identification in described relationship. `crit_0306`: course framework application (dual-process, stress-response window, habit formation) with epistemic-status distinction. Three separate descriptor sets.
- **Requirement 2 (Band F framework set named) HONOURED.** `crit_0310` explicitly names: attachment theory, dual-process models of emotion and cognition, social learning theory, power/context analysis. Competent = ≥2 frameworks; Extending = ≥3 frameworks + framework evaluation.
- **Requirement 3 (Band F justified position operationalised) HONOURED.** `crit_0312` descriptors explicitly encode all four dimensions: evidentiary fit (competent), alternative explanations (competent), framework transparency (competent), acknowledgement of limits (competent). Extending = all four as integrated argument.
- **This session did NOT:** commit; integrate into unified-wellbeing-data or wellbeing-index; author the T3 companion LT for Competency 4; produce the emotional-activation safeguarding protocol.

---

**Session REAL-5 (QA phase — Steps 6 and 8 + KUD v3 + unified v4)** — 2026-04-23 — head `aeae1cd fix: LT 7.1 Know layer + prerequisite hardening; LT 1.3 Band D indicator wording; observation exemplar library (23 Apr 2026)`.

Completed QA Step 6 (whole-chart five-persona panel review, all 19 LTs) and QA Step 8 (T3 observation indicator five-persona panel review, six T3 LTs). Panel output: `docs/reference-corpus/real-wellbeing/REAL_Wellbeing_QA_Steps_6_8_20260423.md` (commit `0bc3b49`). Both gates PASS at framework level.

- **QA Step 6** — PASS (framework mean 90.3). LT 4.2 (86.6) and LT 7.1 (87.8) flagged. LT 7.1 flag resolved by KUD v3 edits (see below). LT 4.2 flag deferred to unit-plan session — chart not structurally broken; Band D cognitive-load split and Band F contested-claim curation protocol required before Band D field use.
- **QA Step 8** — PASS (T3 indicator mean 89.5). LT 1.3 (87.8) flagged. Flag resolved by Band D behavioural-anchor replacement and exemplar library (see below). Christodoulou's Band F four-observation consolidation recommendation was **not adopted**; partial-evidence recording protocol substituted in the exemplar library. Dissent to be recorded in the T3 observation protocol document.
- **KUD v3** — `docs/reference-corpus/real-wellbeing/REAL_Wellbeing_KUD_v3_20260423.md` is the current canonical KUD chart file. Changes from v2: LT 7.1 standalone Know layer added at all bands A–F (own metacognitive terminology; LT 6.1 neuroscience Know cross-reference preserved as companion note); LT 6.1 Band C retyped from conceptual accelerator to **hard prerequisite** for LT 7.1 Band D; Claxton dissent recorded verbatim in LT 7.1 authoring notes; LT 1.3 Band D observation indicator behavioural-anchor replacement applied (Christodoulou wording).
- **criterion-bank-v3.json** — 238 criteria, **499 edges** (up from 491), DAG PASS. `hard_prerequisite` edge type added to schema (8 edges, all LT 6.1 Band C → LT 7.1 Band D: `crit_0080` and `crit_0082` → `crit_0101`, `crit_0102`, `crit_0180`, `crit_0181`). Edge-addition log at `docs/reference-corpus/real-wellbeing/v3-edge-addition-log-lt-6-1-to-7-1-20260423.md`.
- **Unified v4** — `docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v4.json` and `wellbeing-index-v4.json`. Current unified artefacts; built from criterion-bank-v3.json (499 edges) and KUD v3. v3 unified files retained as historical record per no-overwriting rule.
- **LT 1.3 exemplar library** — `docs/reference-corpus/real-wellbeing/LT_1_3_observation_exemplar_library_20260423.md`. Bands D and F: two "met" anchors, one false-positive anchor, one false-negative anchor per band; Band F partial-evidence recording protocol for observers.
- **Path convention** — canonical location for all REAL wellbeing artefacts is `docs/reference-corpus/real-wellbeing/`, not `docs/wellbeing/` or `data/wellbeing/`.

---

**Session REAL-4 (QA phase — criterion bank v3 + Steps 5 and 7)** — 2026-04-23 — head `a25dd5f fix: rebuild unified data and index against v3 bank post-anchoring fixes (23 Apr 2026)`.

Completed QA Steps 1–5 and Step 7 of the REAL wellbeing QA phase. Regenerated the criterion bank and unified data files against the corrected KUD v2 charts, then fixed anchoring and prerequisite structure issues surfaced during the rebuild.

- `criterion-bank-v3.json` — 238 criteria, 491 edges, DAG PASS. Supersedes v2. Per PROMPT_STANDARDS no-overwriting rule, v2 retained as `criterion-bank-v2.json` and the pre-descriptor-fix intermediate as `criterion-bank-v2-pre-descriptor-fix.json`.
- `crit_0297` added — LT 6.1 Band F action-primacy T1 criterion. Resolves Band F under-anchoring on the hierarchical-science LT.
- 49 `cross_lt_source_stated` edges added to resolve Band E/F under-anchoring across LTs 6.1, 5.1, 3.1, 7.1, 8.2.
- LT 5.1 Band F anchor repointed from `crit_0213` to `crit_0212` (correct mechanism anchor for intercultural register calibration).
- `PROMPT_STANDARDS.md` — T2/T3 `within_lt_band` semantic distinction documented (commit `844c8af`).
- Schema docs updated: `docs/schemas/criterion-bank-v1.md` and `docs/schemas/dag-validation-rules-v1.md` now carry Rule 6 on `within_lt_band` edge semantics (commit `a9533d9`).
- `unified-wellbeing-data-v3.json` and `wellbeing-index-v3.json` built and committed against the v3 bank (commit `a25dd5f`). These are the current unified artefacts. v2 versions retained as historical record.
- QA Step 5 (prerequisite structure fix): 237 → 200 edges (37 removed) for band-by-band soft-enabler downgrades at early bands; propagated into the v3 bank. Edge-removal log at `docs/reference-corpus/real-wellbeing/v3-edge-removal-log.md`.
- QA Step 7 (neuroscience factual accuracy check on LT 6.1) — PASS. One note: "stress-emotion-attention-habit system" is curriculum synthesis language, not a named neuroscientific model; footnote recommended in programme guide, no criterion rewrite needed.

Note: LT 1.3 type correction to T3 (was recorded as T2 in error) was applied in a prior session; this entry reflects the current corrected state (section 2 below references it at the earlier REAL-3 entry).

---

**Session REAL-3 (Unified wellbeing data files)** — 2026-04-23 — head `826d6bb feat: unified wellbeing data files + build script for all 19 LTs`.

Built two machine-readable artefacts from the expanded 19-LT REAL Wellbeing Framework (criterion-bank-v2.json, KUD session files) using a deterministic Python build script.

- `scripts/build_unified_wellbeing.py` — loads criterion-bank-v2.json, hardcoded KUD (know/understand/do) for all 19 LTs from three KUD session files, builds per-(lt_id, band) lookups and emits both output files.
- `docs/reference-corpus/real-wellbeing/unified-wellbeing-data.json` — full per-LT/per-band data: know, understand, do arrays, criterion_ids, prerequisite_lt_ids, observation_indicators (T3 LTs only).
- `docs/reference-corpus/real-wellbeing/wellbeing-index.json` — slim one-entry-per-LT index with competency, knowledge_type, compound flag, band_range, summary.
- KUD source documents (Sessions 1–3, ScopeAndSequence, Critique) also committed.

Step 5 verification: all 5 checks PASS — 19 LTs, all 169 criterion_ids valid, all 6 T3 LTs have observation_indicators in every band, no missing do fields, all 8 competency groups (C1–C8) in index.

LT 1.3 type: T3 — Dispositional (corrected 23 April 2026; prior T2 treatment was an error; authoritative source lt-1-3-personal-identity-cultural-self-awareness-v1.md line 17 declares T3; criterion bank T2 entries removed in regeneration session 23 April 2026)

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

- **Crosswalk v4 — complete (REAL-10, `8acd20b`).** `docs/reference-corpus/crosswalks/real-wellbeing-x-all-frameworks-v4-{matrix.md, summary.csv, convergence.md}`. Framework-neutral crosswalk against 21 REAL LTs. Three gap changes (T15, T18 closed; T17 flipped to distinctive strength). 84 LT × external-framework alignment pairs labelled. Gareth spot-check 5/5. v3 retained as historical record.
- **KUD charts v4 — committed (REAL-8a).** `docs/reference-corpus/real-wellbeing/REAL_Wellbeing_KUD_v4_20260424.md`. All band labels corrected to canonical grade-level convention. Content identical to v3. 163,949 bytes. Commit `027b4c1`. v3 retained as historical record.
- **LT 4.5 KUD v2 — committed (REAL-8a).** `docs/reference-corpus/real-wellbeing/LT_4_5_KUD_v2_20260423.md`. T3 dispositional LT, Bands A–F, 6 quality checks PASS. Commit `027b4c1`.
- **unified-wellbeing-data-v6.json — committed (REAL-8d).** `docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v6.json`. 21 LTs, 269 criteria, 523 edges. lt_4_5 (T3) inserted after lt_4_4 in C4 competency group. T3 observation_indicators populated from criterion-bank-v5_1.json. All 10 verification checks PASS.
- **wellbeing-index-v6.json — committed (REAL-8d).** `docs/reference-corpus/real-wellbeing/wellbeing-index-v6.json`. 21 LT index entries. IDs match unified data exactly.
- **criterion-bank-v5_1.json — committed (REAL-8c, `21702f6`).** `docs/reference-corpus/real-wellbeing/criterion-bank-v5_1.json`. 269 criteria, 523 edges, DAG PASS. All band_labels canonical. Supersedes criterion-bank-v5.json for all downstream use.
- **criterion-bank-v5.json — committed (REAL-8b, `d42a6ec`).** `docs/reference-corpus/real-wellbeing/criterion-bank-v5.json`. 269 criteria, 523 edges, DAG PASS. 16 new LT 4.5 T3 entries. Superseded by criterion-bank-v5_1.json (band_label reconciliation). Retained as historical record per no-overwriting rule.
- **KUD charts v3 — superseded by v4 (REAL-5; history).** `docs/reference-corpus/real-wellbeing/REAL_Wellbeing_KUD_v3_20260423.md`. Current canonical KUD. Changes from v2: LT 7.1 standalone Know layer at all bands A–F (own metacognitive terminology; LT 6.1 neuroscience cross-reference preserved as companion); LT 6.1 Band C → LT 7.1 Band D retyped to hard prerequisite; Claxton dissent recorded in LT 7.1 authoring notes; LT 1.3 Band D observation indicator behavioural-anchor replacement (Christodoulou wording). v2 retained as historical record. Commit `aeae1cd`.
- **Criterion bank v3 — complete (REAL-5 edges; REAL-4 base).** `docs/reference-corpus/real-wellbeing/criterion-bank-v3.json`. 238 criteria, **499 edges** (up from 491), DAG PASS. Supersedes v2. REAL-4 base incorporates: generic-descriptor rewrite (Prompt 1), approved decomposition splits (Prompt 2), `crit_0297` LT 6.1 Band F action criterion, 49 `cross_lt_source_stated` edges resolving Band E/F under-anchoring across LTs 6.1/5.1/3.1/7.1/8.2, LT 5.1 Band F anchor repointed `crit_0213`→`crit_0212`, band-by-band prerequisite soft-enabler downgrades (Step 5: 237→200 edges, 37 removed). REAL-5 addition: new `hard_prerequisite` edge type added to schema (8 edges, all LT 6.1 Band C → LT 7.1 Band D; `crit_0080` and `crit_0082` → `crit_0101`, `crit_0102`, `crit_0180`, `crit_0181`). Edge-addition log at `v3-edge-addition-log-lt-6-1-to-7-1-20260423.md`.
- **QA Step 6 — whole-chart panel review PASS (REAL-5).** Framework mean 90.3. LT 4.2 (86.6) and LT 7.1 (87.8) flagged. LT 7.1 flag resolved in KUD v3. LT 4.2 flag deferred to unit-plan session (chart not structurally broken; Band D sequencing plan and Band F contested-claim curation protocol required before Band D field use). Output: `REAL_Wellbeing_QA_Steps_6_8_20260423.md`.
- **QA Step 8 — T3 observation indicator panel review PASS (REAL-5).** T3 indicator mean 89.5. LT 1.3 (87.8) flagged. Flag resolved by Band D behavioural-anchor replacement and exemplar library at `LT_1_3_observation_exemplar_library_20260423.md`. Christodoulou Band F four-observation consolidation recommendation not adopted; partial-evidence recording protocol substituted.
- **Unified wellbeing data v4 — complete (REAL-5).** `docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v4.json` + `wellbeing-index-v4.json`. Current unified artefacts; built from criterion-bank-v3.json (499 edges) and KUD v3. v3 unified files retained as historical record per no-overwriting rule.
- **LT 1.3 observation-indicator exemplar library (REAL-5).** `docs/reference-corpus/real-wellbeing/LT_1_3_observation_exemplar_library_20260423.md`. Bands D and F: two "met" anchors, one false-positive anchor, one false-negative anchor per band; Band F partial-evidence recording protocol.
- **Path convention (REAL-5).** Canonical location for all REAL wellbeing artefacts is `docs/reference-corpus/real-wellbeing/`. Not `docs/wellbeing/` or `data/wellbeing/`.
- **Unified wellbeing data v3 — superseded by v4 (REAL-4; history).** `docs/reference-corpus/real-wellbeing/unified-wellbeing-data-v3.json` + `wellbeing-index-v3.json`. Built against criterion-bank-v3 (491-edge state) and KUD v2 charts. Retained as historical record. Commit `a25dd5f`.
- **QA Step 7 — neuroscience factual accuracy check on LT 6.1 — PASS (REAL-4).** Web-search-verified against authoritative neuroscience sources (amygdala, prefrontal cortex, HPA axis, neuroplasticity, allostatic load). One note: "stress-emotion-attention-habit system" is curriculum synthesis language, not a named neuroscientific model — footnote recommended in programme guide; no criterion rewrite needed.
- **Schema docs Rule 6 — within_lt_band edge semantics (REAL-4).** `docs/schemas/criterion-bank-v1.md` and `docs/schemas/dag-validation-rules-v1.md` now carry the T2/T3 `within_lt_band` semantic distinction per `PROMPT_STANDARDS.md` update (commit `844c8af`; schema doc update `a9533d9`).
- **Unified wellbeing data v2 — superseded by v3 (REAL-3; history).** `docs/reference-corpus/real-wellbeing/unified-wellbeing-data.json` (original Session REAL-3 output). Build script: `scripts/build_unified_wellbeing.py`. Retained as historical record. Commit `826d6bb`.
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

**First action next session: Gareth to decide.** Natural candidates after Phase 1 crosswalk v4 ship:
- **Programme guide authoring** (all 21 LTs, unified-wellbeing-data-v6.json as source; now gated open by crosswalk v4 + KUD stability)
- **Safeguarding protocol commission** for LT 4.4 (attraction / rejection / loss scenarios at Band D) and LT 4.5 (emotional-activation in practice)
- **LT 4.2 Band D/F unit-plan session** (deferred from QA Step 6: Band D sequencing plan; Band F contested-claim curation protocol)
- **T22 growth-mindset gap decision** (PLC question from v4: author dedicated LT, subsume into LT 7.2, or document out-of-scope)

**Prior first-action carried forward: Phase 0.3 verification — invoke the panel-review skill on LT 4.5 KUD v2 as a first real-run calibration.** Panel-review skill v1.0.1 is deployed in claude-education-skills; this session confirms it runs correctly against a real REAL Wellbeing artefact and that the gate rule (mean_overall ≥ 88, no role mean < 70) returns a defensible verdict. (Ran as commit `ed2c563` between REAL-9d and REAL-10; not yet folded into STATE.md.)

**Deferred — T3 observation protocol extension (reinstated after Phase 0.2 gate is in place).** Add LT 4.5 to `T3_observation_protocol_20260423.md` (currently covers LTs 1.1, 1.2, 1.3, 3.2, 7.2, 8.3 only). LT 4.5 requires a Band D rupture-and-repair section (distinguishing genuine initiation from defensive acknowledgement) and a Band F pattern-articulation section (distinguishing genuine model use from performed articulation).

**Open commissions for Competency 4 (not blocking other work):**
- **LT 4.5 observation exemplar library** — Band D (rupture-and-repair: distinguishing genuine initiation from defensive acknowledgement) and Band F (pattern articulation as working model: distinguishing genuine model use from performed articulation). Commission flagged in LT 4.5 authoring notes; not yet started.
- **Emotional activation safeguarding protocol** for scenario tasks involving attraction, rejection, loss. To be produced with safeguarding lead and Circle Solutions programme.
- **LT 4.2 unit-plan session** (deferred from QA Step 6): Band D sequencing plan; Band F contested-claim curation protocol. Required before Band D field use.

**Recommended downstream work (no gates blocking):**
- Programme guide authoring (all 21 LTs, unified-wellbeing-data-v6.json as source).
- Dashboard integration against unified-wellbeing-data-v6.json.
- LT 4.5 panel review on KUD and criterion bank (separate sessions per gate discipline).

**QA phase — REAL wellbeing framework — ALL 10 STEPS COMPLETE (prior state).** Step 10 cross-artefact consistency check run 23 April 2026 against v4 artefacts. All 10 checks PASS. Gate closed. v4 artefacts are verified and ready for programme guide and dashboard work.

1. ✅ Prompt 1 output review (generic descriptor rewrite).
2. ✅ Prompt 2 Phase 1 decomposition audit.
3. ✅ Decomposition split approvals.
4. ✅ Prompt 2 Phase 2 execution.
5. ✅ Flat prerequisite structure fix (Step 5: 237→200 edges).
6. ✅ Panel review all 19 KUD charts (Step 6, REAL-5, framework mean 90.3 PASS). LT 4.2 flag deferred to unit-plan session; LT 7.1 flag resolved by KUD v3.
7. ✅ Neuroscience factual accuracy check on LT 6.1.
8. ✅ Panel review T3 observation indicators for all six T3 LTs 1.1, 1.2, 1.3, 3.2, 7.2, 8.3 (Step 8, REAL-5, T3 indicator mean 89.5 PASS). LT 1.3 flag resolved by Band D behavioural-anchor replacement and exemplar library; Band F consolidation recommendation not adopted; partial-evidence protocol substituted.
9. ✅ Rebuild unified-wellbeing-data-v4.json and wellbeing-index-v4.json from KUD v3 and criterion-bank-v3 (499 edges).
10. ✅ **Final cross-artefact consistency check — PASS (23 Apr 2026).** All 10 checks passed against v4 artefacts. See QA summary below. One non-blocking flag: embedded `dag_validation` field in criterion-bank-v3.json is stale (shows 237 criteria / 439 edges, predating crit_0297 addition and REAL-5 hard_prerequisite edge additions). Actual data correct; fresh DAG run confirms 238 criteria, 499 edges, DAG PASS. Field does not affect artefact integrity.

**QA Step 10 results summary (23 Apr 2026):**

| Check | Expected | Actual | Result |
|---|---|---|---|
| 1 — Criterion count | 238 (bank) / 238 (unified unique IDs) | 238 / 238 | ✅ PASS |
| 2 — Edge count | 499 | 499 (from prerequisite_edges_detail across all criteria) | ✅ PASS |
| 3 — DAG validity | Valid DAG, 0 cycles, 0 dangling, 0 orphaned | Valid; 0 cycles; 0 dangling; 0 orphaned; edge-type dist: within_lt_band 318, cross_lt_source_stated 173, hard_prerequisite 8 | ✅ PASS |
| 4 — LT 1.3 knowledge_type | "T3" | "T3" | ✅ PASS |
| 5 — LT 1.3 Band D indicator | Does not contain "genuine reflection rather than surface performance" | Does not contain it. New wording: "The teacher notices the student…naming a specific unchosen group membership…giving a specific example of how that membership has shaped one of their own experiences — where the example is not a repetition of a class discussion example offered by a peer or teacher." | ✅ PASS |
| 6 — LT 7.1 Know A–F | None read "None standalone" | A: "There are two different kinds of thinking…" B: "A pattern is a response I make in a similar way in similar kinds of situations." C: "A driver of a pattern is a specific thing that sets the pattern off or keeps it going…" D: "The origin of a pattern (what originally set it up) and its sustaining conditions (what keeps it going now) are two different things." E: "A structured metacognitive protocol is a named sequence of steps applied in advance to a high-stakes challenge…" F: "A personal metacognitive framework is an explicit, named set of strategies, prompts, and monitoring practices…" | ✅ PASS |
| 7 — Hard prerequisite edges | 8 edges, all LT 6.1 Band C → LT 7.1 Band D | 8 edges: crit_0080→crit_0101, crit_0082→crit_0101, crit_0080→crit_0102, crit_0082→crit_0102, crit_0080→crit_0180, crit_0082→crit_0180, crit_0080→crit_0181, crit_0082→crit_0181 (all LT 6.1 Band C → LT 7.1 Band D) | ✅ PASS |
| 8 — Schema version consistency | Match | Both "v2" | ✅ PASS |
| 9 — 19 LTs present | 19 LTs, C1–C8 | 19 LTs, competencies C1–C8 all present | ✅ PASS |
| 10 — crit_0297 | T1, Band F, LT 6.1 | Type 1, Band F, lt_6_1. Statement: "I can apply an integrative understanding of the stress-emotion-attention-habit system (drawing on mechanisms from Bands A–E) to a real decision or situation in my own life or community, choosing an action that addresses the system rather than a single symptom and justifying the action by specific mechanisms." | ✅ PASS |

Deferred follow-ups (not blocking Step 10):
- **T3 authenticity observation protocol document** covering all six T3 LTs — authoring underway; includes the cross-cutting "authentic vs performative" operationalisation, LT 1.3 Band F partial-evidence protocol and Christodoulou dissent, LT 7.2 Band F and LT 8.3 Band F exemplar libraries as appendices, and LT 1.2 Band F calibration note.
- **LT 4.2 unit-plan session:** Band D sequencing plan splitting D content into ≥2 instructional sub-units; Band F contested-claim curation protocol (≥3 claims, paired evidence bases, curation principles). Required before Band D field use.

Invocation:
cd ~/Github/curriculum-harness && claude --dangerously-skip-permissions --model sonnet

## 6. Open questions

- **Framework-scope decision for T16, T19, T20, T22 (surfaced by crosswalk v4).** For each of T16 (family diversity), T19 (physical activity/movement), T20 (nutrition/food literacy), T22 (growth mindset/self-efficacy) — is REAL's absence a deliberate scope decision, a coverage-elsewhere-in-curriculum assumption, or an unexamined gap? All four are covered by at least one external framework; the answer shapes whether REAL needs a new LT, a documented out-of-scope rationale, or a cross-reference to non-wellbeing curriculum delivery.
- **LOW confidence tier not seen in any run.** Defined in 4c-1; hasn't fired yet.
- **Ontario LT halts on large Opus clusters.** Carry-forward from 4b-5. Pick up in 4c-7.
- **AP US Gov rubric flag rate after 4c-2b gate recalibration.** Not yet re-run.
- **RSHE KUD count (149 vs expected 30-55).** Defensible — RSHE bullets contain multiple sub-items. Not a gate failure.

---

*Last updated 2026-04-24 — REAL-10: Phase 1 crosswalk v4 shipped (commit 8acd20b). Framework-neutral matrix, summary CSV, convergence document across 21 REAL LTs × 4 external frameworks. Three gap changes (T15, T18 closed; T17 flipped to distinctive strength). 84 LT × framework pairs labelled; Gareth spot-check 5/5. Preflight 12/12 PASS. 21 LTs, 269 criteria, 267 unified-data edges. Next: Gareth to decide — programme guide, safeguarding protocol, LT 4.2 unit-plan session, or T22 gap decision.*
