# Session 4a-4 Step 3b — schema 0.5.0 regression report

**Date:** 2026-04-18
**Script:** `scripts/phase0/regenerate_under_0_5_0.py`
**Output:** `outputs/_regression_4a4/<slug>/`

## Outcome — ALL OK (within behaviour-preserving bounds)

| Case                               | Hash match    | Structural match               | Notes                                                                                                                  |
| ---------------------------------- | ------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Common Core 7.RP                   | N/A — outage  | N/A — outage                   | Live site now returns HTTP 403 to the harness UA. Source-side change between Session 4a-2a and 4a-4. Cannot regenerate. |
| DfE KS3 Maths (PDF)                | OK            | OK\*                           | \*`primitive_sequence` and `verification_trace` shape differ from stored snapshot — pre-existing pipeline evolution from Session 4a-2b's dual-verify split, not a 4a-4 refactor regression. |
| AP US Gov CED Unit 1 (requeued)    | OK            | OK\*                           | Same pre-4a-2b shape note as DfE KS3.                                                                                   |
| Ontario K-8 Grade 7 History (PDF)  | OK            | OK                             | Snapshot is from current pipeline shape — full structural match.                                                        |
| Ontario DCP Grade 7 History (JS)   | OK            | OK                             | Live site stable; full match (excluding manually-appended `manual_cross_validation` verification entry).                |
| NZ Curriculum Online Social Sci    | DRIFT (0-char) | OK (structural)                | Live site now returns a "Block Page" to the playwright browser fingerprint. Extracted 0 chars; SHA-256 of empty string. Source-side change, not a refactor regression. |

## What Step 3b verified

The schema 0.5.0 refactor is **behaviour-preserving** for the
extraction pipeline: every artefact whose source remains accessible
produced byte-identical content under the discriminated-union scope
schema.

Strict checks that passed:
- **Content hash byte-stable** for 4/4 deterministic cases that could
  run (DfE KS3, AP US Gov, Ontario K-8, Ontario DCP).
- **Manifest structural fields** (`source_type`,
  `known_pathology_handling`, `investigation_memo_refs`,
  `primitive_sequence` for current-pipeline snapshots) unchanged in
  value; runner-applied annotations
  (`known_pathology_handling`, `investigation_memo_refs`) re-applied
  from the stored manifest in the regen script to mirror the original
  runner behaviour.
- **Verification verdicts** (`clean` for every pipeline-produced
  entry; `manual_cross_validation` is a runner annotation excluded
  from comparison).
- **`scope_requested` field equivalence** — every non-default field
  on the stored 0.4.0 flat scope appears with the same value in the
  regenerated 0.5.0 discriminated-union variant.

## Drifts that are NOT refactor regressions

1. **Common Core 7.RP — site now bot-blocked.** `thecorestandards.org`
   returns HTTP 403 to both the project UA and a generic browser UA.
   The site appears to have added bot detection between 4a-2a and 4a-4.
   The schema refactor cannot be tested against this source today;
   the fix is either to source a cached copy of the page or to wait
   for the site's policy to shift. Tracked as **OUTAGE**, not an
   error.
2. **NZ Curriculum — Block Page returned to browser fingerprint.**
   The Tahurangi platform now serves a "Block Page" template (HTML
   `<title>Block Page</title>`) to playwright Chromium with this
   harness's default fingerprint. The browser fetch reports HTTP 200
   with 2 627 bytes of rendered HTML, but the `main` element is
   absent so extraction returns 0 chars. Tracked as **source-side
   drift on a JS source**, not a refactor regression. The structural
   manifest fields all match.
3. **DfE KS3 / AP US Gov / Common Core sequence shape.** These three
   were captured in Session 4a-2a under a single `verify_extraction_quality`
   primitive (pre-normalise mode only). Session 4a-2b later split that
   into two primitives (`verify_raw_extraction` +
   `verify_normalised_extraction`). The current pipeline therefore
   produces a different `primitive_sequence` than the 4a-2a snapshots
   recorded — but the verify primitives are observation-only and do
   not mutate output, so content hashes are byte-stable across the
   shape change. The regen script flags these explicitly as
   pre-existing pipeline evolution.

## Recommendation

The schema 0.5.0 refactor is **safe to ship**. Step 3a's discriminated-
union split, the forward-compatible deserialiser, and the `ScopeSpec`
backwards-compat callable preserve extraction behaviour byte-for-byte
on every source we can still acquire deterministically. Source-side
drifts (bot blocks, layout changes) are independent of the refactor
and tracked as such.

The Common Core and NZ outages do **not** block Phase 0 completion.
They surface an upstream concern for Session 4b's reference test
corpus: corpus sources need to be either local-archived or
mirror-served so reference outputs remain reproducible across site
changes.
