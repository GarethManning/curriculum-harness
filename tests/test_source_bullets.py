"""Unit tests for `curriculum_harness.source_bullets.extract_source_bullets`.

Guards the three detectors (marker_bullet, numbered_outcome,
topic_statement) and the known false-positive guard (short date-like
lines must NOT be emitted as numbered_outcomes).
"""
from __future__ import annotations

from curriculum_harness.source_bullets import extract_source_bullets


def _types(bullets: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for b in bullets:
        out[b["bullet_type"]] = out.get(b["bullet_type"], 0) + 1
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
    assert _types(bullets).get("marker_bullet") == 4
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
    numbered = [b for b in bullets if b["bullet_type"] == "numbered_outcome"]
    assert len(numbered) == 3
    assert numbered[0]["text"].startswith("A1.1 describe")


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
    types = _types(bullets)
    assert types.get("numbered_outcome", 0) == 0
    # Real topic bullet under the colon-header is still captured.
    topic_texts = [b["text"] for b in bullets if b["bullet_type"] == "topic_statement"]
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
    topic = [b for b in bullets if b["bullet_type"] == "topic_statement"]
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
    topic_texts = [b["text"] for b in bullets if b["bullet_type"] == "topic_statement"]
    assert len(topic_texts) == 2
    assert any("commutative" in t for t in topic_texts)
    assert any("associative" in t for t in topic_texts)
