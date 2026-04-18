"""Phase 0 extraction — UK gov.uk National Curriculum (England)
Mathematics programme of study, Key Stage 3 (Session 4a-4 Step 8).

Writes into docs/run-snapshots/2026-04-18-session-4a-4-gov-uk-nc-maths-ks3/.
Uses a detection_override because the gov.uk page does not trip the
type detector's nested-DOM heuristic (no <details> elements; div_count
< 1500). The override is the documented fallback for ambiguous pages,
mirroring the JS-rendered runs.
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
    "https://www.gov.uk/government/publications/"
    "national-curriculum-in-england-mathematics-programmes-of-study/"
    "national-curriculum-in-england-mathematics-programmes-of-study"
)
OUT = Path(
    "docs/run-snapshots/2026-04-18-session-4a-4-gov-uk-nc-maths-ks3"
)


def main() -> None:
    scope = HtmlNestedDomScope(
        url=URL,
        content_root_selector=".govspeak",
        section_anchor_selector="#key-stage-3",
        # section_anchor_stop_selector defaults to the anchor's tag (h2)
        include_details_content=True,
        preserve_headings=True,
        notes=(
            "UK Department for Education / Department for Education and "
            "Skills — National Curriculum in England, Mathematics "
            "programmes of study, Key Stage 3 (England). gov.uk-published "
            "HTML; KS3 is interleaved with KS1/KS2/KS4 inside .govspeak, "
            "scoped via heading-anchor (#key-stage-3) — see Step 1 "
            "investigation memo "
            "docs/diagnostics/2026-04-18-gov-uk-nc-maths-ks3-investigation.md."
        ),
    )

    override = DetectionResult(
        source_type="html_nested_dom",
        confidence="high",
        rationale=(
            "Session 4a-4 Step 8 deterministic override — gov.uk's "
            ".govspeak container is structurally a html_nested_dom "
            "source even though it does not trip the conservative "
            "heuristic (no <details>, div_count < 1500)."
        ),
        signals={"override_source": "session_4a_4_step_8_runner"},
        is_supported_now=True,
    )

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    m = acquire(scope=scope, output_dir=OUT, detection_override=override)

    # Post-acquisition annotation: link the investigation memo so the
    # manifest is self-describing.
    m.investigation_memo_refs = [
        "docs/diagnostics/2026-04-18-gov-uk-nc-maths-ks3-investigation.md",
    ]
    # Persist the post-acquisition annotation by re-saving the manifest.
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
