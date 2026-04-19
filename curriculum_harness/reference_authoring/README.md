# Reference-authoring pipeline

Produces neutral reference KUDs, LTs, and criteria for anchor curriculum
sources. Compared against harness output in the separate comparison
pipeline (Session 4b-6).

## Distinct from the harness

This subsystem is **not** called by the harness (Phase 0–5 in
`curriculum_harness/phases/`). It runs separately, reads an extracted
source (a run-snapshot `content.txt`), and writes a reference corpus
to `docs/reference-corpus/<source-slug>/`.

## Discipline

The pipeline **must not** read, import, or reference any harness output
(no Palya run, no `outputs/...` JSONs, no prior KUDs). References are
neutral targets. Any cross-contamination invalidates their role as
comparators.

## Source-native progression structure (load-bearing principle)

The pipeline **does not impose** any specific school's band/level/grade
framework on its outputs. Each curriculum source is read, its own
native progression structure is detected, and downstream stages
generate band statements and observation indicators against THAT
structure:

- **Welsh Curriculum for Wales** (any AOLE) → Progression Steps 1-5,
  ages 3-16 per Welsh Government statutory specification.
- **US Common Core State Standards** → US grade levels (single-band
  per source: Grade 7, etc.) per the Common Core State Standards
  Initiative.
- **Ontario K-8** → Canadian grade levels (single-band per source)
  per the Ontario Ministry of Education.
- **Scottish CfE** → Early / First / Second / Third / Fourth Levels
  + Senior Phase per Education Scotland.
- **England National Curriculum** → Key Stages 1-4 per the DfE
  statutory framework.
- **New Zealand Curriculum** → Levels 1-8 per the Ministry of
  Education NZ.

`progression/detect_progression.py` produces a `ProgressionStructure`
for the source via a curated jurisdiction lookup (URL host/path with
source-slug fallback) plus a source-text inspection fallback at
medium confidence. If neither succeeds the pipeline **halts** with a
specific diagnostic — it does NOT default to A-D.

**Single-band sources are first-class.** When `band_count == 1`
(Common Core 7.RP, Ontario Grade 7 History, etc.) the band-statement
generator produces a single statement per LT at the source's grade
level, not a band progression. The observation-indicator generator
produces a single band entry per LT. Self-reflection prompts come
from the source's own per-band calibration on the
`ProgressionStructure`.

**Translation is out of scope.** The harness does not translate
between native frameworks. Mapping a Welsh CfW Progression Step
output onto REAL School Budapest's A-D, or any other school-specific
structure, is downstream product work, not harness work. (See the 4b
arc plan's "Deferred product work" section for the KUD visualisation
app concept.)

**Detection confidence drives output stability.** Medium- or
low-confidence detection (source-text inspection, no curated match)
flags the generated reference with `progression_structure_uncertain`
in the quality report so a reviewer knows the band framework itself
may need verification before the reference is used as a comparator.

The LT authoring skill's "typically A-D across ages 5-14" example is
a REAL School Budapest calibration. It is an EXAMPLE, not a mandatory
output format. Sessions 4b-1 and 4b-2 mistook it for a universal
default; Session 4b-2.5 corrected the pipeline.

## Architecture

- `inventory/build_inventory.py` — verbatim source-content extraction into
  structured content blocks with source-position and heading hierarchy.
- `kud/classify_kud.py` — applies the LT authoring skill's Step 0
  knowledge-type decision tree mechanically. 3x self-consistency at
  temperature 0.3. Welsh CfW placement rule: sustained orientations
  route to Do-Disposition/Type 3; propositional content to Know/Understand/Type 1;
  occasion-triggered skills to Do-Skill/Type 2.
- `gates/kud_gates.py` — structural quality gates (source coverage,
  traceability, artefact-count ratio with **domain-aware thresholds**
  per vision v4.1 + the 4b-2 PROVISIONAL dispositional revision, Type 3
  distribution, no compound unsplit). Failures halt output with
  specific diagnostics.
