"""Unit tests for `curriculum_harness.source_bullets.extract_source_bullets`.

Guards the three detectors (marker_bullet, numbered_outcome,
topic_statement), the known false-positive guard (short date-like
lines must NOT be emitted as numbered_outcomes), and the Session-3d
semantic bullet_type classifier.
"""
from __future__ import annotations

from curriculum_harness.source_bullets import (
    BULLET_TYPES,
    classify_bullet_type,
    extract_source_bullets,
)


def _detectors(bullets: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for b in bullets:
        out[b["detector"]] = out.get(b["detector"], 0) + 1
    return out


def test_empty_or_trivial_input_returns_empty() -> None:
    assert extract_source_bullets("") == []
    assert extract_source_bullets("   ") == []
    assert extract_source_bullets("short") == []


_PAD = "\n\nContext paragraph providing some narrative background for the tests to exceed the 100-char minimum input guard and exercise realistic detector behaviour.\n"


def test_marker_bullet_detector_catches_common_markers() -> None:
    text = _PAD + (
        "Learning outcomes:\n"
        "\n"
        "• First outcome text that is reasonably long.\n"
        "- Second outcome text that is reasonably long.\n"
        "* Third outcome text that is reasonably long.\n"
        "– Fourth outcome text that is reasonably long.\n"
    )
    bullets = extract_source_bullets(text)
    assert _detectors(bullets).get("marker_bullet") == 4
    # ids are sequential; marker bullets sit among any other detections
    assert all(b["id"].startswith("sb_") for b in bullets)


def test_numbered_outcome_detector_catches_letter_number_codes() -> None:
    text = _PAD + (
        "Specific expectations\n"
        "\n"
        "A1.1 describe the significance of the fur trade to diverse communities.\n"
        "A1.2 analyse the impact of colonialism on Indigenous governance structures.\n"
        "A1.3 explain how treaties shaped early Canadian settlement patterns.\n"
    )
    bullets = extract_source_bullets(text)
    numbered = [b for b in bullets if b["detector"] == "numbered_outcome"]
    assert len(numbered) == 3
    assert numbered[0]["text"].startswith("A1.1 describe")
    # Session 3d — numbered_outcome structurally maps to specific_expectation.
    assert all(b["bullet_type"] == "specific_expectation" for b in numbered)


def test_numbered_outcome_guard_rejects_short_date_like_lines() -> None:
    # Regression fixture — felvételi's "2023. szeptember 1." date was
    # matching the numbered_outcome pattern before the min-text guard
    # was added. Must stay rejected as a numbered_outcome.
    text = _PAD + (
        "Követelmények:\n"
        "\n"
        "2023. szeptember 1.\n"
        "Elemi kombinatorika mint összeszámolás és sorrendek leírása.\n"
    )
    bullets = extract_source_bullets(text)
    detectors = _detectors(bullets)
    assert detectors.get("numbered_outcome", 0) == 0
    # Real topic bullet under the colon-header is still captured.
    topic_texts = [b["text"] for b in bullets if b["detector"] == "topic_statement"]
    assert any("Elemi kombinatorika" in t for t in topic_texts)


def test_topic_statement_detector_catches_hungarian_style_list() -> None:
    text = _PAD + (
        "Az írásbeli feladatsorokban előforduló követelmények:\n"
        "\n"
        "Elemi kombinatorika (összeszámolás, sorrendek száma, kiválasztás).\n"
        "Matematikai állítások megfogalmazása és igazolása.\n"
        "Műveletek törtekkel és tizedes törtekkel.\n"
    )
    bullets = extract_source_bullets(text)
    topic = [b for b in bullets if b["detector"] == "topic_statement"]
    assert len(topic) == 3
    assert "követelmények" in topic[0]["source_location"].lower()


def test_bullets_get_stable_sequential_ids() -> None:
    text = _PAD + (
        "Header:\n"
        "\n"
        "First topic that is sufficiently long and complete.\n"
        "Second topic that is sufficiently long and complete.\n"
        "Third topic that is sufficiently long and complete.\n"
    )
    bullets = extract_source_bullets(text)
    ids = [b["id"] for b in bullets]
    # Sequential with no gaps.
    assert ids == [f"sb_{i:03d}" for i in range(1, len(ids) + 1)]


def test_duplicates_are_collapsed() -> None:
    text = _PAD + (
        "Topics:\n"
        "\n"
        "Apply the commutative property to whole-number addition.\n"
        "Apply the commutative property to whole-number addition.\n"
        "Apply the associative property to whole-number addition.\n"
    )
    bullets = extract_source_bullets(text)
    topic_texts = [b["text"] for b in bullets if b["detector"] == "topic_statement"]
    assert len(topic_texts) == 2
    assert any("commutative" in t for t in topic_texts)
    assert any("associative" in t for t in topic_texts)


# --- Session 3d: bullet_type semantic classifier --------------------


def test_classify_bullet_type_enum_is_stable() -> None:
    # Guard downstream code that indexes by enum value — any rename
    # must be a deliberate schema migration.
    assert set(BULLET_TYPES) == {
        "specific_expectation",
        "overall_expectation",
        "sample_question",
        "teacher_prompt",
        "cross_grade",
        "front_matter",
        "other",
    }


def test_classify_sample_question_on_trailing_question_mark() -> None:
    out = classify_bullet_type(
        "What role does an Elder play in your community?",
        "line 7500",
        "marker_bullet",
    )
    assert out == "sample_question"


def test_classify_teacher_prompt_on_eg_lead() -> None:
    out = classify_bullet_type(
        "e.g., the birth of a sibling or starting school",
        "line 8000",
        "marker_bullet",
    )
    assert out == "teacher_prompt"


def test_classify_cross_grade_on_non_target_grade_tag() -> None:
    # Sample question cross-referenced to another grade.
    out = classify_bullet_type(
        "Why don't farmers in Ontario grow bananas or pineapples. (Grade 2, B1.2)",
        "line 7580",
        "marker_bullet",
        target_grade="7",
    )
    assert out == "cross_grade"


def test_classify_cross_grade_matches_target_grade_is_not_cross() -> None:
    out = classify_bullet_type(
        "What are wetlands. Why are they important. (Grade 7, A3.4)",
        "line 8115",
        "marker_bullet",
        target_grade="7",
    )
    # Not cross_grade (same grade). Falls through other rules to
    # "other" because no other heuristic matches on this short line.
    assert out != "cross_grade"


def test_classify_specific_expectation_for_numbered_detector() -> None:
    out = classify_bullet_type(
        "A1.1 describe how and why roles change",
        "line 8771",
        "numbered_outcome",
    )
    assert out == "specific_expectation"


def test_classify_front_matter_on_known_header_token() -> None:
    out = classify_bullet_type(
        "the strands of the curriculum; and",
        "line 44 (under: Version history)",
        "marker_bullet",
    )
    assert out == "front_matter"


def test_classify_front_matter_on_early_line_number() -> None:
    # No header, line well before the Ontario 8000 cutoff.
    out = classify_bullet_type(
        "All students can succeed.",
        "line 519",
        "marker_bullet",
    )
    assert out == "front_matter"


def test_classify_other_default_for_late_unmatched_bullet() -> None:
    out = classify_bullet_type(
        "analyse data, evidence, and information, applying concepts",
        "line 8246",
        "marker_bullet",
    )
    assert out == "other"


def test_bullets_emit_detector_and_bullet_type_fields() -> None:
    text = _PAD + (
        "Learning outcomes:\n"
        "\n"
        "• First outcome text that is reasonably long.\n"
    )
    bullets = extract_source_bullets(text)
    assert bullets
    # Session 3d schema — both fields must exist on every bullet.
    for b in bullets:
        assert "detector" in b
        assert "bullet_type" in b
        assert b["bullet_type"] in BULLET_TYPES
