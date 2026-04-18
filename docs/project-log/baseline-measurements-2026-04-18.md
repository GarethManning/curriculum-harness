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