- `progression/detect_progression.py` — source-native progression
  structure detection (curated jurisdiction lookup + source-text
  fallback + halt-on-no-match). Returns `ProgressionStructure` with
  band labels in developmental order, verified age-range hint,
  detection confidence, and per-band self-reflection prompts.
- `lt/cluster_competencies.py` — clusters KUD items into competencies
  (2-3 LTs per competency, LT skill). 3x self-consistency with a
  deterministic stability check (cluster count, membership drift via
  Jaccard alignment, dominant-knowledge-type drift, unmatched-cluster
  existence).
- `lt/generate_lts.py` — LT generator. 2-3 LTs per competency;
  single-construct rule; knowledge-type split when a competency mixes
  Type 3 with Type 1/2; "I can" / "The student" definition-format
  check.
- `lt/generate_band_statements.py` — Type 1/2 band-statement
  generator. **Bands are the source's own native bands** (e.g.
  Progression Step 1-5 for Welsh CfW; single Grade for a single-grade
  source). Progression levers (independence, complexity, scope,
  precision, reasoning, transfer) are universal — only the labels are
  local. Quality gate: "I can" prefix, 10-25 word count,
  observable-verb presence, banned substrings. Gate failures halt.
- `lt/generate_observation_indicators.py` — Type 3 observation-
  indicator generator. LT-specific observable behaviours per native
  band, LT-specific parent prompts, prerequisite pointers,
  developmental conversation protocol reference. Self-reflection
  prompts come from the source's own per-band calibration on the
  `ProgressionStructure`. Mode 3 gate rejects rubric descriptors.
  Gate failures halt.
- `pipeline/run_pipeline.py` — orchestration. Full sequence: inventory
  → classify → KUD gates → detect progression → cluster → LTs → bands
  + indicators → extended report. `--resume-from-kud` skips inventory
  + classify; progression detection still runs against the loaded
  inventory. Writes `progression_structure.json` to the corpus.
