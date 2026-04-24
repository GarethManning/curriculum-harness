# scripts/legacy/

Scripts in this directory are archived. They are retained for reference — do not run against current artefacts.

## Why scripts here are legacy

- Output schemas have diverged from the live canonical schema
- Output paths point at superseded directories
- Not wired into any current pipeline, CI, or workflow
- Live artefacts are produced by different processes

## Preflight scope

`scripts/preflight.py` Check 6 (no inline BAND_LABELS) does NOT scan `scripts/legacy/`. Legacy code intentionally preserves historical patterns. Legacy scripts are exempt from active-code invariants.

## Current files

### `generate_real_wellbeing.py`

Produced the original REAL-1 corpus at `docs/reference-corpus/real-wellbeing-2026-04/` (4-band, 107 criteria, schema v1). Superseded by session-by-session LLM criterion authoring plus dedicated version build scripts (`scripts/build_unified_wellbeing_v5.py`, `v6.py`). Schema diverged at v2 with the addition of T3 observation fields (`observation_indicators`, `confusable_behaviours`, `absence_indicators`, `conversation_prompts`) that this script does not produce. Not safe to run against the live `docs/reference-corpus/real-wellbeing/` path or against v2-schema artefacts.

Retained for reference: the core pipeline logic (architecture diagnosis, KUD classification via LLM, LT gate-check, deterministic prerequisite edge generation) may be worth reusing if a future session needs to run the same workflow for a different internal school framework from scratch.

Last run: REAL-1, 2026-04-20. Archived REAL-9b, 2026-04-24.
