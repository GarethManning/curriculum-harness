"""Phase 0 extraction — UK gov.uk National Curriculum (England)
English programmes of study, KS1–KS3.

Extracts the full statutory content from the gov.uk .govspeak container,
which contains the nested <ul><li> statutory bullet lists that Phase 1's
tag-stripping HTML extractor misses.

No section_anchor_selector — we want the full KS1–KS3 scope in one pass.
KS4 content will be included in the raw extraction; the Phase 1 Haiku
scoping pass will restrict to KS1–KS3 per the grade field in the config.

Output: docs/run-snapshots/england-nc-english-2026-05-11/content_v2.txt
"""

from __future__ import annotations

from pathlib import Path

from curriculum_harness.phases.phase0_acquisition.acquire import acquire
from curriculum_harness.phases.phase0_acquisition.scope import HtmlNestedDomScope
from curriculum_harness.phases.phase0_acquisition.type_detector import DetectionResult


URL = (
    "https://www.gov.uk/government/publications/"
    "national-curriculum-in-england-english-programmes-of-study/"
    "national-curriculum-in-england-english-programmes-of-study"
)
OUT = Path("docs/run-snapshots/england-nc-english-2026-05-11")
CONTENT_FILE = "content_v2.txt"


def main() -> None:
    scope = HtmlNestedDomScope(
        url=URL,
        content_root_selector=".govspeak",
        # No section_anchor_selector — extract full KS1-KS3 content.
        # Phase 1 Haiku scoping will exclude KS4.
        include_details_content=True,
        preserve_headings=True,
        notes=(
            "UK Department for Education — National Curriculum in England, "
            "English programmes of study, KS1–KS3 (statutory). gov.uk-published "
            "HTML; .govspeak container holds all statutory <ul><li> bullet lists. "
            "Run ID: england_nc_english_ks1_to_ks3_2026_05_11_v2. "
            "Fix for v1 Phase 1 tag-stripper extraction failure."
        ),
    )

    override = DetectionResult(
        source_type="html_nested_dom",
        confidence="high",
        rationale=(
            "Deterministic override — gov.uk .govspeak container is "
            "html_nested_dom even though it does not trip the conservative "
            "heuristic (no <details>, div_count < 1500). Pattern mirrors "
            "run_gov_uk_nc_maths_ks3.py."
        ),
        signals={"override_source": "run_gov_uk_nc_english_ks1_to_ks3"},
        is_supported_now=True,
    )

    OUT.mkdir(parents=True, exist_ok=True)

    m = acquire(
        scope=scope,
        output_dir=OUT,
        content_filename=CONTENT_FILE,
        detection_override=override,
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
