"""Unit tests for Phase 4 regeneration-loop helpers (Session 3c).

Covers the pure-Python pieces that don't require an LLM call:
- FAIL_SET membership
- ``_fail_flags`` filter preserves order, excludes warnings
- ``_should_bypass_for_language`` language-bypass gate
- ``_compose_retry_instruction`` shape
"""
from __future__ import annotations

from curriculum_harness.phases.phase4_lt_generation import (
    FAIL_SET,
    MAX_REGENERATION_RETRIES,
    REGEN_INTRODUCED_NEW_FLAG,
    REGEN_NEAR_IDENTICAL_FLAG,
    REGENERATION_NEAR_IDENTICAL_THRESHOLD,
    SOURCE_LANGUAGE_BYPASS_ANNOTATION,
    _compose_retry_instruction,
    _fail_flags,
    _should_bypass_for_language,
    cosine_similarity_text,
)
from curriculum_harness.source_faithfulness import SOURCE_FAITHFULNESS_FAIL_FLAG


def test_fail_set_contains_the_seven_hard_failures() -> None:
    assert FAIL_SET == frozenset({
        SOURCE_FAITHFULNESS_FAIL_FLAG,
        "EXCEEDS_WORD_LIMIT",
        "COMPOUND_TYPE",
        "EMBEDDED_EXAMPLE",
        "DISPOSITION_RUBRIC_ERROR",
        "MISSING_I_CAN_FORMAT",
        "MISSING_LT_STATEMENT",
    })
    assert "POSSIBLE_COMPOUND" not in FAIL_SET
    assert "LT_FORMAT_EXPECTATION_MISMATCH" not in FAIL_SET


def test_fail_flags_preserves_order_and_excludes_warnings() -> None:
    flags = [
        "POSSIBLE_COMPOUND",
        "EXCEEDS_WORD_LIMIT",
        "LT_FORMAT_EXPECTATION_MISMATCH",
        "MISSING_I_CAN_FORMAT",
    ]
    assert _fail_flags(flags) == ["EXCEEDS_WORD_LIMIT", "MISSING_I_CAN_FORMAT"]


def test_language_bypass_fires_for_non_en_with_faithfulness_only() -> None:
    assert _should_bypass_for_language(
        [SOURCE_FAITHFULNESS_FAIL_FLAG], "non-en"
    )


def test_language_bypass_does_not_fire_on_english() -> None:
    assert not _should_bypass_for_language(
        [SOURCE_FAITHFULNESS_FAIL_FLAG], "en"
    )


def test_language_bypass_does_not_fire_if_other_fail_flags_present() -> None:
    # Word limit is language-agnostic; retry should run.
    assert not _should_bypass_for_language(
        [SOURCE_FAITHFULNESS_FAIL_FLAG, "EXCEEDS_WORD_LIMIT"], "non-en"
    )


def test_compose_retry_instruction_includes_prior_text_and_flags() -> None:
    instruction = _compose_retry_instruction(
        prior_statement="I can describe",
        prior_flags=["EXCEEDS_WORD_LIMIT"],
        attempt_idx=1,
    )
    assert "I can describe" in instruction
    assert "EXCEEDS_WORD_LIMIT" in instruction
    assert f"ATTEMPT 1 of {MAX_REGENERATION_RETRIES}" in instruction


def test_cosine_similarity_detects_near_identical_text() -> None:
    sim = cosine_similarity_text(
        "I can identify prime numbers up to one hundred",
        "I can identify prime numbers up to one hundred",
    )
    assert sim == 1.0
    assert sim >= REGENERATION_NEAR_IDENTICAL_THRESHOLD


def test_cosine_similarity_low_on_different_topics() -> None:
    sim = cosine_similarity_text(
        "I can identify prime numbers",
        "I can evaluate historical sources",
    )
    assert sim < 0.4


def test_annotation_flag_strings_are_stable() -> None:
    # Gate (e) parses these strings; guard against rename.
    assert REGEN_NEAR_IDENTICAL_FLAG == "REGENERATION_NEAR_IDENTICAL"
    assert REGEN_INTRODUCED_NEW_FLAG == "REGENERATION_INTRODUCED_NEW_FLAG"
    assert SOURCE_LANGUAGE_BYPASS_ANNOTATION == "SOURCE_LANGUAGE_BYPASS"
