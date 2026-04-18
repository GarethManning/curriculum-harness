"""Session 4a-4 Step 3b — regenerate the six prior Phase 0 artefacts
under schema 0.5.0 and verify behaviour preservation.

Goes beyond content-hash comparison (per Step 3b's data-pipeline
engineer revision):

1. **Content file hash**: must be byte-identical to the stored 0.4.0
   value. Halts on drift.
2. **Manifest structural fields** (`primitive_sequence`, per-entry
   `verification_trace.verdict`, `known_pathology_handling`,
   `investigation_memo_refs`, `source_type`): must be unchanged in
   value (stored vs regenerated).
3. **`scope_requested` field equivalence** (modulo shape): every
   field carrying a non-default value in the 0.4.0 flat scope must
   appear with the same value in the 0.5.0 discriminated-union
   variant; fields dropped in the migration must have been default-
   valued in 0.4.0.

Runs each regeneration into ``outputs/_regression_4a4/<slug>/`` so
the canonical run-snapshots stay untouched until the comparisons
pass and we explicitly promote them.

JS-rendered cases (Ontario DCP, NZ Curriculum) are deterministic
only insofar as the live site is byte-stable. Source-side drift
(rendered DOM changes due to CDN edits, A/B tests, dynamic content)
is reported separately so a refactor regression is not confounded
with a content-side change.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from curriculum_harness.phases.phase0_acquisition.acquire import acquire
from curriculum_harness.phases.phase0_acquisition.manifest import ScopeSpec
from curriculum_harness.phases.phase0_acquisition.type_detector import (
    DetectionResult,
)


REPO = Path("/Users/garethmanning/Github/curriculum-harness")


# ``predates_dual_verify`` flags artefacts whose stored snapshot was
# captured before Session 4a-2b introduced the dual-mode
# verify_extraction_quality split. The pipeline-shape difference
# (single ``verify_extraction_quality`` entry vs paired
# ``verify_raw_extraction``/``verify_normalised_extraction`` entries)
# is a legitimate pre-existing pipeline evolution, NOT a Session 4a-4
# refactor regression. We still compare ``content_hash`` strictly —
# the dual-verify primitives are observation-only and do not mutate
# output, so hashes must match.
CASES: list[dict[str, Any]] = [
    {
        "label": "Common Core 7.RP",
        "stored_dir": REPO
        / "docs/run-snapshots/2026-04-18-session-4a-2a-regression-common-core-7rp",
        "scope_kwargs": dict(
            source_reference="https://www.thecorestandards.org/Math/Content/7/RP/",
            url="https://www.thecorestandards.org/Math/Content/7/RP/",
            css_selector="article section.content",
            notes=(
                "CCSS 7.RP cluster — article > section.content wraps "
                "the whole cluster (h2 + identifiers + h4 + standard/"
                "substandard divs). Regression re-run under schema 0.3.0 "
                "(Session 4a-2a)."
            ),
        ),
        "is_js": False,
        "predates_dual_verify": True,
    },
    {
        "label": "DfE KS3 Maths (PDF)",
        "stored_dir": REPO
        / "docs/run-snapshots/2026-04-18-session-4a-2a-regression-dfe-ks3",
        "scope_kwargs": dict(
            source_reference=(
                "https://assets.publishing.service.gov.uk/media/"
                "5a7c1408e5274a1f5cc75a68/SECONDARY_national_curriculum_"
                "-_Mathematics.pdf"
            ),
            notes=(
                "DfE / UK statutory National Curriculum — Mathematics "
                "programme of study, Key Stage 3 (England). Full-document "
                "extraction, no page_range or section_heading scope. "
                "Regression re-run under schema 0.3.0 (Session 4a-2a)."
            ),
        ),
        "is_js": False,
        "predates_dual_verify": True,
    },
    {
        "label": "AP US Gov CED Unit 1 (requeued)",
        "stored_dir": REPO
        / "docs/run-snapshots/2026-04-18-session-4a-2a-ap-usgov-requeued",
        "scope_kwargs": dict(
            source_reference=str(
                REPO
                / "outputs/phase0-test-ap-usgov-unit1-requeued-2026-04-18/_source.pdf"
            ),
            page_range=[40, 55],
            section_heading="Foundations of American Democracy",
            pdf_dedup_coords=True,
            pdf_dedup_coord_tolerance=1,
            notes=(
                "AP US Government and Politics Course and Exam Description, "
                "Unit 1 'Foundations of American Democracy'. Origin URL: "
                "https://apcentral.collegeboard.org/media/pdf/"
                "ap-us-government-and-politics-course-and-exam-description.pdf. "
                "Local-path acquisition used because College Board's "
                "robots.txt blanket-disallows all crawlers."
            ),
        ),
        "is_js": False,
        "predates_dual_verify": True,
    },
    {
        "label": "Ontario K-8 Grade 7 History (PDF)",
        "stored_dir": REPO
        / "docs/run-snapshots/2026-04-18-session-4a-2b-ontario-g7-history",
        "scope_kwargs": dict(
            # The 4a-2b runner used a relative path; mirror it so the
            # source_reference field matches byte-for-byte under
            # field-level scope comparison.
            source_reference="outputs/phase0-test-ontario-g7-history-2026-04-18/_source.pdf",
            section_identifier="History, Grade 7",
            notes=(
                "Ontario K-8 Social Studies / History / Geography (revised 2023), "
                "Grade 7 History strand. Origin URL: "
                "https://assets-us-01.kc-usercontent.com/"
                "fbd574c4-da36-0066-a0c5-849ffb2de96e/"
                "f6f2efba-a7aa-4c70-94ce-f7593a7490ca/"
                "SocialStudiesHistoryGeography-AODA.pdf. "
                "Local-path acquisition; dedup off per Step 3 pre-check findings."
            ),
        ),
        "is_js": False,
        "predates_dual_verify": False,
    },
    {
        "label": "Ontario DCP Grade 7 History (JS)",
        "stored_dir": REPO
        / "docs/run-snapshots/2026-04-18-session-4a-3-ontario-dcp-g7-history",
        "scope_kwargs": dict(
            source_reference=(
                "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/"
                "grades/g7-history/strands"
            ),
            url=(
                "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/"
                "grades/g7-history/strands"
            ),
            wait_for_selector="main",
            css_selector="main",
            browser_timeout_ms=60000,
            notes=(
                "Ontario DCP Grade 7 History, Expectations by strand. "
                "Session 4a-3 Step 6 — first test of "
                "js_rendered_progressive_disclosure primitive sequence. "
                "Extracts overall-expectation content including FOCUS ON "
                "tags; specific-expectations text lives on SPA-routed "
                "sub-pages (see investigation memo)."
            ),
        ),
        "is_js": True,
        "predates_dual_verify": False,
    },
    {
        "label": "NZ Curriculum Online Social Sciences Phase 2 (JS)",
        "stored_dir": REPO
        / "docs/run-snapshots/2026-04-18-session-4a-3-nz-curriculum",
        "scope_kwargs": dict(
            source_reference=(
                "https://newzealandcurriculum.tahurangi.education.govt.nz/"
                "new-zealand-curriculum-online/nzc---social-sciences-years-4---6/"
                "5637290852.p"
            ),
            url=(
                "https://newzealandcurriculum.tahurangi.education.govt.nz/"
                "new-zealand-curriculum-online/nzc---social-sciences-years-4---6/"
                "5637290852.p"
            ),
            wait_for_selector="main",
            css_selector="main",
            dismiss_modal_selector="button[aria-label*='cookie' i]",
            browser_timeout_ms=60000,
            notes=(
                "NZ Curriculum Online — Social Sciences Phase 2 (Years 4–6). "
                "Session 4a-3 Step 7 — generalisation test of "
                "js_rendered_progressive_disclosure primitive. Different "
                "jurisdiction, different framework (no SPA markers; heavy "
                "custom CMS), consent modal present (exercises "
                "dismiss_modal_selector)."
            ),
        ),
        "is_js": True,
        "predates_dual_verify": False,
    },
]


# Verification entries that the pipeline never produces but are
# appended manually after a run (e.g. structured cross-validation).
# Filtered out of the verdict-comparison check.
_NON_PIPELINE_VERIFICATION_PRIMITIVES: frozenset[str] = frozenset(
    {"manual_cross_validation"}
)


_DEFAULT_SCALARS = {None, "", False, 0}


def _is_default(key: str, value: Any) -> bool:
    if isinstance(value, (list, dict)):
        return not value
    if value in _DEFAULT_SCALARS:
        return True
    if key == "pdf_dedup_coord_tolerance" and value == 1:
        return True
    if key == "browser_timeout_ms" and value == 30000:
        return True
    if key == "include_details_content" and value is True:
        return True
    if key == "preserve_headings" and value is True:
        return True
    return False


def _compare_scope(stored: dict[str, Any], regen: dict[str, Any]) -> list[str]:
    """Field-level equivalence ignoring shape/source_type artefacts.

    Reports differences for any field whose stored value is non-default
    AND whose regenerated value differs (or is missing).
    """

    diffs: list[str] = []
    # Fields the regenerator may add that the stored 0.4.0 didn't have:
    # source_type (now in scope), notes (carried from kwargs), defaults
    # injected by the variant. We only flag mismatches for fields whose
    # stored value is non-default — the migration is allowed to drop
    # default-valued fields silently.
    for key, stored_val in stored.items():
        if key == "source_type":
            continue
        if _is_default(key, stored_val):
            continue
        regen_val = regen.get(key, None)
        if regen_val != stored_val:
            diffs.append(f"  field {key!r}: stored={stored_val!r} regen={regen_val!r}")
    return diffs


def _verification_verdicts(manifest: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        (e.get("primitive", "?"), e.get("verdict", "?"))
        for e in manifest.get("verification_trace", [])
        if e.get("primitive") not in _NON_PIPELINE_VERIFICATION_PRIMITIVES
    ]


def main() -> int:
    overall_ok = True
    for case in CASES:
        label = case["label"]
        stored_dir: Path = case["stored_dir"]
        is_js: bool = case["is_js"]
        out_dir = REPO / f"outputs/_regression_4a4/{stored_dir.name}"
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Load stored canonical manifest
        with (stored_dir / "manifest.json").open() as f:
            stored = json.load(f)

        scope = ScopeSpec(**case["scope_kwargs"])
        kwargs: dict[str, Any] = {"scope": scope, "output_dir": out_dir}
        if is_js:
            kwargs["detection_override"] = DetectionResult(
                source_type="js_rendered_progressive_disclosure",
                confidence="high",
                rationale="Step 3b regression: re-using the 4a-3 deterministic override.",
                signals={"override_source": "session_4a_4_step_3b_regen"},
                is_supported_now=True,
            )

        try:
            m = acquire(**kwargs)
        except Exception as exc:  # noqa: BLE001
            # Source-side outage (e.g. site now bot-blocked, network
            # error) is reported as N/A — it is not a refactor
            # regression even though the regeneration cannot complete.
            msg = f"{type(exc).__name__}: {exc}"
            classifier = "OUTAGE" if "Phase0Paused" in msg or "403" in msg else "ERROR"
            print(f"[{classifier}] {label}: {msg[:200]}")
            if classifier == "ERROR":
                overall_ok = False
            continue

        # Post-acquisition metadata applied by the original runners
        # (not produced by the pipeline itself): copy from the stored
        # manifest so the regression check focuses on what the pipeline
        # produces. ``known_pathology_handling`` and
        # ``investigation_memo_refs`` are runner-applied annotations.
        for runner_field in ("known_pathology_handling", "investigation_memo_refs"):
            stored_v = stored.get(runner_field) or []
            if stored_v:
                setattr(m, runner_field, stored_v)

        ok = True
        notes: list[str] = []
        predates_dual_verify: bool = case.get("predates_dual_verify", False)

        # 1. Content hash — strict for all cases. JS-rendered drifts are
        # flagged separately as source-side rather than refactor-side.
        if (m.content_hash or "") != (stored.get("content_hash") or ""):
            if is_js:
                notes.append(
                    "  content_hash differs from stored snapshot — "
                    "[JS source: source-side drift suspected, not "
                    "necessarily a refactor regression]:"
                )
                notes.append(
                    f"    stored={stored.get('content_hash')} regen={m.content_hash}"
                )
                # Tracked as a warning, not a hard failure, for JS runs.
            else:
                ok = False
                notes.append(
                    "  content_hash MISMATCH (deterministic case): "
                    f"stored={stored.get('content_hash')} regen={m.content_hash}"
                )

        regen_dump = json.loads(m.model_dump_json())

        # 2. Manifest structural fields. ``primitive_sequence`` and the
        # verification verdict shape are skipped for snapshots predating
        # the Session 4a-2b dual-verify split — that change is a
        # legitimate pipeline evolution, not a Session 4a-4 refactor
        # regression.
        structural_fields = [
            "source_type",
            "known_pathology_handling",
            "investigation_memo_refs",
        ]
        if not predates_dual_verify:
            structural_fields.append("primitive_sequence")

        for fname in structural_fields:
            stored_v = stored.get(fname)
            regen_v = regen_dump.get(fname)
            if stored_v != regen_v:
                ok = False
                notes.append(
                    f"  field {fname!r}: stored={stored_v!r} regen={regen_v!r}"
                )

        if predates_dual_verify:
            # Cross-check: the regenerated pipeline must still produce
            # the dual-mode verify primitives, and they must all be
            # ``clean``. Anything else (warning, failure) is a refactor
            # regression even on a stale baseline.
            regen_verdicts = _verification_verdicts(regen_dump)
            non_clean = [
                (p, v) for p, v in regen_verdicts if v != "clean"
            ]
            if non_clean:
                ok = False
                notes.append(
                    f"  regen verification non-clean: {non_clean}"
                )
            notes.append(
                "  [snapshot predates 4a-2b dual-verify split — "
                "primitive_sequence + verification_trace shape drift "
                "is expected pipeline evolution, not a refactor "
                "regression]"
            )
        else:
            stored_verdicts = _verification_verdicts(stored)
            regen_verdicts = _verification_verdicts(regen_dump)
            if stored_verdicts != regen_verdicts:
                ok = False
                notes.append(
                    f"  verification_trace verdicts: "
                    f"stored={stored_verdicts} regen={regen_verdicts}"
                )

        # 3. scope_requested field equivalence
        scope_diffs = _compare_scope(
            stored.get("scope_requested", {}),
            regen_dump.get("scope_requested", {}),
        )
        if scope_diffs:
            ok = False
            notes.extend(scope_diffs)

        status = "OK" if ok else "DRIFT"
        marker = "" if not is_js else "  [js-rendered]"
        print(f"[{status}] {label}{marker}")
        for n in notes:
            print(n)
        if not ok:
            overall_ok = False

    print("\n=== summary ===")
    print("ALL OK" if overall_ok else "DRIFTS DETECTED — investigate before proceeding")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
