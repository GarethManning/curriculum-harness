"""Phase 0 extraction — Welsh Curriculum for Wales Mathematics &
Numeracy "Statements of what matters" (Session 4a-4 Step 9, the
generalisation test).

Writes into docs/run-snapshots/2026-04-18-session-4a-4-wales-cfw-maths-sow/.
Same primitive as the gov.uk run (Step 8) — only the scope differs
(single_main_container shape vs hierarchical_with_scope shape;
in-container chrome stripping vs heading-anchor scoping). If the
primitive needs code changes to handle Wales, the architecture is
wrong.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from curriculum_harness.phases.phase0_acquisition.acquire import acquire
from curriculum_harness.phases.phase0_acquisition.scope import (
    HtmlNestedDomScope,
)
from curriculum_harness.phases.phase0_acquisition.type_detector import (
    DetectionResult,
)


URL = (
    "https://hwb.gov.wales/curriculum-for-wales/"
    "mathematics-and-numeracy/statements-of-what-matters/"
)
OUT = Path(
    "docs/run-snapshots/2026-04-18-session-4a-4-wales-cfw-maths-sow"
)


def main() -> None:
    scope = HtmlNestedDomScope(
        url=URL,
        content_root_selector="article#aole-v2",
        # No section_* fields — single URL = single section. The whole
        # article body is the target; in-container chrome (in-page nav,
        # prev/next, explore-links) is stripped via exclude_selectors.
        exclude_selectors=[
            "nav",
            ".tab-next-prev",
            ".explore-links",
            ".contents",
            ".cookie-block",
            ".breadcrumb",
        ],
        include_details_content=True,
        preserve_headings=True,
        notes=(
            "Welsh Government / hwb.gov.wales — Curriculum for Wales, "
            "Mathematics and Numeracy Area of Learning and Experience, "
            "Statements of what matters. Session 4a-4 Step 9 — "
            "generalisation test of extract_nested_dom primitive against "
            "a structurally-distinct second source. Different platform "
            "(custom CMS vs GOV.UK Publishing), different container "
            "depth (5 vs 10), different scoping discipline (no anchor; "
            "in-container chrome stripping needed). See Step 2 "
            "investigation memo "
            "docs/diagnostics/2026-04-18-wales-cfw-mathematics-sow-investigation.md."
        ),
    )

    override = DetectionResult(
        source_type="html_nested_dom",
        confidence="high",
        rationale=(
            "Session 4a-4 Step 9 deterministic override — Wales hwb's "
            "article#aole-v2 container is a single_main_container "
            "html_nested_dom source. Conservative auto-heuristic does "
            "not trip (no <details>, modest div count)."
        ),
        signals={"override_source": "session_4a_4_step_9_runner"},
        is_supported_now=True,
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    m = acquire(scope=scope, output_dir=OUT, detection_override=override)

    m.investigation_memo_refs = [
        "docs/diagnostics/2026-04-18-wales-cfw-mathematics-sow-investigation.md",
    ]
    import json

    (OUT / "manifest.json").write_text(
        json.dumps(m.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("Run complete.")
    print("  source_type :", m.source_type)
    print("  content_hash:", m.content_hash)
    print("  chars       :", m.scope_acquired.get("chars"))
    print("  content_files:")
    for p in m.content_files:
        print(f"    - {p}")


if __name__ == "__main__":
    main()
