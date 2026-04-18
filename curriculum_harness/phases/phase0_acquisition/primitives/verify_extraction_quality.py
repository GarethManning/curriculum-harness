"""Statistical verification of extracted-text quality.

Runs deterministic checks on the output of an extraction primitive to
distinguish clean extractions from extractions whose output has been
corrupted by source-PDF pathologies (overlapped footers, interleaved
columns, encoding failures). Does not call any model.

Session 4a-1 shipped an AP CED artefact whose extract primitive reported
``status: "ok"`` while the content was actually half-doubled. This
primitive is the gate that prevents that class of regression: an
extraction that looks fine by byte-count but is structurally corrupt
now fails at the verification step and pauses the pipeline for
user-in-the-loop recovery.

Modes (Session 4a-2b Step 4)
----------------------------

``normalise_whitespace`` collapses horizontal whitespace runs and
triple+ newlines, which destroys the signal ``whitespace_runs`` was
designed to catch. The primitive is therefore run twice in production
sequences:

- ``mode="raw"``      — only ``whitespace_runs``. Inserted between the
  extractor and ``normalise_whitespace``. Primitive name recorded in
  the trace: ``verify_raw_extraction``.
- ``mode="normalised"`` — the other checks (``character_doubling``,
  ``repeated_bigram``, ``empty_line_ratio``, ``completeness``). Runs
  after ``normalise_whitespace``. Primitive name recorded in the
  trace: ``verify_normalised_extraction``.
- ``mode="all"``       — backward-compatible default that runs every
  check in a single pass. Primitive name: ``verify_extraction_quality``.
  Not used by the production sequences but preserved for callers that
  want a single-shot verification on arbitrary content.

Checks
------

1. **character_doubling** (normalised-mode) — per line, fraction of
   consecutive character pairs with identical text (letter/digit/punct;
   whitespace excluded). A line with ratio ≥
   ``doubling_line_threshold`` is flagged. Failure triggers by EITHER
   of:
   (a) flagged fraction of countable lines > ``doubling_doc_threshold``
       (document-wide doubling);
   (b) ≥ ``doubling_systematic_min_count`` flagged lines with mean
       ratio ≥ ``doubling_systematic_mean_ratio`` (systematic
       footer-only doubling repeating across pages).
   Case (b) catches the Session 4a-1 AP CED pattern: only 3 footer
   lines per page are doubled, so the flagged-line fraction is ~8 %,
   but the pattern is clearly systematic and a production-blocker.

2. **repeated_bigram** (normalised-mode) — across the document, count
   character bigrams (letters only, case-folded). If the top-10
   bigrams account for > ``top_bigram_threshold`` of all bigrams
   (typical English ~0.25), flag as suspicious. A ratio >
   ``top_bigram_failure_threshold`` triggers failure.

3. **whitespace_runs** (raw-mode) — count runs of 80+ contiguous
   whitespace characters. More than ``whitespace_run_max`` such runs
   flags; more than ``whitespace_run_max * 10`` fails. Must run
   pre-normalisation — ``normalise_whitespace`` collapses the pattern.

4. **empty_line_ratio** (normalised-mode) — fraction of lines that
   are empty or whitespace-only. A ratio > ``empty_line_threshold``
   indicates structural issue or failed extraction.

Verdicts
--------

- ``clean`` — no check flagged.
- ``suspicious`` — one or more checks flagged but none triggered
  failure. Pipeline continues with a warning recorded.
- ``failed`` — one or more checks triggered failure. Primitive sets
  ``meta["pause_request"]`` with a PauseState so the executor pauses.

All thresholds are constructor arguments with defaults; all threshold
values and per-check results are recorded in ``summary``/``meta`` so
they land in the manifest's verification trace.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
)
from curriculum_harness.phases.phase0_acquisition.session_state import (
    PauseState,
)


_LETTER_RX = re.compile(r"[A-Za-z]")
_WHITESPACE_RUN_RX = re.compile(r"[ \t\n\r\f\v]{80,}")
_WORD_RX = re.compile(r"[A-Za-zÀ-ÿ]+")


# Conservative English stopword list. Presence of these at >=
# ``_ENGLISH_STOPWORD_CONFIDENT_RATIO`` of all alphabetic tokens flags
# the document as high-confidence English. Below the flagged threshold,
# we treat the document as "not confidently English" and downgrade
# bigram FAILURES to `suspicious` — the project has no calibrated
# bigram thresholds for any other language and should not block on a
# threshold with no empirical basis.
_ENGLISH_STOPWORDS = frozenset({
    "the", "and", "of", "to", "in", "a", "is", "that", "for", "it",
    "on", "with", "as", "at", "by", "this", "be", "are", "from", "or",
    "an", "was", "were", "which", "but", "not", "have", "has", "had",
    "they", "their", "these", "those", "been", "will", "would", "can",
    "could", "should", "may", "might", "into", "over", "under", "also",
})
_ENGLISH_STOPWORD_CONFIDENT_RATIO = 0.03


def _detect_english_confidence(text: str) -> tuple[bool, dict[str, Any]]:
    """Conservative English detector.

    Returns ``(is_confident_english, details)``. ``details`` goes into
    the verification trace so the downgrade decision is auditable.

    Deterministic, no model call. The stopword list is intentionally
    small and generic — we only need to distinguish "clearly English"
    from "not clearly English". Calibrated thresholds for other
    languages require real data; see module docstring for rationale.
    """
    words = [w.lower() for w in _WORD_RX.findall(text)]
    total = len(words)
    if total == 0:
        return False, {"total_words": 0, "english_hits": 0, "ratio": 0.0}
    hits = sum(1 for w in words if w in _ENGLISH_STOPWORDS)
    ratio = hits / total
    is_english = ratio >= _ENGLISH_STOPWORD_CONFIDENT_RATIO
    return is_english, {
        "total_words": total,
        "english_hits": hits,
        "ratio": round(ratio, 4),
        "threshold": _ENGLISH_STOPWORD_CONFIDENT_RATIO,
    }


def _doubling_ratio(line: str) -> tuple[float, int]:
    """Return (ratio_of_identical_adjacent_non_ws_pairs, pair_count)."""

    pairs = 0
    doubles = 0
    for i in range(len(line) - 1):
        a, b = line[i], line[i + 1]
        if a.isspace() or b.isspace():
            continue
        pairs += 1
        if a == b:
            doubles += 1
    if pairs == 0:
        return 0.0, 0
    return doubles / pairs, pairs


def _top_bigram_share(text: str, top_n: int = 10) -> tuple[float, int, list]:
    """Share of letter bigrams accounted for by the top-N most frequent.

    Returns (share, total_bigrams, top_bigrams_list).
    """
    letters = [c.lower() for c in text if _LETTER_RX.match(c)]
    if len(letters) < 2:
        return 0.0, 0, []
    bigrams = Counter(
        "".join(letters[i : i + 2]) for i in range(len(letters) - 1)
    )
    total = sum(bigrams.values())
    if total == 0:
        return 0.0, 0, []
    top = bigrams.most_common(top_n)
    share = sum(v for _, v in top) / total
    return share, total, top


_MODE_NAMES = {
    "all": "verify_extraction_quality",
    "raw": "verify_raw_extraction",
    "normalised": "verify_normalised_extraction",
}

_RAW_CHECKS = frozenset({"whitespace_runs"})
_NORMALISED_CHECKS = frozenset(
    {"character_doubling", "repeated_bigram", "empty_line_ratio", "completeness"}
)


def _completeness_check(
    text: str, source_metrics: dict[str, Any]
) -> dict[str, Any] | None:
    """Compare extracted volume against a plausible expected range.

    Returns a check entry, or ``None`` if no source metadata is
    available to compute an expected range (in which case the check is
    recorded in the verification trace as skipped by the caller).

    HTML: expected chars scale with fetched byte count. Below 5 %
    flagged, below 2 % failed. PDF: expected chars scale with pages
    extracted, at 200 chars/page minimum; below 50 chars/page flagged,
    below 20 chars/page failed.
    """

    chars = len(text)
    pages = source_metrics.get("pages_extracted_count")
    if pages is not None and pages > 0:
        per_page = chars / pages
        check = {
            "name": "completeness",
            "source_kind": "pdf",
            "value": round(per_page, 1),
            "threshold": 50,
            "chars_total": chars,
            "pages_extracted_count": pages,
        }
        check["passed"] = per_page >= 20
        check["flagged"] = per_page < 50
        return check
    fetched_bytes = source_metrics.get("fetched_bytes")
    if fetched_bytes is not None and fetched_bytes > 0:
        ratio = chars / fetched_bytes
        check = {
            "name": "completeness",
            "source_kind": "html",
            "value": round(ratio, 4),
            "threshold": 0.05,
            "chars_total": chars,
            "fetched_bytes": fetched_bytes,
        }
        check["passed"] = ratio >= 0.02
        check["flagged"] = ratio < 0.05
        return check
    return None


class VerifyExtractionQualityPrimitive:
    """Gate extraction output on statistical quality checks.

    Output: passes the input text through unchanged. Summary records
    the verdict, check results, and sample failures. On verdict
    ``failed``, ``meta["pause_request"]`` is populated so the executor
    raises ``Phase0Paused``.

    ``mode`` selects which checks run (see module docstring). The
    primitive's recorded ``name`` tracks the mode so the verification
    trace distinguishes pre- and post-normalisation entries.
    """

    required_scope_fields: tuple[str, ...] = ()
    optional_scope_fields: tuple[str, ...] = ()
    side_effects: frozenset[str] = frozenset()

    def __init__(
        self,
        *,
        mode: str = "all",
        doubling_line_threshold: float = 0.3,
        doubling_doc_threshold: float = 0.2,
        doubling_systematic_min_count: int = 5,
        doubling_systematic_mean_ratio: float = 0.4,
        top_bigram_threshold: float = 0.6,
        top_bigram_failure_threshold: float = 0.75,
        whitespace_run_max: int = 5,
        empty_line_threshold: float = 0.4,
        sample_limit: int = 5,
        output_dir: str | None = None,
    ) -> None:
        if mode not in _MODE_NAMES:
            raise ValueError(
                f"mode must be one of {list(_MODE_NAMES)}, got {mode!r}"
            )
        self.mode = mode
        self.name = _MODE_NAMES[mode]
        self.doubling_line_threshold = doubling_line_threshold
        self.doubling_doc_threshold = doubling_doc_threshold
        self.doubling_systematic_min_count = doubling_systematic_min_count
        self.doubling_systematic_mean_ratio = doubling_systematic_mean_ratio
        self.top_bigram_threshold = top_bigram_threshold
        self.top_bigram_failure_threshold = top_bigram_failure_threshold
        self.whitespace_run_max = whitespace_run_max
        self.empty_line_threshold = empty_line_threshold
        self.sample_limit = sample_limit
        self.output_dir = output_dir

    def _runs_check(self, check_name: str) -> bool:
        if self.mode == "all":
            return True
        if self.mode == "raw":
            return check_name in _RAW_CHECKS
        return check_name in _NORMALISED_CHECKS

    def validate_scope(self, scope) -> None:
        return None

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        text = "" if previous is None else str(previous.output or "")
        lines = text.splitlines()

        checks: list[dict[str, Any]] = []
        flagged_lines: list[dict[str, Any]] = []

        if self._runs_check("character_doubling"):
            countable_lines = 0
            for i, line in enumerate(lines):
                ratio, pair_count = _doubling_ratio(line)
                if pair_count < 10:
                    continue
                countable_lines += 1
                if ratio >= self.doubling_line_threshold:
                    flagged_lines.append(
                        {
                            "line_index": i,
                            "ratio": round(ratio, 3),
                            "pair_count": pair_count,
                            "preview": line[:120],
                        }
                    )
            doubling_fraction = (
                len(flagged_lines) / countable_lines if countable_lines else 0.0
            )
            doubling_flagged = len(flagged_lines) > 0
            doubling_failed_docwide = (
                doubling_fraction > self.doubling_doc_threshold
            )
            mean_flagged_ratio = (
                sum(ln["ratio"] for ln in flagged_lines) / len(flagged_lines)
                if flagged_lines
                else 0.0
            )
            doubling_failed_systematic = (
                len(flagged_lines) >= self.doubling_systematic_min_count
                and mean_flagged_ratio >= self.doubling_systematic_mean_ratio
            )
            doubling_failed = doubling_failed_docwide or doubling_failed_systematic
            checks.append(
                {
                    "name": "character_doubling",
                    "value": round(doubling_fraction, 3),
                    "threshold": self.doubling_doc_threshold,
                    "passed": not doubling_failed,
                    "flagged": doubling_flagged,
                    "lines_flagged": len(flagged_lines),
                    "countable_lines": countable_lines,
                    "mean_flagged_ratio": round(mean_flagged_ratio, 3),
                    "systematic_failure": doubling_failed_systematic,
                    "docwide_failure": doubling_failed_docwide,
                }
            )

        if self._runs_check("repeated_bigram"):
            share, bigram_total, top = _top_bigram_share(text, top_n=10)
            is_english, lang_details = _detect_english_confidence(text)
            bigram_hard_failed = share > self.top_bigram_failure_threshold
            bigram_flagged = share > self.top_bigram_threshold
            # Conservative language-aware calibration (Step 5): only
            # English has calibrated thresholds. For non-English or
            # low-confidence text, downgrade a failure to `suspicious`
            # so the finding is surfaced but does not block extraction
            # on a threshold with no empirical basis for the language.
            downgraded = False
            if bigram_hard_failed and not is_english:
                bigram_failed = False
                downgraded = True
            else:
                bigram_failed = bigram_hard_failed
            bigram_check = {
                "name": "repeated_bigram",
                "value": round(share, 3),
                "threshold": self.top_bigram_failure_threshold,
                "passed": not bigram_failed,
                "flagged": bigram_flagged,
                "top_bigrams": [(b, c) for b, c in top[:5]],
                "total_bigrams": bigram_total,
                "language_detected": (
                    "english_confident" if is_english else "non_english_or_unknown"
                ),
                "language_details": lang_details,
            }
            if downgraded:
                bigram_check["downgraded_from_failed"] = True
                bigram_check["downgrade_reason"] = (
                    "bigram_failure_downgraded_due_to_non_english_content"
                )
            checks.append(bigram_check)

        if self._runs_check("whitespace_runs"):
            ws_runs = _WHITESPACE_RUN_RX.findall(text)
            ws_run_count = len(ws_runs)
            ws_failed = ws_run_count > self.whitespace_run_max * 10
            ws_flagged = ws_run_count > self.whitespace_run_max
            checks.append(
                {
                    "name": "whitespace_runs",
                    "value": ws_run_count,
                    "threshold": self.whitespace_run_max * 10,
                    "passed": not ws_failed,
                    "flagged": ws_flagged,
                }
            )

        if self._runs_check("empty_line_ratio"):
            if lines:
                empty_lines = sum(1 for ln in lines if not ln.strip())
                empty_fraction = empty_lines / len(lines)
            else:
                empty_fraction = 0.0
            empty_failed = empty_fraction > (self.empty_line_threshold + 0.2)
            empty_flagged = empty_fraction > self.empty_line_threshold
            checks.append(
                {
                    "name": "empty_line_ratio",
                    "value": round(empty_fraction, 3),
                    "threshold": self.empty_line_threshold + 0.2,
                    "passed": not empty_failed,
                    "flagged": empty_flagged,
                }
            )

        completeness_skipped_reason: str | None = None
        if self._runs_check("completeness"):
            src_metrics = (
                (previous.meta or {}).get("_source_metrics", {})
                if previous is not None
                else {}
            )
            c = _completeness_check(text, src_metrics)
            if c is not None:
                checks.append(c)
            else:
                completeness_skipped_reason = (
                    "no source metadata (fetched_bytes or "
                    "pages_extracted) available in executor accumulator"
                )

        any_failed = any(not c["passed"] for c in checks)
        any_flagged = any(c.get("flagged") for c in checks)

        if any_failed:
            verdict = "failed"
        elif any_flagged:
            verdict = "suspicious"
        else:
            verdict = "clean"

        sample_failures = flagged_lines[: self.sample_limit]

        summary: dict[str, Any] = {
            "verdict": verdict,
            "mode": self.mode,
            "checks": checks,
            "chars_in": len(text),
            "line_count": len(lines),
        }
        if completeness_skipped_reason:
            summary["completeness_skipped_reason"] = completeness_skipped_reason
        if sample_failures:
            summary["sample_failures"] = sample_failures
        meta: dict[str, Any] = {
            "verification": {
                "verdict": verdict,
                "mode": self.mode,
                "checks": checks,
                "sample_failures": sample_failures,
                "completeness_skipped_reason": completeness_skipped_reason,
            }
        }

        if verdict == "failed":
            # Recommend recovery action
            failed_names = [c["name"] for c in checks if not c["passed"]]
            recovery = _recommend_recovery(failed_names)

            pause_dir = (
                Path(self.output_dir) / "_paused"
                if self.output_dir
                else Path("_paused")
            )
            meta["pause_request"] = PauseState(
                primitive=self.name,
                reason="extraction_quality_failed",
                needed=_render_pause_needed(
                    verdict, checks, sample_failures, recovery
                ),
                expected_format="scope_fields",
                resume_hint=(
                    "Review the failing checks, update the scope spec as "
                    "recommended, and re-run Phase 0. For PDFs with "
                    "overlaid-footer doubling, set "
                    "`pdf_dedup_coords: true` in the scope."
                ),
                state_dir=str(pause_dir),
                source_reference=getattr(scope, "source_reference", ""),
                extra={
                    "failed_checks": failed_names,
                    "recommended_recovery": recovery,
                    "verdict": verdict,
                },
            )

        return PrimitiveResult(output=text, summary=summary, meta=meta)


def _recommend_recovery(failed_checks: list[str]) -> dict[str, Any]:
    """Map failed-check names to recommended scope-level remediation."""
    if "character_doubling" in failed_checks:
        return {
            "action": "set_pdf_dedup_coords",
            "scope_fields": {"pdf_dedup_coords": True},
            "rationale": (
                "Character-doubling detected — re-run with the "
                "coordinate-deduplicating extraction primitive."
            ),
        }
    if "repeated_bigram" in failed_checks:
        return {
            "action": "inspect_content_manually",
            "scope_fields": {},
            "rationale": (
                "Abnormal bigram distribution. Inspect content.txt to "
                "determine whether the extraction is corrupt or the "
                "source has unusual character frequency."
            ),
        }
    return {
        "action": "inspect_content_manually",
        "scope_fields": {},
        "rationale": (
            "Extraction-quality failure surfaced. Inspect the manifest's "
            "verification_trace and the content file to diagnose."
        ),
    }


def _render_pause_needed(
    verdict: str,
    checks: list,
    sample_failures: list,
    recovery: dict,
) -> str:
    lines = [
        "Extraction-quality verification returned verdict "
        f"`{verdict}`. The following checks failed:",
        "",
    ]
    for c in checks:
        if c.get("passed"):
            continue
        lines.append(
            f"- **{c['name']}**: value={c['value']}, "
            f"threshold={c['threshold']}"
        )
    lines.append("")
    if sample_failures:
        lines.append("Sample failing lines:")
        lines.append("")
        for s in sample_failures[:3]:
            lines.append(f"  - line {s['line_index']}: `{s['preview']}`")
        lines.append("")
    lines.append("**Recommended recovery:**")
    lines.append(f"- action: `{recovery.get('action')}`")
    fields = recovery.get("scope_fields") or {}
    if fields:
        lines.append(f"- scope fields to set: `{fields}`")
    lines.append(f"- rationale: {recovery.get('rationale')}")
    return "\n".join(lines)
