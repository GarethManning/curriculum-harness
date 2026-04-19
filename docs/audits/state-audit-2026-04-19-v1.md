# State audit — 2026-04-19 v1

Read-only verification of claims in
`docs/plans/curriculum-harness-remaining-build-plan-v2.md` (the plan
file was found at the primary path; the alternate `/mnt/project/...`
path does not exist on this machine). No repo state modified; no
harness runs executed.

---

## Section 1 — VERIFIED

### Phase 0 acquisition layer

**Commit b2f872c exists.** `git log` resolves it to
`b2f872c [docs] Session 4a-5 log and state snapshot`.

**`git log --oneline -20` top** (most recent first):

```
58670ea [docs] Session 4b-4 log and state snapshot
ef677a8 [gen] CSV exporter, review renderer, cross-source summary ...
80b65a0 [gen] Regenerate Common Core + Welsh CfW criterion artefacts
542db1a [fix] Sync gate OBSERVABLE_VERBS with generator _VERB_BUCKETS
c0de07e [gen] Regenerate Common Core 7.RP criterion artefacts
47fe000 [fix] Sync _dominant_verb_bucket to use _lemmatise
7fefbc4 [gen] Common Core 7.RP criterion artefacts + prompt tightening
48bd304 [fix] Relax rubric self-consistency signature
cfa27c7 [pipe] Wire criterion + supporting components into pipeline
c4d6882 [gen] Criterion quality gates (4b-4 step 3)
ba993c5 [gen] Supporting-components generator (4b-4 step 2)
f44ad91 [gen] Type 1/2 criterion generator (4b-4 step 1)
89159e1 [docs] Session 4b-3 log and state snapshot
fe96038 [docs] Session 4b-3: CSVs, review renders, cross-source summary
698fcd0 [gen] Reference output for Ontario Grade 7 History
cee3aae [fix] Clustering validator: recover duplicates and ≤3 missing
dbcb857 [fix] Clustering: increase max_tokens to 8192
b4f8a6a [gen] Reference output for Common Core Grade 7 Ratios
fc22c08 [gen] Regenerate Welsh CfW metadata surfaces
dfa2df3 [gen] CSV exporter and review renderer surface per-band metadata
```

**Five source-type primitives present as code.**
`curriculum_harness/phases/phase0_acquisition/sequences.py` defines
all five sequences:

- `static_html_linear_sequence` (line 63)
- `flat_pdf_linear_sequence` (line 101)
- `multi_section_pdf_sequence` (line 133)
- `js_rendered_progressive_disclosure_sequence` (line 175)
- `html_nested_dom_sequence` (line 219)

`type_detector.py:43` lists the same five in `SUPPORTED_SOURCE_TYPES`.

**Manifest schema 0.6.0 is in the schema file.**
`curriculum_harness/phases/phase0_acquisition/manifest.py:280`:
`phase0_version: str = "0.6.0"`. Module docstring at line 21 notes
"Schema 0.6.0 (Session 4a-4.5) — adds raw-content caching fields".
Spot-check against a real manifest
(`docs/run-snapshots/2026-04-19-session-4a-5-.../manifest.json`)
returns `phase0_version: 0.6.0`.

### Nine artefacts ingested across three domain types

`docs/run-snapshots/` holds nine Phase 0 ingestion artefacts produced
by Session 4a-4.5 (eight regenerations under schema 0.6.0) plus
Session 4a-5 (one net-new dispositional-domain source):

```
2026-04-18-session-4a-4-5-ap-usgov-ced-unit1          (horizontal)
2026-04-18-session-4a-4-5-common-core-7rp             (hierarchical)
2026-04-18-session-4a-4-5-dfe-ks3-maths-pdf           (hierarchical)
2026-04-18-session-4a-4-5-gov-uk-nc-maths-ks3         (hierarchical)
2026-04-18-session-4a-4-5-nz-curriculum-social-sciences (horizontal)
2026-04-18-session-4a-4-5-ontario-dcp-g7-history      (horizontal)
2026-04-18-session-4a-4-5-ontario-k8-g7-history-pdf   (horizontal)
2026-04-18-session-4a-4-5-wales-cfw-maths-sow         (hierarchical)
2026-04-19-session-4a-5-wales-cfw-health-wellbeing-sow (dispositional)
```

