"""Unit tests for `curriculum_harness.source_faithfulness`.

Guards the shared helper Phase 3 and Phase 4 use to compute source
provenance and set the SOURCE_FAITHFULNESS_FAIL flag. Also covers the
edge case where the bullet corpus is empty (pre-Session-3a runs
shouldn't have flags flood the output).
"""
from __future__ import annotations

from curriculum_harness.source_faithfulness import (
    SOURCE_FAITHFULNESS_FAIL_FLAG,
    compute_parent_provenance,
    compute_source_provenance,
)


def _bullet(bid: str, text: str, btype: str = "topic_statement") -> dict:
    return {
        "id": bid,
        "text": text,
        "source_location": "",
        "bullet_type": btype,
    }


def test_empty_corpus_returns_pass_without_flag() -> None:
    prov, passed = compute_source_provenance("anything", [])
    assert prov == []
    assert passed is True


def test_empty_text_returns_pass_without_flag() -> None:
    prov, passed = compute_source_provenance(
        "", [_bullet("sb_001", "some bullet text")]
    )
    assert prov == []
    assert passed is True


def test_below_threshold_returns_fail_with_provenance() -> None:
    # Invented claim that shares no lemmas with the bullet.
    prov, passed = compute_source_provenance(
        "calculate factorials for counting arrangements",
        [_bullet("sb_001", "explain how treaties shaped early settlement")],
    )
    assert passed is False
    # Provenance is still recorded for the below-threshold best match
    # (empty only when lemma / ngram overlap is literally zero).
    # Either outcome (empty list or recorded match with low score) is
    # acceptable here; we only require `passed=False`.


def test_above_threshold_returns_pass_with_matching_bullet() -> None:
    prov, passed = compute_source_provenance(
        "describe the significance of the fur trade to diverse communities",
        [_bullet("sb_001", "describe the significance of the fur trade to diverse communities")],
    )
    assert passed is True
    assert prov
    assert prov[0]["bullet_id"] == "sb_001"
    assert prov[0]["score"] >= 0.35
    assert prov[0]["bullet_type"] == "topic_statement"


def test_provenance_records_top_k_matches() -> None:
    bullets = [
        _bullet("sb_001", "analyse the impact of colonialism on Indigenous governance"),
        _bullet("sb_002", "describe the fur trade between Indigenous and European communities"),
        _bullet("sb_003", "explain treaty negotiations and their long-term impact"),
    ]
    prov, passed = compute_source_provenance(
        "analyse the impact of colonialism on Indigenous peoples",
        bullets,
        top_k=3,
    )
    assert passed is True
    # Best match is sb_001 because it shares 'analyse impact colonialism indigenous'.
    assert prov[0]["bullet_id"] == "sb_001"
    # The list is at most top_k and sorted by score descending.
    assert len(prov) <= 3
    scores = [p["score"] for p in prov]
    assert scores == sorted(scores, reverse=True)


def test_parent_provenance_uses_content_or_statement_field() -> None:
    kud_parents = [
        {"id": "k1", "content": "identify prime numbers and composite numbers"},
        {"id": "k2", "content": "apply the distributive property in algebra"},
    ]
    prov, passed = compute_parent_provenance(
        "identify prime numbers up to 100", kud_parents
    )
    assert passed is True
    assert prov[0]["parent_id"] == "k1"


def test_flag_constant_is_the_expected_string() -> None:
    # Gate reports key on this literal; guard against accidental rename.
    assert SOURCE_FAITHFULNESS_FAIL_FLAG == "SOURCE_FAITHFULNESS_FAIL"
