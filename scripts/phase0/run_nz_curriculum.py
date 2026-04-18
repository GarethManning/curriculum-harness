"""Phase 0 extraction — NZ Curriculum Online Social Sciences Phase 2
via the js_rendered_progressive_disclosure sequence (Session 4a-3
Step 7, the generalisation test).

Writes into docs/run-snapshots/2026-04-18-session-4a-3-nz-curriculum/.
Same primitive as the Ontario DCP run — only the scope differs. If the
primitive needs code changes to handle NZ, the architecture is wrong.
"""

from __future__ import annotations

from pathlib import Path

from curriculum_harness.phases.phase0_acquisition.acquire import acquire
from curriculum_harness.phases.phase0_acquisition.manifest import ScopeSpec
from curriculum_harness.phases.phase0_acquisition.type_detector import (
    DetectionResult,
)


URL = (
    "https://newzealandcurriculum.tahurangi.education.govt.nz/"
    "new-zealand-curriculum-online/nzc---social-sciences-years-4---6/"
    "5637290852.p"
)
OUT = Path(
    "docs/run-snapshots/2026-04-18-session-4a-3-nz-curriculum"
)


def main() -> None:
    scope = ScopeSpec(
        source_reference=URL,
        url=URL,
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
    )
    override = DetectionResult(
        source_type="js_rendered_progressive_disclosure",
        confidence="high",
        rationale=(
            "Session 4a-3 Step 7 deterministic override — the NZ site "
            "renders content server-side but ships enough JS that the "
            "browser primitive is the right sequence for extraction "
            "parity with Ontario DCP."
        ),
        signals={"override_source": "session_4a_3_step_7_runner"},
        is_supported_now=True,
    )
    if OUT.exists():
        import shutil

        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    m = acquire(scope=scope, output_dir=OUT, detection_override=override)

    print("Run complete.")
    print("  source_type :", m.source_type)
    print("  content_hash:", m.content_hash)
    print("  dom_hash    :", m.dom_hash)
    print("  chars       :", m.scope_acquired.get("chars"))
    print("  content_files:")
    for p in m.content_files:
        print(f"    - {p}")


if __name__ == "__main__":
    main()
