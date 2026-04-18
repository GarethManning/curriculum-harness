# Session 3d — Ontario end-to-end re-run post bullet-type calibration (2026-04-18)

Full-pipeline run of Ontario Grade 7 History with Session 3d's
additions active: semantic `bullet_type` on every Phase-1 bullet,
gate-level filtering in `_run_loader.py`, and Phase 4 faithfulness
running against the coverage-relevant bucket only.

Config: `configs/ontario_session3d_e2e.json`. Run completed end-to-end
with exit 0.

## Calibration effect — Session 3c → Session 3d

Both runs operate on the same source PDF (Ontario 2018 Social Studies
/ History / Geography, AODA) and identical scoping. Phase 1 is
deterministic; the bullet corpus is byte-identical at 937 bullets.
The difference is how downstream gates and Phase 4's faithfulness
check read that corpus.

### Phase 4 regeneration outcomes

| Measure                         | Session 3c | Session 3d |
|---------------------------------|-----------:|-----------:|
| Total LTs entering regen loop   | 18         | 18         |
| `success@retry_1`               | 1          | 1          |
| `exhausted_retries`             | 17         | 17         |
| `language_bypass_ship_flagged`  | 0          | 0          |
| Human-review-required entries   | 17         | 17         |

Same aggregate regen mix. The identity of the LT that clears retry
differs — Session 3d's success match traces to a Grade 1
specific_expectation bullet (coverage-relevant) rather than to a
front-matter line, because Phase 4's faithfulness check now filters
to specific_expectation + overall_expectation.

Successful regen (Session 3d):
```
"I can compare how colonialism affected First Nations, Métis, Inuit,
 and settler populations in distinctly different ways"
```
outcome: `success@retry_1`; supporting bullet is a specific_expectation
from the Grade 1 Social Studies section (A1.5).

### Validity gates (Session 3d output)

- `validate_source_coverage`: **3.0 %** (1 / 33 coverage-relevant
  bullets). Session 3c snapshot rebaselined under the same filter:
  0.0 % (0 / 33).
- `validate_source_faithfulness`: **5.6 %** (1 / 18 LTs). Session 3c
  rebaselined: 0.0 %.
- `validate_architecture_diagnosis`: **0.0 %** (0 / 9 strands).
  Session 3c rebaselined: 0.0 % (11 strands).
- `validate_lt_surface_form`: **PASS 100 % (18 / 18)**.
- `validate_regenerate_loop`: **PASS** — clean=1, success-after-retry=0,
  language-bypass=0, human-review=17, gaps=0.

### Bullet-type distribution (unchanged 937-bullet corpus)

| bullet_type            | count |
|------------------------|------:|
| front_matter           | 676   |
| other                  | 181   |
| sample_question        |  38   |
| specific_expectation   |  33   |
| cross_grade            |   9   |
| overall_expectation    |   0   |
| teacher_prompt         |   0   |
| **total**              | 937   |

Coverage denominator (specific_expectation + overall_expectation) = 33.
857 excluded + 38 illustrative + 9 extraction-error = 904 bullets
reported diagnostically but not required to trace.

## What the calibration did and did not fix

Did:
- Collapsed the coverage denominator 937 → 33. The reported coverage
  now reflects LT-to-real-content-bullet match, not LT-to-any-line
  match.
- Surfaced the Phase 1 scoping failure as a diagnostic warning on
  every gate (`[WARN] excluded bucket has 857 bullets ... above review
  threshold 20`), where before it was hidden in the denominator.
- Let one regen-loop success route through a genuine
  specific_expectation match rather than a front-matter false positive.

Did not:
- Fix the underlying Phase 1 scoping problem. The Grade 7 History
  section of the PDF is still not in the scoped slice; the 33
  coverage-relevant bullets are all Grade 1.
- Raise the regeneration-success rate in absolute terms (1/18 both
  runs). The rate is bounded by the real content overlap between the
  Grade 7 LTs and the Grade 1 bullets, which is low by construction.
- Change Phase 3's faithfulness check. Only Phase 4 was threaded
  through the filter in Session 3d (per-phase scope).

## Known phase errors

Every `phase4_mcp_lt_*` call succeeded or recovered via Sonnet-direct
fallback. Phase 3 `MCP/tools failed: Connection error.` warnings
continue as in Sessions 3b / 3c (MCP endpoint intermittent); Phase 3
fell back to Sonnet-direct on each bucket as designed.

## Artefacts

- Run output: `outputs/ontario-2026-04-18-session-3d-e2e/`
- Baseline JSON (rebaselined Session 3c snapshot under Session 3d
  filter): `docs/project-log/baseline-2026-04-18-session-3d/*.json`
- Classification diagnostic:
  `docs/diagnostics/2026-04-18-ontario-bullet-classification.md`
- Calibrated baseline section:
  `docs/project-log/baseline-measurements-2026-04-18.md`
  §"Session 3d — Ontario calibrated baseline".