Nine total; three domain types covered. Cross-confirmed by the domain
coverage table at
`curriculum_harness/phases/phase0_acquisition/README.md:47-56` and by
`phase0-4a4-5-regeneration-summary.json` in `docs/project-log/`.

### Welsh CfW Health & Wellbeing reference

Output lives at `docs/reference-corpus/welsh-cfw-health-wellbeing/`.
Counts verified from the JSON files:

- `kud.json` — 33 items ✓
- `competency_clusters.json` — 9 clusters ✓
- `lts.json` — 20 LTs ✓
- `band_statements.json` — 11 sets, 3 halted ✓ (plan says "11 sets")
- `observation_indicators.json` — 5 sets, 1 halted ✓
- `criteria.json` — 12 rubrics ✓
- `criteria_quality_report.json` summary:
  `rubrics_total: 12, rubrics_with_gate_failures: 1` → 11 gate-pass ✓
- `supporting_components.json` — 9 components ✓
- `progression_structure.json`, `quality_report.json/.md`,
  `reference-review.md` all present ✓
- `_generated-in-error-a-d-version/` subdirectory preserved with 10
  files ✓

### Common Core 7.RP reference

Output at `docs/reference-corpus/common-core-g7-rp/`:

- `kud.json` — 22 items ✓
- `competency_clusters.json` — 4 clusters ✓
- `lts.json` — 8 LTs ✓
- `band_statements.json` — 6 sets, 2 halted ✓
- `observation_indicators.json` — 0 sets (no Type 3 content, as plan
  notes) ✓
- `criteria.json` — 7 rubrics ✓
- `criteria_quality_report.json` summary:
  `rubrics_total: 7, rubrics_with_gate_failures: 1` → 6 gate-pass ✓
- `supporting_components.json` — 4 components ✓

### Ontario Grade 7 History (partial)

Output at `docs/reference-corpus/ontario-g7-history/`:

- `kud.json` — 188 items ✓
- `competency_clusters.json` — 11 clusters, overall
  `cluster_unstable` ✓
- `lts.json` — 23 LTs ✓
- `band_statements.json` — 21 sets ✓
- `observation_indicators.json` — 2 sets ✓
- `quality_report.md` "FOCUS ON placement-rule verification":
  `0 agree / 1 disagree / 6 unstable` ✓ — matches plan verbatim

**Confirmed missing (consistent with plan):**

- `criteria.json` — not present
- `criteria_quality_report.json/.md` — not present
- `supporting_components.json` — not present
- Criterion CSV export — not present (only kud, learning-targets,
  observation-indicators CSVs exist; three CSVs total, matching plan)

### 4b arc diagnostic infrastructure

What exists in the repo under the "diagnostic infrastructure" banner
(as defined by the plan — reference output produced by the authoring
pipeline against which harness output will later be compared):

- Reference-authoring pipeline code:
  `curriculum_harness/reference_authoring/` — inventory, KUD
  classifier, KUD gates, competency clustering, LT generator, band
  statements, observation indicators, Type 1/2 criterion generator,
  criterion gates, supporting-components generator, progression
  detection with jurisdiction lookup, and a `pipeline/run_pipeline.py`
  orchestration entry point.
- Scripts: `scripts/reference_authoring/` — CSV exporter
  (`export_reference_to_csv.py`), review renderer
  (`render_reference_for_review.py`), KUD-only review renderer, and a
  standalone criterion runner (`run_criteria.py`).
- Three reference corpora under `docs/reference-corpus/` (Welsh CfW,
  Common Core 7.RP, Ontario G7 History partial).
- Cross-source summary at `docs/reference-corpus/_cross-source-summary.md`
  (header: "Generated: 2026-04-19 — session 4b-4").
- Session log and state-snapshot entries in
  `docs/project-log/harness-log.md` through Session 4b-4.
- Gate-revision history at
  `docs/plans/session-4b-gate-revisions-v1.md`.

---

## Section 2 — CONTESTED OR UNCLEAR

### Build plan not yet committed to the repo

Plan line 31-35 says "First action for next session — commit this
build plan to the repo" at
`docs/plans/curriculum-harness-remaining-build-plan-v1.md`. Current
state: the file lives at
`docs/plans/curriculum-harness-remaining-build-plan-v2.md` and is
**untracked** (confirmed by `git status`). The v1 filename the plan
asks for is not present. This is a pending first-action-of-next-session
item, not a contradiction, but worth flagging.

