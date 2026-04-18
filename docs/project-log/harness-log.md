# Curriculum Harness — harness log

In-repo session log. Every substantive Claude Code session on this
project appends an entry here at session close covering: what was
built, what commits were made (hashes), what was measured, and what
the next session should pick up.

Sessions are numbered; entries are dated. Baseline measurement
snapshots live alongside this file in `docs/project-log/`.

---

## Session 2 — 2026-04-17 — Source-evidence matcher + gates a/b/c

Judge-side session. No harness code changes. Built the source-
evidence matcher primitive and wrapped it into the three foundation-
moment-1 VALIDITY gates (source coverage, no-invention,
architecture verifiability).

### Commits

- `02917c3` [docs] create project log file
- `a04aa0e` [judge] add source-evidence matcher and fixture tests
- `b8be9cb` [judge] implement VALIDITY gates a/b/c using source-
  evidence matcher
- `a9a047e` [docs] record Session 2 baseline measurements for gates
  a/b/c
- `<this commit>` [docs] Session 2 log entry

### What was built

1. `eval/source_evidence_matcher.py` — pure-Python lexical matcher.
   Lemma Jaccard + char-4gram Jaccard hybrid. No new dependencies
   (PyTorch / spaCy / sentence-transformers flagged as a decision
   point at session start; Gareth chose pure-Python for v1).
2. `eval/test_cases/{known_good,known_bad}/` + `eval/test_matcher.py`
   — fixture tests that gate trust in the matcher before it runs on
   real data. 18/18 assertions passing; threshold 0.20 cleanly
   separates 0.43–1.0 known-good from 0.03–0.08 known-bad.
3. `scripts/validity-gate/_run_loader.py` — helper that hides
   runId-prefixed vs legacy plain filenames and builds the source-
   proxy corpus from Phase 1 `curriculum_profile` + Phase 2
   `architecture`.
4. Three gate scripts, replacing their stubs:
   - `validate_source_coverage.py`
   - `validate_source_faithfulness.py`
   - `validate_architecture_diagnosis.py`
5. `VALIDITY.md` and `scripts/validity-gate/README.md` updated to
   mark assertions a/b/c as **implemented** (were pending).

### Baseline measurements

See `docs/project-log/baseline-measurements-2026-04-17.md`.

Felvételi (`outputs/palya-felveteli-2026-04-17/`):
- coverage 18.8 % (13/16 source-proxy items orphaned)
- faithfulness 9.7 % (28/31 LTs flagged as potentially invented)
- architecture verifiability 100 % (6/6 strands)

Ontario (`outputs/ontario_grade7_history/`):
- coverage 0 %, faithfulness 0 %, verifiability 100 %
- Pre-v1.2 run without `strands[]` / `values_basis` — proxy corpus
  is just 13 short element labels + structural_flaw. Baseline is
  unreliable for this run; re-running under current harness would
  help.

**Session-brief checkpoint met.** The factorial LT (index 0 of the
felvételi run, REVIEW.md §2) is correctly flagged as potentially
invented at score 0.136.

**Known precision issue** documented in the baseline file: the gate
is high-sensitivity / lower-precision in proxy mode because the
Phase 1/2 English rendering of a Hungarian source is too thin for
fine-grained faithfulness matching. Session 3+ upgrade path: harness
emits a `_source_bullets_v1.json` artefact per run.

### What Session 3 should pick up

Session 1 diagnosis identified Shape C (Phase 3 profile-conditional
branching) as the next change to address the consolidation issue.
Session 3's natural scope:

1. Implement a Phase 3 entry branch that reads
   `curriculum_profile.scoping_strategy == "full_document"` +
   `document_family == "exam_specification"` +
   `has_mark_scheme == false` + `has_command_words == false` and
   selects a per-bullet-mode prompt/tool invocation instead of the
   current strand-aggregated call.
2. Re-run the felvételi config under the new Phase 3 and compare
   against Session 2's baseline. The gate's faithfulness percentage
   should move; the factorial LT should either disappear (if the
   per-bullet mode doesn't produce it) or remain (informative failure
   mode).
