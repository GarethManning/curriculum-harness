"""Adversarial tests for ``verify_extraction_quality``.

Empirical proof that the verifier fails correctly on broken extractions.
Each test feeds a constructed-bad input to the primitive and asserts the
expected verdict plus the specific failing check. If any of these
assertions regress, the verifier's thresholds are misconfigured.

Test corpus:

- ``test_ap_ced_original_content_fails_character_doubling`` — real
  failure from Session 4a-1: AP US Gov CED extracted without
  coordinate-level dedup. Systematic footer-only doubling that would
  fall below a document-wide ratio threshold but must still fail via
  the systematic-failure branch. Content hash is pinned so the test
  cannot drift onto the post-fix version.
- ``test_whitespace_runs_synthetic_failure`` — many 80+ character
  whitespace runs. Must fail on ``whitespace_runs``.
- ``test_empty_lines_synthetic_failure`` — mostly-empty document. Must
  fail on ``empty_line_ratio``.
- ``test_bigram_synthetic_failure`` — one word repeated many times.
  Must fail on ``repeated_bigram``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
)
from curriculum_harness.phases.phase0_acquisition.primitives.verify_extraction_quality import (
    VerifyExtractionQualityPrimitive,
)


AP_4A1_SNAPSHOT = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "run-snapshots"
    / "2026-04-18-session-4a-1-phase0-test-ap-usgov"
    / "content.txt"
)

# Hash pinned from the Session 4a-1 snapshot (pre-fix, doubled content).
# If this hash does not match, the test has been pointed at the wrong
# file — stop and investigate before accepting the test as passing.
AP_4A1_CONTENT_HASH = (
    "47d41e8bc6031c9bc91decaa0be5b65f11357452022202d26d662ef0bea7215a"
)


def _run_verifier(
    text: str, *, source_metrics: dict | None = None, **kwargs
) -> PrimitiveResult:
    prim = VerifyExtractionQualityPrimitive(**kwargs)

    class _Scope:
        source_reference = "test"

    previous = PrimitiveResult(output=text)
    if source_metrics is not None:
        previous.meta["_source_metrics"] = source_metrics
    return prim.run(_Scope(), previous)


def _check_by_name(checks: list[dict], name: str) -> dict:
    for c in checks:
        if c.get("name") == name:
            return c
    raise AssertionError(f"check {name!r} not present in verifier output")


def test_ap_ced_original_content_fails_character_doubling() -> None:
    assert AP_4A1_SNAPSHOT.exists(), (
        f"Session 4a-1 snapshot not found at {AP_4A1_SNAPSHOT}; "
        "this test depends on the pre-fix AP CED content being present."
    )
    data = AP_4A1_SNAPSHOT.read_bytes()
    actual_hash = hashlib.sha256(data).hexdigest()
    assert actual_hash == AP_4A1_CONTENT_HASH, (
        "AP 4a-1 content hash mismatch — expected "
        f"{AP_4A1_CONTENT_HASH}, got {actual_hash}. Do not proceed; the "
        "file may have been overwritten with post-fix content."
    )

    text = data.decode("utf-8")
    result = _run_verifier(text)

    assert result.summary["verdict"] == "failed", (
        "AP CED original content (doubled) must verdict 'failed'"
    )

    cd = _check_by_name(result.summary["checks"], "character_doubling")
    assert cd["passed"] is False, "character_doubling must fail on AP original"
    assert cd["systematic_failure"] is True, (
        "AP CED doubling is systematic (footer-only across pages); the "
        "systematic-failure branch is the gate that catches it"
    )


def test_whitespace_runs_synthetic_failure_raw_mode() -> None:
    # Runs the raw-mode verifier (the mode that production sequences use
    # pre-normalise-whitespace) against a document with many 80-char
    # whitespace runs. Step 4 confirmed empirically that the post-
    # normalise verifier cannot see this pattern, so this case asserts
    # the raw-mode primitive catches it.
    block = " " * 80
    real_line = "The quick brown fox jumps over the lazy dog. "
    parts = []
    for _ in range(60):
        parts.append(real_line)
        parts.append(block)
        parts.append("\n")
    text = "".join(parts)

    result = _run_verifier(text, mode="raw")

    assert result.summary["verdict"] == "failed"
    ws = _check_by_name(result.summary["checks"], "whitespace_runs")
    assert ws["passed"] is False, "whitespace_runs must fail on 60 runs"


def test_empty_lines_synthetic_failure() -> None:
    content_lines = [
        f"Content line {i}: The quick brown fox jumps over the lazy dog."
        for i in range(50)
    ]
    empty_lines = [""] * 500
    text = "\n".join(content_lines + empty_lines)

    result = _run_verifier(text)

    assert result.summary["verdict"] == "failed"
    el = _check_by_name(result.summary["checks"], "empty_line_ratio")
    assert el["passed"] is False, (
        "empty_line_ratio must fail when > 60 % of lines are empty"
    )


def test_whitespace_runs_dead_after_normalisation() -> None:
    """Step 4 empirical result: ``normalise_whitespace`` collapses the
    pattern ``whitespace_runs`` is designed to detect. The
    ``normalised``-mode verifier therefore must not include the check,
    and post-normalise text feeding the default ("all") mode must
    report zero whitespace runs. This test is the regression guard
    against re-merging the whitespace check into the post-normalise
    verifier in a future refactor.
    """
    from curriculum_harness.phases.phase0_acquisition.primitives.normalise_whitespace import (
        normalise_text,
    )

    block = " " * 80
    parts = ["Line. " + block + "\n" for _ in range(60)]
    raw = "".join(parts)

    # Raw mode on the raw text: catches it.
    raw_result = _run_verifier(raw, mode="raw")
    assert raw_result.summary["verdict"] == "failed"

    # Normalised mode on the normalised text: passes (cannot see it).
    normalised = normalise_text(raw)
    norm_result = _run_verifier(normalised, mode="normalised")
    check_names = [c["name"] for c in norm_result.summary["checks"]]
    assert "whitespace_runs" not in check_names, (
        "whitespace_runs must not run in normalised mode — the signal "
        "has been collapsed upstream and the check would be a false "
        "reassurance"
    )


def test_bigram_synthetic_failure() -> None:
    # "the the the ..." 5000 times. The bigram check case-folds and
    # considers letter-only bigrams, so the repeated stream yields three
    # distinct bigrams (th, he, et) sharing ~100 % of the total — well
    # above top_bigram_failure_threshold (0.75).
    text = ("the " * 5000).strip()

    result = _run_verifier(text)

    assert result.summary["verdict"] == "failed"
    bg = _check_by_name(result.summary["checks"], "repeated_bigram")
    assert bg["passed"] is False, (
        "repeated_bigram must fail when a single word dominates the "
        "bigram distribution"
    )


def test_completeness_synthetic_html_extraction_too_thin() -> None:
    # Construct the "extracted 20 chars out of a 10 KB HTML fetch" case.
    # Under an expected-ratio threshold of 5 % flagged / 2 % failed on
    # HTML sources, 20 chars ÷ 10,000 bytes = 0.2 % → failure.
    text = "Unit 1 intro only."
    src_metrics = {"fetched_bytes": 10_000}

    result = _run_verifier(text, source_metrics=src_metrics, mode="normalised")

    assert result.summary["verdict"] == "failed"
    c = _check_by_name(result.summary["checks"], "completeness")
    assert c["passed"] is False
    assert c["source_kind"] == "html"


def test_completeness_pdf_thin_extraction_fails() -> None:
    # 10 chars extracted from a 20-page PDF = 0.5 chars/page, far below
    # the 20-char/page failure threshold.
    text = "Unit 1    "
    src_metrics = {
        "pages_extracted_count": 20,
        "pages_extracted": [1, 20],
    }

    result = _run_verifier(text, source_metrics=src_metrics, mode="normalised")

    assert result.summary["verdict"] == "failed"
    c = _check_by_name(result.summary["checks"], "completeness")
    assert c["passed"] is False
    assert c["source_kind"] == "pdf"


def test_completeness_skipped_when_no_source_metadata() -> None:
    result = _run_verifier("Plenty of text here." * 50, mode="normalised")
    names = [c["name"] for c in result.summary["checks"]]
    assert "completeness" not in names
    assert result.summary.get("completeness_skipped_reason"), (
        "skip must be recorded in the verification trace"
    )


def test_bigram_non_english_failure_is_downgraded_to_suspicious() -> None:
    # Hungarian synthetic text that trips the bigram threshold without
    # triggering the English-stopword detector. "ő" repeated with
    # a few filler accented characters gives a very skewed bigram
    # distribution but contains no English stopwords. Expected: the
    # verifier records a failing raw bigram measure but downgrades the
    # verdict so the pipeline is not blocked on a threshold with no
    # Hungarian calibration.
    text = "árvíztűrő ő ő ő ő " * 5000

    result = _run_verifier(text)

    bg = _check_by_name(result.summary["checks"], "repeated_bigram")
    # Raw signal still fails the threshold.
    assert bg["value"] > 0.75
    # But the verdict is not 'failed' — the downgrade kicks in.
    assert result.summary["verdict"] in {"suspicious", "clean"}, (
        "non-English bigram failure must not produce verdict 'failed'"
    )
    assert bg.get("downgraded_from_failed") is True, (
        "the bigram check entry must record the downgrade for audit"
    )
    assert bg["language_detected"] == "non_english_or_unknown"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