### `session-4b-arc-plan-v3.md` not yet revised

Plan asks for `session-4b-arc-plan-v3.md` to be updated to drop
Hungarian felvételi and re-order remaining sessions. The file still
lists felvételi at line ~22 ("One exam-spec companion: Hungarian
felvételi"). Same "pending first-action" status.

### CSV export counts disagree with plan claims

The plan states Welsh CfW has "three CSV exports" and Common Core has
"four CSV exports". Actual counts:

- Welsh CfW: **5 CSVs** — criteria, kud, learning-targets,
  observation-indicators, supporting-components.
- Common Core: **5 CSVs** — same filenames.
- Ontario: **3 CSVs** — kud, learning-targets, observation-indicators
  (matches plan).

The Common Core observation-indicators CSV is metadata-only (8 lines,
zero indicator rows — CC has no Type 3 content). If the plan was
counting non-empty CSVs, Common Core would have 4 and Welsh would have
5 — still doesn't match ("three" for Welsh). Numbers appear stale.

### VALIDITY.md scaffolded-but-not-populated claim

Plan line 82 lists as a future-work item: "VALIDITY.md populated with
construct-validity assertions (currently scaffolded but not
populated)". Repo state contradicts: `VALIDITY.md` carries recent
updates ("foundation-moment-2 gates promoted from pending to
implemented"), and `scripts/validity-gate/` contains seven validator
scripts (`validate_source_coverage.py`,
`validate_source_faithfulness.py`, `validate_architecture_diagnosis.py`,
`validate_exam_block_scope.py`, `validate_lt_surface_form.py`,
`validate_regenerate_loop.py`, `validate_lt_criterion_coverage.py`,
`validate_prerequisite_dag.py`) plus a `run_all.py` driver. Either
"scaffolded but not populated" means something narrower than it
reads, or the item is stale relative to the Session-3c VALIDITY
update.

### Comparison pipeline / Phase 1-rebuild diagnostic output

Plan line 4-5 says "Harness Phase 1 onwards unchanged since project
start; awaiting diagnostic output from the comparison pipeline". The
plan also schedules Session 4b-6 to *build* that comparison pipeline.
As of HEAD, no comparison-pipeline code exists (grep for
`comparison|compare_harness|diagnostic_pipeline` in
`curriculum_harness/` returns only incidental hits in docstrings and
the reference-authoring README). No comparison-pipeline output exists.
Plan is internally consistent but readers should not expect to find
4b-6 or 4b-7 artefacts.

### "Flag-and-continue validation rather than hard-fail regeneration"

Plan line 13 lists "flag-and-continue validation" as a current known
failure. This is partially inaccurate for Phase 4: Session 3c
(`cfc73c5`) added `FAIL_SET` + bounded retry loop
(`MAX_REGENERATION_RETRIES = 3`) at
`curriculum_harness/phases/phase4_lt_generation.py:1-58`.
Budget-exhausted LTs go to `state["human_review_required"]` rather
than shipping silently; that is a hard-fail-to-human-review pattern,
not flag-and-continue. Phase 3's KUD generation does still
flag-and-continue in the sense that items with e.g.
`classification_unreliable` can be emitted without forced
regeneration. So the claim is true of Phase 3 but overstated for
Phase 4.

---

## Section 3 — HARNESS PHASES 1-5 STATE

Plan claim: "Phases 1-5 unchanged since project start" with specific
known failures. Verified as follows.

### Recent commits touching Phase 1-5 files

`git log --oneline -- <phase files>` shows **no commits since Session
3d** (late on 2026-04-18) touching Phase 1/3/4/5 source:

```
00a9cb8 [gen] Phase 4 faithfulness filters source_bullets by bullet_type
80bab1b [gen] Phase 1 tags bullets with type metadata
cfc13f5 [gen] Phase 4 regeneration loop, exam-spec output discipline
2e7c5da [gen] Phase 3 profile-conditional branch (Shape C fix)
43f4f4a [gen] Phase 1 scope extraction stabilised
70c1e86 [gen] Phase 4 emits source provenance and faithfulness flags
656b87f [gen] Phase 3 emits source provenance and faithfulness flags
cc04b4a [gen] Phase 1 emits source_bullets artefact
666f7d9 [gen] rename package to curriculum_harness
```

Every 4b-arc commit has been in
`curriculum_harness/reference_authoring/` or `docs/`. Phases 1-5 are
"unchanged during the 4b arc" in the literal sense. But they did
receive substantive Session 3a-3d work (regeneration loop, profile
branch, scope stabilisation, bullet-type tagging) — they are not
"unchanged since project start". Plan's framing is accurate for the
4b arc, inaccurate for project-lifetime.

### Known-failure mode presence in current code

**English-only Phase 1 cue list — CONFIRMED PRESENT.**
`curriculum_harness/phases/phase1_ingestion.py:202-245` defines
`cues: dict[str, tuple[str, ...]]` with English-only needles
("assessment objective", "mark scheme", "subject content",
"expectation", "key stage", "syllabus", "schedule", etc.) across all
five `document_family` branches. `_window_history_grade7` at
line 171-188 uses English-only anchors ("grades 7 and 8 history",
"history, grade"). A Hungarian or Welsh-language source will miss
every needle.

**Hardcoded `GCSE_AQA_EXAM_BLOCK` in Phase 4 — CONFIRMED PRESENT.**
Defined at `curriculum_harness/phases/phase4_lt_generation.py:132-138`
and still attached unconditionally when
`document_family == "exam_specification"` at line 871
(`exam_addon = GCSE_AQA_EXAM_BLOCK if doc_fam == "exam_specification"
else ""`). The comment at line 867-870 explicitly flags this:
"GCSE_AQA_EXAM_BLOCK is still attached on any exam_specification
profile. VALIDITY.md foundation moment 3 (validate_exam_block_scope)
tracks the AQA-specific scoping bug; Session 3c does not change that
gate's scope." The bug is known and scoped-for-future.

**Phase 5 strand mis-routing (token-overlap heuristic) — CONFIRMED
PRESENT.** `curriculum_harness/phases/phase5_formatting.py:70-86`
implements `_competency_relevance_score` as a pure token-set
intersection divided by name token count (tiebroken by substring
match). `map_lt_to_strand_label` at line 127-149 uses this score to
pick between candidate strands. If the source strand labels don't
share tokens with the LT's `kud_source` / `statement` (which is what
the plan means by "label vocabulary doesn't match"), the score
collapses to 0 and routing falls back on arbitrary ordering among
zero-scored candidates.

**Flag-and-continue validation — PARTIALLY PRESENT.** Phase 4 has a
hard-fail regeneration loop (see Section 2 above); Phase 3 still
emits items tagged `classification_unreliable` without forced
regeneration. The plan's framing as a single unresolved pattern is
too coarse for the current code; it needs to be stated per-phase.

---

## Items not verified and why

- **Plan's "32 bullets → 14 Do-Skills on felvételi" consolidation
  collapse claim.** Phrase does not appear in the Phase 3 source; it
  is an empirical observation from a prior run (`outputs/palya-...`
  or `outputs/felveteli-...` directories). Audit brief prohibits
  running the harness, so the specific 32→14 collapse could not be
  re-observed from code alone. The Phase 3 docstring at
  `curriculum_harness/phases/phase3_kud.py:1-57` does describe the
  per_bullet vs strand_aggregated branching that was introduced to
  mitigate this pattern, which is indirect corroboration.
- **"Injection from model priors" (factorial-notation style
  hallucination on felvételi).** Same reason — visible only in a
  produced output, not in Phase source. The source-faithfulness flag
  infrastructure at `curriculum_harness/source_faithfulness.py` plus
  the `SOURCE_FAITHFULNESS_FAIL_FLAG` wired into Phase 4's `FAIL_SET`
  suggests the pattern has been acknowledged in code, but the claim
  itself is about observed output, not code state.
- **Whether the reference-authoring pipeline's criterion gate pass
  rates match the plan's stated 12/11 and 7/6 counts under a fresh
  run.** Audit is read-only; plan numbers matched the last-generated
  `criteria_quality_report.json` summaries on disk, which was the
  read-only verification available.
- **Ontario clustering 43% membership drift / 11-vs-15 cluster count
  claims.** Visible in
  `docs/reference-corpus/ontario-g7-history/quality_report.md` and
  confirmed against plan, but the underlying per-run cluster JSONs
  are not preserved separately — only the stability-summary fields
  in the quality report. If someone later disputes the 43% figure,
  the raw run-level data is not in the repo.
