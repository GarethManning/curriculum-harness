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

## Architecture

- `inventory/build_inventory.py` — verbatim source-content extraction into
  structured content blocks with source-position and heading hierarchy.
- `kud/classify_kud.py` — applies the LT authoring skill's Step 0
  knowledge-type decision tree mechanically. 3x self-consistency at
  temperature 0.3. Welsh CfW placement rule: sustained orientations
  route to Do-Disposition/Type 3; propositional content to Know/Understand/Type 1;
  occasion-triggered skills to Do-Skill/Type 2.
- `gates/kud_gates.py` — structural quality gates (source coverage,
  traceability, artefact-count ratio per vision v4.1, Type 3
  distribution, no compound unsplit). Failures halt output with
  specific diagnostics.
- `pipeline/run_pipeline.py` — orchestration (inventory → classify →
  gates → output).
- `lt/` (stub) — LT generator for session 4b-2.
- `criterion/` (stub) — criterion/observation-indicator generator for
  session 4b-2.

## Implementation status

Session 4b-1 (this session):

- inventory: **implemented**
- KUD classifier: **implemented**
- KUD quality gates: **implemented**
- pipeline orchestration: **implemented** (KUD only)
- LT generator: **stubbed** — session 4b-2
- criterion generator: **stubbed** — session 4b-2
- comparison pipeline: **not here** — session 4b-6

## Running

```bash
python -m curriculum_harness.reference_authoring.pipeline.run_pipeline \
    --snapshot docs/run-snapshots/<session>-<source-slug>/ \
    --out docs/reference-corpus/<source-slug>/
```
