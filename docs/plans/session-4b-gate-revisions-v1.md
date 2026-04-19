# Session 4b — gate revisions (v1)

Running record of KUD / LT / criterion quality-gate threshold revisions
made during the 4b arc. Revisions are data-driven (triggered by
real-corpus runs), provisional until validated against additional
sources in the same domain, and named explicitly rather than quietly
bumped.

## 4b-2 — `artefact_count_ratio` domain-aware ceiling

**Date applied:** 2026-04-19 (session 4b-2).

**Trigger.** Session 4b-1 ran the reference-authoring pipeline on the
Welsh CfW Health and Well-being Statements of What Matters. KUD
classification produced 33 items across 20 expected-yield blocks
(excluding 4 severely-underspecified blocks and 2 blocks halted for
classification unreliability). Artefact-count ratio = 33/20 = 1.650.
The single ceiling at 1.5 (vision v4.1) halted the pipeline.

**Review.** Gareth and the panel (Wiliam/Claxton/Christodoulou/Shankar)
inspected the KUD output (`docs/reference-corpus/welsh-cfw-health-wellbeing/kud-review.md`).
Conclusion: the content is correct. Welsh CfW source text routinely
bundles a propositional claim (Type 1) with a sustained orientation
(Type 3) within a single bullet, and the LT authoring skill's
compound-splitting rule requires those be separated into distinct KUD
items. The 1.65 ratio is the skill working as designed, not noise.
The gate threshold is the problem.

**Revision.** `artefact_count_ratio` is now domain-aware:

| Source domain  | Floor | Ceiling | Status                          |
|----------------|-------|---------|---------------------------------|
| hierarchical   | 0.8   | 1.5     | unchanged, inherits vision v4.1 |
| horizontal     | 0.8   | 1.5     | unchanged, inherits vision v4.1 |
| dispositional  | 0.8   | 2.2     | **PROVISIONAL** (4b-2 revision) |

**Rationale for the 2.2 dispositional ceiling.**

1. Dispositional prose sources legitimately bundle multiple
   capabilities (propositional claim + sustained orientation, or two
   sustained orientations) within a single source bullet.
2. The LT authoring skill's compound rule mandates splitting by
   knowledge type regardless of source-bullet count.
3. Welsh CfW's real-corpus ratio of 1.65 is therefore expected
   behaviour for a rich dispositional source, not inflation.
4. 2.2 provides ~33% headroom above the observed 1.65 without being
   unbounded, preserving the gate's role as a structural sanity check.

**Provisional status.** This ceiling is derived from a single
dispositional source. The next dispositional extraction (candidate:
Scottish CfE Health and Wellbeing, or the Alberta Wellness curriculum)
may land at a ratio that challenges 2.2 — either significantly lower
(suggesting Welsh CfW is an outlier and the ceiling can tighten) or
higher (suggesting 2.2 is still too tight for the domain). The
ceiling is reviewed against each new dispositional source until a
stable cross-source pattern emerges. This revision document is
updated in place when that happens.

**Code locations.**

- Threshold constants: `curriculum_harness/reference_authoring/gates/kud_gates.py`
  (`RATIO_BANDS`).
- Gate function: `_gate_artefact_count_ratio` now takes a
  `source_domain` kwarg; the resulting diagnostic names the band
  used and flags the dispositional ceiling as provisional.
- Pipeline CLI: `pipeline/run_pipeline.py` accepts `--domain`
  (default: inferred from `--dispositional`).

**Re-run result.** With the revised threshold, the Welsh CfW KUD now
passes all halting gates. `docs/reference-corpus/welsh-cfw-health-wellbeing/quality_report.md`
updated.

## Arc-plan touchpoint

`docs/plans/session-4b-arc-plan-v3.md` §"Structural checks in reference
authoring" refers to vision v4.1 artefact count ratios. That reference
is still correct for hierarchical/horizontal; this document records
the dispositional deviation until vision v4.2 lands.
