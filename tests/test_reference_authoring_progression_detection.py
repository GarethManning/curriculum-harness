"""Deterministic tests for source-native progression-structure detection.

The detector must:

1. Identify Welsh CfW sources from the hwb.gov.wales URL host AND from
   the source_slug fallback. Five Progression Step labels.
2. Identify Common Core single-grade sources (band_count=1).
3. Identify Ontario single-grade sources (band_count=1).
4. Identify Scottish CfE multi-Level sources.
5. Fall back to source-text inspection at medium confidence when neither
   URL nor slug match.
6. Halt with ``ProgressionDetectionError`` when nothing matches —
   the pipeline must NOT silently default to A-D.

These tests run without any LLM call and are pure functions of input.
"""

from __future__ import annotations

import pytest

from curriculum_harness.reference_authoring.progression import (
    ProgressionDetectionError,
    ProgressionStructure,
    band_label_slug,
    detect_progression,
)
from curriculum_harness.reference_authoring.types import (
    ContentBlock,
    SourceInventory,
)


def _inv(
    *,
    slug: str = "",
    reference: str = "",
    text_blocks: list[str] | None = None,
) -> SourceInventory:
    blocks: list[ContentBlock] = []
    for i, t in enumerate(text_blocks or [], start=1):
        blocks.append(
            ContentBlock(
                block_id=f"blk_{i:04d}",
                raw_text=t,
                block_type="statement",
                line_start=i,
                line_end=i,
            )
        )
    return SourceInventory(
        source_slug=slug,
        snapshot_path="/tmp/whatever",
        manifest_content_hash="x",
        phase0_version="0",
        source_reference=reference,
        content_blocks=blocks,
    )


def test_welsh_cfw_url_high_confidence_five_progression_steps() -> None:
    inv = _inv(
        slug="wales-cfw-health-wellbeing-sow",
        reference=(
            "https://hwb.gov.wales/curriculum-for-wales/"
            "health-and-well-being/statements-of-what-matters/"
        ),
    )
    s = detect_progression(inv)
    assert s.detection_confidence == "high"
    assert s.source_type == "welsh_cfw_aole"
    assert s.band_count == 5
    assert s.band_labels == [
        "Progression Step 1",
        "Progression Step 2",
        "Progression Step 3",
        "Progression Step 4",
        "Progression Step 5",
    ]
    assert "ages 3-16" in s.age_range_hint
    assert all(label in s.band_self_reflection_prompts for label in s.band_labels)
    assert all(s.band_self_reflection_prompts[label] for label in s.band_labels)


def test_welsh_cfw_slug_fallback_high_confidence() -> None:
    inv = _inv(slug="wales-cfw-maths-sow", reference="")
    s = detect_progression(inv)
    assert s.source_type == "welsh_cfw_aole"
    assert s.detection_confidence == "high"
    assert s.band_count == 5


def test_common_core_grade_seven_single_band() -> None:
    inv = _inv(
        slug="common-core-7rp",
        reference="http://www.corestandards.org/Math/Content/7/RP/",
    )
    s = detect_progression(inv)
    assert s.detection_confidence == "high"
    assert s.source_type == "us_common_core_grade"
    assert s.band_count == 1
    assert s.band_labels == ["Grade 7"]
    assert s.is_single_band()
    assert "Grade 7" in s.band_self_reflection_prompts


def test_ontario_grade_seven_single_band() -> None:
    inv = _inv(
        slug="ontario-k8-g7-history-pdf",
        reference="https://www.edu.gov.on.ca/eng/curriculum/elementary/grade7-8.html",
    )
    s = detect_progression(inv)
    assert s.detection_confidence == "high"
    assert s.source_type == "ontario_grade"
    assert s.band_count == 1
    assert s.band_labels == ["Grade 7"]
    assert "Grade 7" in s.band_self_reflection_prompts


def test_scottish_cfe_url_high_confidence() -> None:
    inv = _inv(
        slug="scottish-cfe-health",
        reference=(
            "https://education.gov.scot/curriculum-for-excellence/"
            "health-and-wellbeing/"
        ),
    )
    s = detect_progression(inv)
    assert s.detection_confidence == "high"
    assert s.source_type == "scottish_cfe"
    assert s.band_labels[0] == "Early Level"
    assert "Senior Phase" in s.band_labels


def test_england_nc_url_high_confidence() -> None:
    inv = _inv(
        slug="dfe-ks3-maths",
        reference=(
            "https://www.gov.uk/government/publications/"
            "national-curriculum-in-england-mathematics-programmes-of-study"
        ),
    )
    s = detect_progression(inv)
    assert s.detection_confidence == "high"
    assert s.source_type == "england_national_curriculum"
    assert s.band_labels == ["Key Stage 1", "Key Stage 2", "Key Stage 3", "Key Stage 4"]


def test_source_text_fallback_medium_confidence() -> None:
    # No URL/slug match; explicit Progression Step markers in text.
    inv = _inv(
        slug="custom-internal",
        reference="https://example.com/no-match",
        text_blocks=[
            "Progression Step 1: foundational expectations.",
            "Progression Step 2: developing expectations.",
            "Progression Step 3: secure expectations.",
        ],
    )
    s = detect_progression(inv)
    assert s.detection_confidence == "medium"
    assert s.uncertain()
    assert s.source_type == "welsh_cfw_aole_inferred"
    assert s.band_count == 3
    assert s.band_labels == [
        "Progression Step 1",
        "Progression Step 2",
        "Progression Step 3",
    ]


def test_halt_when_no_detection_signal() -> None:
    inv = _inv(slug="totally-novel", reference="https://example.com/x")
    with pytest.raises(ProgressionDetectionError):
        detect_progression(inv)


def test_band_label_slug() -> None:
    assert band_label_slug("Progression Step 1") == "progression_step_1"
    assert band_label_slug("Grade 7") == "grade_7"
    assert band_label_slug("Early Level") == "early_level"
    assert band_label_slug("Key Stage 4") == "key_stage_4"


def test_progression_structure_to_dict_round_trips_label_order() -> None:
    inv = _inv(
        slug="wales-cfw-x",
        reference="https://hwb.gov.wales/curriculum-for-wales/",
    )
    s = detect_progression(inv)
    d = s.to_dict()
    assert d["band_labels"] == [
        "Progression Step 1",
        "Progression Step 2",
        "Progression Step 3",
        "Progression Step 4",
        "Progression Step 5",
    ]
    assert d["band_count"] == 5
    assert d["detection_confidence"] == "high"