3. Populate `docs/run-snapshots/` with the new run (not created this
   session; will be first populated in Session 3).

Adjacent improvements Session 3 could fold in if scope allows:
- Emit `_source_bullets_v1.json` from Phase 1 so the gates can run
  against structured bullets rather than the proxy.
- Promote gate (d) LT surface form from stub — pure-Python syntactic
  check, no matcher needed.

### Open questions / concerns

- The 0.20 threshold is fixture-calibrated, not baseline-calibrated.
  Real proxy corpora produce a narrower distribution. Once Session 3
  produces a richer source artefact, re-calibrate.
- Gate (c) architecture verifiability passes at 100 % on both
  runs but the check is really "strands are internally coherent",
  not "strands match the source". Adjacent-mechanism declaration in
  the gate's docstring is explicit about this; revisit when the
  upgrade to per-bullet source is in.

---

## Session 3a — 2026-04-18 — Rename, source-bullet artefact, 0.35 threshold, Phase 3/4 faithfulness flags

Foundation session for Sessions 3b/3c. Established the trustworthy
baseline those sessions need by moving the validity gates off the
Session-2 proxy corpus onto real source bullets and threading
source-faithfulness flagging through the harness.

### Commits

- `666f7d9` [gen] rename package to curriculum_harness
- `cc04b4a` [gen] Phase 1 emits source_bullets artefact
- `54d471d` [judge] source-bullet-aware corpus loader
- `c6fb45e` [judge] threshold 0.35 and recalibrated baseline on real source bullets
- `656b87f` [gen] Phase 3 emits source provenance and faithfulness flags
- `70c1e86` [gen] Phase 4 emits source provenance and faithfulness flags
- `3ed8ea7` [docs] Session 3a end-to-end Ontario run + flag-count baseline
- `<this commit>` [docs] Session 3a log entry

### What was built

