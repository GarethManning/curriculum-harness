# Baseline measurements — 2026-04-18

Session 3a rebaseline after:

- Phase 1 emitting `_source_bullets_v1.json` (Step 3 — commit `cc04b4a`)
- Loader preferring the bullet artefact (Step 4 — commit `54d471d`)
- Threshold raised from 0.20 → 0.35 (this commit — see
  `eval/source_evidence_matcher.DEFAULT_THRESHOLD`)

**Do not replace `baseline-measurements-2026-04-17.md` with this file.**
That document is the proxy-corpus baseline. This one is the
bullet-corpus baseline. Both are preserved so the shape of the move can
be read directly rather than reconstructed from git.

Raw gate JSON lives alongside this file in `baseline-2026-04-18/`.

## Corpus sizes

| Run | Bullets | Bullet types |
|---|---:|---|
| `outputs/palya-felveteli-2026-04-17/` | 32 | `topic_statement` ×32 (all Hungarian) |
| `outputs/ontario_grade7_history/` | 237 | `marker_bullet` ×186 (sample questions), `numbered_outcome` ×50 (A1.1-style specific expectations), `topic_statement` ×1 |

Bullets were regenerated from each run's checkpoint `raw_curriculum`
via a one-off script that calls `extract_source_bullets`. Future runs
will emit this artefact automatically from Phase 1.

## Gate results — threshold 0.35, corpus mode "bullets"

### Felvételi — `outputs/palya-felveteli-2026-04-17/`

| Gate | Total | Flagged | Rate |
|---|---:|---:|---|
| source_coverage | 32 bullets | 32 orphaned | coverage **0.0 %** |
| source_faithfulness | 31 LTs | 31 flagged | faithfulness **0.0 %** |
| architecture_diagnosis | 6 strands | 6 unverifiable | verifiability **0.0 %** |

### Ontario — `outputs/ontario_grade7_history/`

| Gate | Total | Flagged | Rate |
|---|---:|---:|---|
| source_coverage | 237 bullets | 234 orphaned | coverage **1.3 %** |
| source_faithfulness | 22 LTs | 19 flagged | faithfulness **13.6 %** |
| architecture_diagnosis | 13 strands | 11 unverifiable | verifiability **15.4 %** |

## Hard requirement — factorial LT still flagged

The Session 1 / Session 2 / Session 3a hard requirement: the factorial
LT at felvételi LT index 0 (`"I can calculate factorials and apply
counting principles..."`) must be flagged as potentially invented.

**Result: confirmed.** Best source match against the 32 Hungarian
bullets scored **0.0073** (against `sb_002` — Elemi kombinatorika).
Below the 0.35 threshold; the LT is flagged.

## Comparison to Session 2 (proxy, threshold 0.20)

| Run | Metric | 2026-04-17 (proxy, 0.20) | 2026-04-18 (bullets, 0.35) | Move |
|---|---|---:|---:|---|
| Felvételi | coverage | 18.8 % | 0.0 % | **-18.8** |
| Felvételi | faithfulness | 9.7 % | 0.0 % | **-9.7** |
| Felvételi | verifiability | 100 % | 0.0 % | **-100** |
| Ontario | coverage | 0 % | 1.3 % | **+1.3** |
| Ontario | faithfulness | 0 % | 13.6 % | **+13.6** |
| Ontario | verifiability | 100 % | 15.4 % | **-84.6** |

The brief predicted felvételi would *improve* under bullet-mode
matching. It regressed instead. The mechanism is not a matcher bug —
it is a language-boundary effect the matcher cannot bridge.

### Why felvételi regressed