- `criterion/generate_criteria.py` — Type 1/2 criterion generator.
  Five-level rubric (No Evidence / Emerging / Developing / Competent
  / Extending) per the rubric logic skill, with Competent = pass
  criterion ("I can" declarative, demonstrated independently at the
  LT's band). 3x self-consistency at temperature 0.3. Structural
  signature (collapsed within-limit word-count class + binary
  scope + dominant verb bucket) determines rubric stability. Verb
  matching uses the same `_lemmatise` logic as the gate module.
- `criterion/generate_supporting_components.py` — for each rubric
  that passes halting gates: co-construction plan (stages + student
  prompts + anchor-examples guidance), student-facing rubric
  (5 levels + self-check prompts), and feedback guide (moves per
  level, no moves for Extending).
- `gates/criterion_gates.py` — criterion quality gates. Halting:
  five-level present, Competent-framing judge, asymmetric word
  limits (10/15/20/25/20), observable verbs at Emerging+, banned
  phrasing, single-construct scope. Informational: propositional-
  thin flag for factual Type 1 LTs where the rubric necessarily
  compresses at Emerging/Developing. The gate's `OBSERVABLE_VERBS`
  list is kept in sync with the generator's `_VERB_BUCKETS`.

## Implementation status

After session 4b-4:

- inventory: **implemented** (4b-1)
- KUD classifier: **implemented** (4b-1); `source_context` parameter
  added (4b-3) to support classifier priming (Ontario FOCUS ON)
- KUD quality gates: **implemented** (4b-1); domain-aware
  `artefact_count_ratio` **revised twice**: dispositional ceiling 1.5→2.2
  PROVISIONAL (4b-2), hierarchical ceiling 1.5→2.5 (4b-3 — CC 7.RP
  landed at 2.2); documented in
  `docs/plans/session-4b-gate-revisions-v1.md`
- FOCUS ON priming: **implemented** (4b-3) — `--focus-on-priming` flag
  injects Seixas/Morton Big Six descriptions; post-classification
  verification records agree/disagree/unstable per placement rule without
  silent override
- progression detection: **implemented** (4b-2.5); `band_details` and
  `progression_philosophy` fields added (4b-3); all curated jurisdiction
  constants updated
- pipeline orchestration: **implemented**, full sequence including
  progression detection, LT + band + indicator stages, `--resume-from-kud`
  supported
- competency clustering: **implemented** with operationalised stability
  check (4b-2); large-KUD fixes: max_tokens 4096→8192, skip source_blocks
  for >80-item KUDs, duplicate/missing-item recovery (4b-3)
- LT generator: **implemented** (4b-2)
- Type 1/2 band-statement generator: **implemented** with source-native
  bands (4b-2; 4b-2.5 removed hardcoded A-D)
- Type 3 observation-indicator generator: **implemented** with source-native
  bands and per-source self-reflection prompt calibration (4b-2)
- CSV exporter: **implemented** (4b-2); progression metadata section added
  (4b-3); criteria + supporting-components CSVs added (4b-4)
- review renderer: **implemented** (4b-2); per-band developmental index
  table added (4b-3); rubric tables + supporting-components sections
  added inside Type 1/2 LT blocks (4b-4)
- Reference corpus: 3 sources through full pipeline — Welsh CfW HWB
  (dispositional, 5 bands), Common Core G7 RP (hierarchical, 1 band),
  Ontario G7 History (horizontal, 1 band, FOCUS ON priming). Welsh CfW
  HWB and Common Core G7 RP additionally through the 4b-4 criterion +
  supporting-components stage.
- Type 1/2 criterion generator (five-level rubrics): **implemented**
  (4b-4) with structural-signature self-consistency; signature
  relaxation (within-limit word-count class collapsed; scope binary)
  and lemmatiser sync between generator + gate documented in
  `docs/plans/session-4b-gate-revisions-v1.md` §4b-4.
- Type 1/2 supporting components (co-construction plan + student
  rubric + feedback guide): **implemented** (4b-4), runs after the
  criterion gate on passing rubrics only.
- standalone criterion-only runner: `scripts/reference_authoring/run_criteria.py`
  — reads an existing corpus's `lts.json` + `progression_structure.json`,
  runs the criterion generator + gates + supporting-components stage,
  writes `criteria.json` / `criteria_quality_report.{json,md}` /
  `supporting_components.json`. Appropriate tool for adding criterion
  artefacts to a corpus generated before the criterion stage existed.
- comparison pipeline: **not here** — session 4b-6

## Running

Full pipeline from a Phase 0 snapshot:

```bash
python -m curriculum_harness.reference_authoring.pipeline.run_pipeline \
    --snapshot docs/run-snapshots/<session>-<source-slug>/ \
    --out docs/reference-corpus/<source-slug>/ \
    --domain dispositional   # or hierarchical / horizontal
```

Resume from an existing KUD (skips inventory + KUD re-classification):

```bash
python -m curriculum_harness.reference_authoring.pipeline.run_pipeline \
    --resume-from-kud \
    --out docs/reference-corpus/<source-slug>/ \
    --domain dispositional   # or hierarchical / horizontal
```

Ontario History sources with FOCUS ON tags (primes classifier with
Seixas/Morton Big Six descriptions; records agree/disagree/unstable
per placement rule in quality_report.md):

```bash
python -m curriculum_harness.reference_authoring.pipeline.run_pipeline \
    --snapshot docs/run-snapshots/<session>-ontario-<slug>/ \
    --out docs/reference-corpus/<slug>/ \
    --domain horizontal \
    --focus-on-priming
```

Run the criterion stage only (adds Type 1/2 five-level rubrics +
supporting components to a corpus whose inventory / KUD / LTs / bands
are already generated; does NOT touch any upstream artefact):

```bash
python -m scripts.reference_authoring.run_criteria \
    --corpus docs/reference-corpus/<source-slug>/
```

Render the full reference for human review:

```bash
python -m scripts.reference_authoring.render_reference_for_review \
    --corpus docs/reference-corpus/<source-slug>/
```

Export reference as CSV (LT and indicator CSVs use source-native band
columns):

```bash
python -m scripts.reference_authoring.export_reference_to_csv \
    --corpus docs/reference-corpus/<source-slug>/ \
    --prefix <slug>
```