1. **Project rename.** `kaku_decomposer/` → `curriculum_harness/`.
   Package imports, `pyproject.toml`, README, VALIDITY, harness-log
   all updated. Tests: 10 → 24 passing (14 new unit tests added in
   later commits). GitHub repo rename still pending (manual step via
   GitHub settings; Gareth's action).
2. **Phase 1 `source_bullets` artefact.** New module
   `curriculum_harness/source_bullets.py` with three rule-based
   detectors (`marker_bullet`, `numbered_outcome`, `topic_statement`).
   Validated on the felvételi source (32 Hungarian topic statements
   round-trip) and Ontario's checkpoint raw (237 bullets). Schema:
   `{source_bullets: [{id, text, source_location, bullet_type}]}`.
   Bullet IDs (`sb_001`, ...) are the provenance pointer downstream
   gates and phases attach to items.
3. **Source-bullet-aware corpus loader.** `_run_loader.py` prefers
   `<runId>_source_bullets_v1.json` when present; falls back to the
   Session-2 proxy with `corpus_mode = "proxy"` + a warning. Three
   gates surface the mode + warning in their JSON output.
4. **Threshold 0.35.** Centralised as
   `eval.source_evidence_matcher.DEFAULT_THRESHOLD`, shared by gates
   and matcher fixture tests. Fixtures still 18/18 at the new
   threshold.
5. **Source-faithfulness threading.** Shared helper
   `curriculum_harness/source_faithfulness.py` wraps the matcher
   into `compute_source_provenance` (for Phase 3 KUD items and Phase
   4 LTs) and `compute_parent_provenance` (for Phase 4 → KUD
   traceability). `KUDItem` gains `source_provenance` + `flags`;
   `LearningTarget` gains `source_provenance` + `kud_provenance` +
   the existing `flags`. Items below threshold ship with
   `SOURCE_FAITHFULNESS_FAIL` — Session 3b adds the regeneration
   loop.
6. **Adjacent-mechanism declarations.** Every new module
   (`source_bullets`, `source_faithfulness`) carries an explicit
   "what this does NOT check" section in its module docstring.

### Baseline measurements

See `docs/project-log/baseline-measurements-2026-04-18.md` (this
session) and `baseline-measurements-2026-04-17.md` (Session 2,
preserved for comparison).

Felvételi (bullets mode, threshold 0.35):
- coverage 0.0 % (32/32 orphaned)
- faithfulness 0.0 % (31/31 flagged) — factorial LT at 0.0073 ✓
- architecture verifiability 0.0 % (6/6 unverifiable)

Ontario (bullets mode, threshold 0.35, against the 2026-04-17
checkpoint-backfilled bullets):
- coverage 1.3 % (234/237 orphaned)
- faithfulness 13.6 % (19/22 flagged)
- architecture verifiability 15.4 % (11/13 unverifiable)

Ontario Session 3a full-pipeline re-run (flag counts from the
live-threading path):
- 5 source bullets, 14 KUD items, 14 LTs
- 14/14 KUD items flagged SOURCE_FAITHFULNESS_FAIL
- 14/14 LTs flagged SOURCE_FAITHFULNESS_FAIL
- Snapshot: `docs/run-snapshots/2026-04-18-ontario-session-3a/`

### Hard-requirement checkpoint

Factorial LT (felvételi LT index 0) must remain flagged as
potentially invented. **Confirmed** at score 0.0073 against
`sb_002`; well below the 0.35 threshold.

### Key finding — Session 2's proxy numbers were misleading

Felvételi went from Session 2's 18.8 % / 9.7 % to this session's
0 % / 0 %. The move is not a regression. The Session 2 proxy corpus
was Phase 1/2's *English rendering* of the Hungarian source — the
matcher was comparing English LTs against an English proxy and
measuring pipeline-internal consistency, not source fidelity. The
bullet-mode result is honest: the matcher is English-only, and the
raw felvételi bullets are Hungarian. Baseline doc explains this in
detail.

### What Session 3a did NOT do

- **Step 2 — in-repo vision summary (`docs/vision/binding-specifications.md`).**
  Deferred. Gareth will paste v4.1 sections in a follow-up session so
  the summary can be written without invention.
- **Felvételi end-to-end re-run.** Deferred to the
  multilingual-matcher session. Running it today produces the same
  0/0/0 blocked by the English-only matcher and adds no signal.
- **Phase 3 consolidation-bias fix.** Session 3b scope. Today's
  flagging gives 3b a measuring stick (today's 0 / 14 floor), but
  does not address the root cause.
- **Regeneration loop on SOURCE_FAITHFULNESS_FAIL.** Session 3b.
  Today flagged items ship with the flag.
- **Classifier confidence / grain consistency / self-consistency
  (Session 3c).**

### Pending manual actions for Gareth

1. **Rename the GitHub repo** from `curriculum-decomposer` to
   something matching `curriculum_harness` (e.g.
   `curriculum-harness` with the hyphen) via GitHub Settings. Git
   remotes will update via GitHub's redirect; local `.git/config`
   may need `git remote set-url origin` after the rename lands.
2. **Paste v4.1 vision-doc sections** into the Session-3a.5 / 3b
   prompt so `docs/vision/binding-specifications.md` can be
   written. Pulling specifications from project-knowledge into the
   repo is a standing requirement (VALIDITY.md pattern).

### What Session 3b should pick up

1. Implement the Phase-3 profile-conditional branch (Shape C — see
   Session 1 diagnosis Q2). Signal already on state
   (`curriculum_profile.scoping_strategy == "full_document"`,
   `document_family == "exam_specification"`, assessment signals) —
   Phase 3 just needs to read them.
2. Add the regeneration-on-SOURCE_FAITHFULNESS_FAIL loop in Phase 4.
   The flag is already attached; 3b adds the retry and re-validate
   plumbing.
3. Surface the bullet-corpus weakness from this session: Ontario's
   6 285-char scoped extract missed the Specific Expectations
   entirely. A deterministic bullet-preservation step at Phase 1
   (or a broader `scoping_strategy = "full_document"` default for
   national frameworks) would stabilise the baseline across runs.

### Open questions for 3b/3c

- **Translation step for non-English sources.** Until either (a) the
  matcher becomes multilingual or (b) Phase 1 translates bullets at
  extraction time, felvételi's bullet-mode baseline is 0/0/0 by
  construction. Decide which of (a) or (b) first in Session 3b
  planning — (b) is smaller scope but lossier; (a) is bigger but
  more faithful.
- **Bullet-type weighting.** `marker_bullet` sample questions are
  not the same primary-source object as `numbered_outcome` specific
  expectations. The gate currently treats them uniformly; a weighted
  coverage number would be more interpretable. Not load-bearing for
  Session 3b but worth tracking.

---

## Session 3b — 2026-04-18 — Binding-specifications, Phase 1 stability, Phase 3 Shape C branch

Three substantive deliverables: the Session 3a carry-over
(binding-specifications.md), a Phase 1 scope-extraction stabilisation
(Shape A + Shape B), and the Phase 3 profile-conditional branch
(Shape C fix from Session 1's diagnosis). Phase 4 regeneration loop
originally scoped here slipped to Session 3c per the brief.

### Commits

- `268a106` [docs] Session 3a carry-over: binding-specifications from vision v4.1
- `305f4e5` [docs] Phase 1 scoping nondeterminism diagnosis
- `43f4f4a` [gen] Phase 1 scope extraction stabilised (Shape A + Shape B)
- `c3ee13b` [judge] rebaseline on stabilised Phase 1 output
- `2e7c5da` [gen] Phase 3 profile-conditional branch (Shape C fix)
- `d969a71` [docs] Session 3b end-to-end runs — Ontario + felvételi with Phase 3 fix
- `<this commit>` [docs] Session 3b log entry

### What was built

1. **`docs/vision/binding-specifications.md`** — the in-repo subset of
   vision v4.1 that binds code. Written verbatim from Gareth's paste.
   Covers two-tool architecture, input modes, numeric thresholds,
   schema versioning, human-review workflow, provenance, and deferred
   specifications. Session 3a's missing Step 1.

2. **Phase 1 scope-extraction diagnosis
   (`docs/diagnostics/2026-04-18-phase1-scoping-diagnosis.md`).**
   Identified three compounding sources of the observed 47× variance
   on Ontario bullets (237 → 5 between runs): (a) `haiku_stream_text`
   omitted `temperature`, defaulting to API 1.0; (b) the Haiku
   classifier at temp 1.0 could flip `document_family` and change the
   scope prompt between runs; (c) `_scoped_content_ok` accepted thin
   Haiku output as equivalent to rich output when a single cue word
   was present.

3. **Phase 1 stabilisation (Shape A + Shape B).**
   `curriculum_harness/_anthropic.py:haiku_stream_text` gains
   `temperature: float = 0.0` and passes it to the streaming call.
   `phase1_ingestion.py` now feeds `extract_source_bullets` from the
   deterministic `_scope_fallback_slice(...)` rather than the
   Haiku-scoped `raw_curriculum`; `raw_curriculum` still receives the
   Haiku narrowing for downstream LLM phases. Shape A alone was
   insufficient (Anthropic streaming at temp=0 is not bit-deterministic
   — runA vs runB still differed 37.5 % / 47.6 %). Shape B pins
   bullets: runA/runB variance **0.0 % on count, 0.0 % on bullet-text
   chars** (`docs/run-snapshots/2026-04-18-session-3b-phase1-stability/variance_report.md`).

4. **Validity-gate rebaseline on stable Phase 1.** Three-way comparison
   added to `docs/project-log/baseline-measurements-2026-04-18.md`.
   Ontario verifiability: **15.4 % → 44.4 %** (major move). Ontario
   faithfulness (Session-3a LTs vs stable corpus): **0.0 % → 7.1 %**.
   Ontario coverage dropped numerically (1.3 % → 0.1 %) because the
   denominator grew 4× and only 14 LTs exist to cover 937 bullets;
   coverage is not the right headline metric for bare-pre-
   consolidation Ontario and is a follow-up (bullet-type weighting).

5. **Phase 3 profile-conditional branch (Shape C fix).**
   `phase3_kud.py` reads `curriculum_profile` from state and routes to
   one of three branches at Phase 3 entry: `per_bullet` (bare-bullet
   exam spec), `strand_aggregated` (designed sources), `default`
   (uncertain — runs strand_aggregated and logs the defaulting).
   `KUDItem` gains `source_bullet_ids`; merges surface in the run
   report. Adjacent-mechanism declaration in the module docstring.
   Fallback (`_direct_sonnet_kud_per_bullet`) wires through for the
   per_bullet branch when MCP fails.

6. **End-to-end runs on Ontario + felvételi with both fixes active**
   (`docs/run-snapshots/2026-04-18-session-3b-post-phase3-fix/`).

### What was measured — Session 3b end-to-end

- **Ontario (strand_aggregated branch, as expected):** 937 source
  bullets (was 5 in Session 3a), 17 KUD items, 17 LTs.
  Phase 3 KUD faithfulness-flagged: 13/17 (76.5 % flagged, 4/17 clear
  threshold vs Session 3a's 0/14). Phase 4 LT flagged: 15/17 (88.2 %,
  2/17 clear threshold). No merge events recorded (not applicable to
  strand_aggregated).
- **Felvételi (per_bullet branch fires — as designed):** 32 source
  bullets, **32 KUD items**, **0 merge events**. Bullet-to-KUD
  consolidation ratio moves from Session 2's ~2.3 : 1 to **1 : 1**. LT
  count follows: **32 LTs** (was 31 in Session 2). Factorial LT still
  flagged SOURCE_FAITHFULNESS_FAIL (32/32 flagged by construction —
  English-only matcher on Hungarian source).
- Phase 3 MCP returned Connection error on both runs; Sonnet-direct
  fallback ran, and the correct fallback (per_bullet vs
  strand_aggregated) fired for each config.

### What this does NOT do

- **No Phase 4 regeneration loop** (Session 3c). Flagged items still
  ship with the flag.
- **No exam-spec output-shape discipline** (also Session 3c). Felvételi
  still populates 4 Understands; v4.1's rule to refuse Understands /
  Dispositions in exam-spec mode is not yet enforced.
- **No multilingual matcher.** Felvételi's 100 % faithfulness flag
  rate remains an English-only-matcher artefact.

### Temptation log (per brief)

The brief instructed not to add the Phase 4 regeneration loop even if
output regression tempted. The temptation did arise — Ontario
faithfulness drops from 76.5 % flagged in Session 3a (0 cleared) to
88.2 % in Session 3b's post-fix run (2/17 cleared). Phase 3 is emitting
more Understands and Dispositions with less verbatim source alignment,
so surface-form LT flags rise. Logged here and left alone — Session 3c.

### What Session 3c should pick up

1. **Phase 4 regeneration loop on SOURCE_FAITHFULNESS_FAIL.** The flag
   is live; 3c adds the retry-and-re-validate plumbing.
2. **v4.1 exam-spec output-shape discipline.** In per_bullet mode,
   refuse to emit Understands and Dispositions; relabel output as
   "Assessed Demonstrations Map" per binding-specifications.md.
3. **Multilingual matcher (or translation step).** Either upgrade
   `eval/source_evidence_matcher` with cross-language support, or add
   a Phase 1 translation pass so felvételi's bullets become matchable.
4. **Bullet-type weighting on coverage.** 937 bullets includes many
   sample questions and cross-grade content that no reasonable LT set
   would cover; the coverage metric needs either a weighted denominator
   or a "meaningful subset" filter.

### Open questions for 3c

- **Ontario's 937-bullet corpus is over-wide.** The deterministic slice
  from `_scope_fallback_slice` grabbed a large window around the
  Grade 7 History anchor. That's faithful in the sense that
  extraction is deterministic, but it picks up adjacent grades'
  bullets as well. Tightening the window (explicit section boundaries
  in `_window_history_grade7`) would sharpen coverage; it is not
  load-bearing for the Session 3c work but will make measurements
  easier to read.
- **Phase 3 MCP reliability.** Two of two e2e runs in this session hit
  `Connection error` on the MCP endpoint. Fallback fires and the runs
  complete, but the intermittent failure clouds comparisons against
  prior runs. Worth tracking whether this is a MCP-server issue or a
  local network effect.

---

<!-- next session entry goes here -->