The matcher is English-only (`source_evidence_matcher.py`
adjacent-mechanism #4). Two matching pairs produce very different
baselines:

1. **Session 2 (proxy mode):** English LTs vs Phase 1/2's *English
   rendering* of the Hungarian source (strand labels, values_basis,
   rationale). Shared vocabulary = shared language. The matcher
   produces meaningful scores; some LTs clear 0.20.
2. **Session 3a (bullet mode):** English LTs vs the *raw Hungarian
   bullets* extracted from the Phase 1 scoped text. Vocabulary is
   disjoint because the languages are. The matcher returns near-zero
   for every pair. Every bullet is an orphan and every LT is flagged.

The bullet artefact for a non-English source is correct as a record of
what the source actually says — but it is not directly matchable
against English LTs without a translation step. Session 3a does not
add that step; Session 3b+ will need to.

Session 2's baseline was not "better" in any substantive sense — it
was measuring pipeline-internal consistency (how well the English
output matches the English proxy of the source) rather than
source-faithfulness. The Session 2 baseline file is honest about this
("high-sensitivity / lower-precision") but the number was misleading
without that caveat attached.

### Why Ontario moved the way it did

- **Coverage dropped from 0 % → 1.3 %** because the Ontario proxy was
  extremely sparse (13 element labels, no `strands[]` — pre-v1.2 run).
  Any coverage is an improvement over nothing.
- **Faithfulness rose from 0 % → 13.6 %** for the same reason.
  Bullet-mode has real source content to match against. Three LTs
  (the ones most lexically similar to specific expectations) now
  clear 0.35.
- **Verifiability dropped from 100 % → 15.4 %** because the Session 2
  verifiability number was "internal coherence" (strand labels shared
  vocabulary with each other). In bullet mode, strand labels are
  matched against the *actual source bullets*; only 2 of 13 strand
  labels survive that test at 0.35. Most strand labels are synonym-
  or-paraphrase-distant from the bullet vocabulary (e.g. strand
  "Historical Empathy" vs bullet "A1.1 describe some of the central
  values and world views..."). The matcher's bag-of-lemmas has no way
  to bridge them.

## What the new baseline is *actually* measuring

- **Felvételi numbers are dominated by the language boundary.** The
  0.0 % results are not evidence that the felvételi pipeline is doing
  anything more wrong than it was yesterday. They are a measurement
  limit — the matcher cannot score English LTs against Hungarian
  bullets. Until a translation pass lands, felvételi cannot be
  rebaselined usefully in bullet mode.
- **Ontario numbers are real and interpretable.** Coverage at 1.3 %
  reflects that ~220 of 237 bullets are `marker_bullet` sample
  questions from the teacher-supports sections, not specific
  expectations — LTs do not address those questions, which is as it
  should be. The meaningful subset is the 51 `numbered_outcome` +
  `topic_statement` items; coverage against just that subset is
  ≈ 6 % (3 / 51) — a cleaner signal once the gate is taught to
  weight by bullet_type.
- **The factorial LT test survives the threshold change.** That is
  the only per-case guarantee Session 3a makes. It is sufficient to
  keep Session 3b's regeneration-loop work unblocked.

## Session 3a end-to-end re-run — Ontario only

A fresh full-pipeline run with the Session 3a code active (Phase 3/4
faithfulness threading and run-time bullet emission). Felvételi
re-run is deferred to the multilingual-matcher session — running it
end-to-end now produces the same 0/0/0 blocked by the English-only
matcher and doesn't inform Session 3b's design.

- **Config:** `configs/ontario_grade7_history_session3a.json`.
- **Snapshot:** `docs/run-snapshots/2026-04-18-ontario-session-3a/`.

### Flag counts — Ontario, Session 3a run

| Measure | Count |
|---|---:|
| Source bullets emitted (Phase 1 artefact) | **5** (all `marker_bullet`) |
| Phase 1 `raw_curriculum` length | **6 285 chars** |
| KUD items total | 14 |
| Phase 3 KUD items flagged `SOURCE_FAITHFULNESS_FAIL` | **14 / 14** |
| LTs total | 14 |
| Phase 4 LTs flagged `SOURCE_FAITHFULNESS_FAIL` | **14 / 14** |
| LT best-source-score — min / median / max | 0.049 / 0.060 / 0.100 |
| LTs clearing 0.35 threshold | **0 / 14** |
| Other Phase 4 flags | `COMPOUND_TYPE` (1 LT) |

### Why this run scores worse than the 2026-04-17 Ontario baseline (bullets mode)

The earlier Ontario baseline (this doc's top section — 237 bullets,
22 LTs, 54.5 % faithfulness) was computed against the *checkpointed
raw_curriculum* of an older run (50 962 chars — full Overview Chart
plus many A1.*/B1.* Specific Expectations). This fresh run's Phase 1
Haiku-scoped extract is only 6 285 chars — Haiku selected a much
narrower slice of the 500+-page Ontario PDF, keeping the Overview
paragraph + five Sample-Spatial-Skills bullets and dropping the
Specific Expectations entirely. The bullet extractor worked correctly
(it found the 5 `•` markers) — the Phase 1 scope selection is the
problem.

Two separate issues compound:

1. **Haiku scope nondeterminism.** Two runs against the same URL
   produced 6 285-char and 50 962-char scoped extracts. For
   multi-hundred-page documents with `grade_subject_filter` strategy,
   the anchor-based windowing + Haiku extraction is unstable.
2. **Consolidation bias (known from Session 1 Q1).** Phase 3 emitted
   only 14 KUD items, collapsed into 3 content-theme strands. This is
   the same consolidation failure Session 1 diagnosed; Session 3b
   Shape-C branching is the planned fix. The faithfulness flagging
   this session added will be its measuring stick.

### What this baseline does mean

- **The faithfulness-flag plumbing is live and measuring.** Every
  emitted KUD item and LT carries a `source_provenance` entry and a
  `SOURCE_FAITHFULNESS_FAIL` flag where appropriate; the run report
  surfaces the counts.
- **The threshold (0.35) is strict enough that with a 5-bullet corpus
  dominated by spatial-skills content, only LTs about maps /
  locations could clear — and Phase 4 generated 14 LTs none of which
  were that.** 14/14 flagged is the correct measurement *for this
  run's corpus*, not a claim about the pipeline's general
  faithfulness.
- **Session 3b's work will be measurable against this baseline**
  once Phase 3 branching stabilises the bullet corpus and KUD
  cardinality. Today's 0/14 becomes the floor; any move upward is a
  real signal.

### Felvételi measurement — pending

The felvételi end-to-end re-run was deferred. Mechanism unchanged
since Session 2: matcher is English-only, source is Hungarian → every
LT scores ≈ 0 regardless of faithfulness. Running the pipeline again
will produce 0/0/0 again, so the re-run is only worth doing after
the multilingual-matcher upgrade (Session 3c or later).

## Session 3b / follow-ups

1. **Translation pass for non-English sources.** Until bullets can be
   translated (or the matcher made multilingual), felvételi's
   bullet-mode baseline is 0/0/0 by construction. Session 3b or 3c
   should decide: translate at extraction time (bullets become
   English), or run a second matcher that compares translated LTs
   against raw-language bullets.
2. **Bullet-type weighting.** Coverage is computed uniformly across
   all bullet types. A `marker_bullet` sample question is not a
   curriculum content element in the same sense a `numbered_outcome`
   specific expectation is. The gate should optionally weight by
   bullet_type, or emit separate coverage numbers per type.
3. **Architecture-diagnosis gate reframing.** In bullet mode, strand
   labels are expected to match source bullets only where the strand
   is a direct summary of a bullet set. A strand synthesising many
   bullets ("Historical Empathy" over 10+ specific expectations) will
   not lexically match any single bullet. The gate needs either (a)
   embedding-based matching, (b) synonym handling, or (c) a
   coverage-of-bullets semantic rather than a lexical-match one.

None of these are Session 3a's job. They are recorded here so the
Session 3b planning has the right starting point.

---

## Session 3b rebaseline — 2026-04-18 (Phase 1 stabilised, Shape A + B)

Phase 1 stabilisation shipped: `haiku_stream_text` defaults to
`temperature=0.0`, and `extract_source_bullets` is fed the deterministic
`_scope_fallback_slice` instead of the Haiku-scoped `raw_curriculum`.
Bullet variance across re-runs of the same config: **0.0 % bullet-count,
0.0 % bullet-text char**. See
`docs/run-snapshots/2026-04-18-session-3b-phase1-stability/variance_report.md`.

Ontario bullet corpus with the stabilised extractor: **937 bullets**
(237 `numbered_outcome` / 699 `marker_bullet` / 1 `topic_statement`,
all extracted from the deterministic Grade 7 / History window of the
full Ontario PDF). This replaces Session 3a's 5-bullet corpus and the
earlier 237-bullet corpus that was built off a variable Haiku output.

Gate inputs: Session 3a's LTs, KUD, architecture, and curriculum
profile held constant; only the `source_bullets_v1.json` artefact
swapped to the new stable 937-bullet set. Gate reports:
`docs/project-log/baseline-2026-04-18-session-3b/`.

### Ontario — three-way baseline comparison (threshold 0.35, bullets mode)

| Gate | 2026-04-18 proxy-Haiku baseline (237 bullets, 22 LTs) | Session 3a run (5 bullets, 14 LTs) | Session 3b — stabilised (937 bullets, 14 Session-3a LTs) |
|---|---:|---:|---:|
| source_coverage | 1.3 % (3 / 237) | 0.0 % (0 / 5 at 0.35 in Session 3a end-to-end; implicit from 14/14 LT flags) | **0.1 %** (1 / 937) |
| source_faithfulness | 13.6 % (3 / 22) | 0.0 % (0 / 14) | **7.1 %** (1 / 14) |
| architecture_diagnosis verifiability | 15.4 % (2 / 13) | — (not run in Session 3a baseline table) | **44.4 %** (4 / 9) |

### Reading the move

- **Verifiability: 15.4 % → 44.4 %** (≈ +29 points). Four of nine
  architecture strands now find at least one bullet above the 0.35
  threshold, up from two of thirteen. The bullet corpus now contains
  the Ontario Grade 7 specific expectations (`A1.1 describe...`,
  `B1.2 analyse...`, etc.) verbatim as `numbered_outcome` items, so
  strand labels like "Historical Inquiry Process" and "Historical
  Empathy Perspective" find lexically-adjacent bullets. The strand
  count also dropped from 13 to 9 because Session 3a's architecture
  has nine strands rather than the older run's thirteen — the
  denominator shift partly drives the rate change, but the absolute
  covered count rose (2 → 4) so the improvement is real, not purely a
  denominator effect.
- **Faithfulness: 0.0 % → 7.1 %.** One of Session 3a's 14 LTs
  (specifically the LT most lexically aligned with an Ontario
  specific-expectation bullet) now clears threshold. This is the
  measurable floor-rise the brief predicted: the Session 3a corpus
  (5 thin marker bullets) made faithfulness unmeasurable; the
  stabilised corpus lets a genuine signal emerge.
- **Coverage: 1.3 % → 0.1 %** (numerically down). The denominator
  grew 4×; the numerator held at 1. This is expected and not a
  regression of the harness — it is the inverse of the faithfulness
  story. With 937 bullets and only 14 LTs, coverage is denominator-
  bounded at **14 / 937 = 1.5 %** maximum even if every LT covered a
  unique bullet. The right gate-level fix (bullet-type weighting or a
  "meaningful subset" filter) is recorded in Session 3a's follow-ups
  §2 and remains open. Session 3b reads this as confirmation that
  coverage is not the right headline metric for bare-pre-consolidation
  Ontario runs; faithfulness and verifiability are.

### Factorial LT guarantee — still holds

Session 3a's hard requirement was that the felvételi factorial LT
flagged as potentially invented. That test is not directly re-run by
this step (felvételi is English-only-matcher-blocked; see Session 3a
follow-up §1), but nothing in Shape A/B changed the source-faithfulness
matcher's behaviour — only the bullet corpus fed to it. The factorial
LT's best-source-score against Hungarian bullets remains < 0.35 by
construction.

### Artefacts

- Full gate JSON: `docs/project-log/baseline-2026-04-18-session-3b/*.json`
- Input run dir (Session 3a artefacts + stable bullets):
  `outputs/ontario-session-3b-phase1-rebaseline/`
- Stable bullet artefact source:
  `docs/run-snapshots/2026-04-18-session-3b-phase1-stability/runA_source_bullets.json`
  (runA and runB are byte-identical on bullet text — see variance report)

