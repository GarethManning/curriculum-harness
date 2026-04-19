# Welsh CfW Health and Well-being — A-D-band output (generated in error)

This directory contains the Welsh Curriculum for Wales Health and
Well-being reference corpus as produced in **Sessions 4b-1 and 4b-2**
using REAL School Budapest's **Band A-D** framework across **ages
5-14**.

## Why this is preserved separately

The output was generated using REAL School Budapest's A-D / 5-14
framework, which the reference-authoring pipeline imported from the
LT authoring skill's example calibration as if it were a mandatory
output format for all sources. **This was an error in the session
prompts.** A-D is not Welsh Curriculum for Wales' native progression
structure: Welsh CfW uses **Progression Steps 1-5** across ages 3-16
per the Welsh Government's statutory specification under the
Curriculum and Assessment (Wales) Act 2021.

The Curriculum Harness is domain-agnostic. Its reference outputs use
each source's own native progression structure (Welsh Progression
Steps for Welsh CfW, US grade levels for Common Core, Canadian grade
levels for Ontario, Scottish CfE Levels for Scottish CfE, Key Stages
for the English National Curriculum, NZ Curriculum Levels for the
NZC). Imposing REAL School Budapest's A-D bands on Welsh CfW
violated this principle.

## What's in this directory

The full 4b-1/4b-2 output is preserved here:

- `inventory.json`, `kud.json`, `kud-review.md` — KUD layer (band-
  agnostic; remains correct).
- `competency_clusters.json`, `lts.json` — competency clusters and
  Learning Targets (band-agnostic structurally; remain correct).
- `band_statements.json` — Type 1/2 band statements with bands `A`,
  `B`, `C`, `D`. **Band labels are misframed.** The pedagogical
  content of the statements (the developmental escalation pattern
  using independence / complexity / scope / precision / reasoning /
  transfer levers) is usable, but the labels do not match Welsh CfW's
  own framework.
- `observation_indicators.json` — Type 3 observation indicator sets
  with bands `A` through `D` and self-reflection prompts calibrated to
  REAL School's A-D, not to Welsh CfW's own per-Step expectations.
- `quality_report.md` / `quality_report.json` — pipeline gate report
  for that run.
- `reference-review.md` — human-readable review document.
- `welsh-cfw-hwb-*.csv` — CSV exports with `band_A` through `band_D`
  columns.

## When to use this version vs the corrected version

- **REAL School Budapest's internal use:** because A-D matches REAL's
  own framework, REAL teachers can consume this output directly with
  no translation. It is acceptable for that purpose.
- **Domain-agnostic reference for the harness arc:** **DO NOT use
  this output.** Use the corrected version at the parent directory
  (`docs/reference-corpus/welsh-cfw-health-wellbeing/`), generated in
  Session 4b-2.5, which expresses the same content against Welsh CfW's
  own Progression Steps 1-5.

## Why the KUD layer is reusable

The KUD is band-agnostic — it carries no Progression Step or A-D
labels. The Session 4b-2.5 regeneration reads `kud.json` from this
subdirectory and runs only the LT, band-statement, and observation-
indicator stages with the Welsh-Progression-Step-aware generators.
Nothing about the Welsh KUD itself was wrong.

## Why this is not deleted

Per the Curriculum Harness's hard rule against overwriting generated
artefacts (see `~/Documents/gareth-config/RULES.md`), the original
output is preserved rather than rewritten. The mislabelling is
documented honestly here, and the corrected version sits at the
parent directory for clarity.
