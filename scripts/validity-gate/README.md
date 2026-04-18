# Validity gate

Scaffolded scripts backing the assertions in the repo-root `VALIDITY.md`.
See that file for the full claim, foundation moments, and pre-mortem.

## Status legend

- **pending** — the assertion is live, the artefacts needed to check
  it already land in `outputs/<run>/`, and a gate script should be
  written. Currently emits `NOT_IMPLEMENTED` exit code 2.
- **deferred** — the assertion is reserved for a pipeline phase that
  does not yet exist (e.g. the criterion bank). Do not implement until
  that phase lands. Currently emits `NOT_IMPLEMENTED` exit code 2.

## Scripts

| Script | Foundation moment | Status |
| --- | --- | --- |
| `validate_source_coverage.py` | 1 — source → LT coverage | **implemented** |
| `validate_source_faithfulness.py` | 1 — no-fabrication | **implemented** |
| `validate_architecture_diagnosis.py` | 1 — architecture verifiable from source | **implemented** |
| `validate_lt_surface_form.py` | 2 — word count / format / compound-check | **implemented** |
| `validate_regenerate_loop.py` | 2 — regenerate loop ran for any initial failure | **implemented** |
| `validate_exam_block_scope.py` | 3 — `GCSE_AQA_EXAM_BLOCK` only on AQA sources | pending (known bug) |
| `validate_lt_criterion_coverage.py` | 4 — LT decomposes to ≥1 criterion | deferred |
| `validate_prerequisite_dag.py` | 4 — prerequisite edges form a DAG | deferred |

## Running

```bash
python scripts/validity-gate/run_all.py outputs/<run>/
```

The runner prints a per-script status table and exits 0 (scaffold
reports but does not block). When individual scripts are promoted to
real checks, the runner will exit non-zero on any FAIL.

Individual gates can also be run directly:

```bash
python scripts/validity-gate/validate_source_faithfulness.py outputs/<run>/ --out faithfulness.json
```

Each gate prints its JSON report to stdout (or `--out`) and a
one-line `[PASS]`/`[FAIL]` summary to stderr.

## Promoting a stub to a real gate

1. Read the assertion's section in `VALIDITY.md` — the foundation
   moment describes what the check should assert and what artefact it
   reads.
2. Replace the stub body with the real check. Preserve the
   `RUN_PATH_ARG` convention (single positional arg pointing at a
   run's `outputs/<run>/` directory).
3. Exit 0 on PASS, 1 on FAIL, 2 on NOT_IMPLEMENTED. The runner
   distinguishes these three.
4. Update the status table above and the foundation-moment entry in
   `VALIDITY.md` from `pending` to a short description of what the
   gate now enforces.
