"""Coordinate-deduplicating PDF-text extraction primitive.

Variant of ``extract_pdf_text`` for PDFs where the source renders text
twice at identical (x0, top) coordinates — e.g. running headers/footers
stamped on top of themselves. Default pdfplumber behaviour emits every
character in the char stream, so overlaid-identical text extracts as
``"RR"`` ``"ee"`` ``"tt"`` etc.

Mechanism identified in Session 4a-2a (see
`docs/diagnostics/2026-04-18-ap-ced-doubling-investigation.md`):
Mechanism B — coordinate-level overlapping text.

Algorithm
---------

For each page in scope:

1. Read ``page.chars`` (raw character list with positions).
2. Group characters by ``(round(x0/tol)*tol, round(top/tol)*tol, text)``.
3. Keep one representative per group.
4. Reassemble text per page: group unique chars by rounded ``top``
   (one pixel precision); sort each line's chars by ``x0``; join lines
   by ``"\\n"``. This reproduces the natural reading order for
   single-column pages and is a deliberate approximation for
   multi-column pages (see caveats).

Side-effect tag: none (pure computation over bytes in memory).
Deterministic — no model calls.

Scope handling matches ``extract_pdf_text``: ``page_range`` wins over
``section_heading``; heading is recorded as verification-only when both
are supplied. The dedup tolerance is exposed as the
``pdf_dedup_coord_tolerance`` scope field (default 1 pixel) and
recorded in the acquisition trace.

Caveats
-------

Multi-column PDFs: the line-assembly step groups chars by ``round(top)``,
which for two-column layouts produces line-by-line interleaving (left
column line 1, right column line 1, left line 2, …). This is the same
trade-off ``extract_pdf_text`` accepts; the deduped primitive doesn't
regress it.

Non-standard whitespace: pdfplumber's ``extract_text`` infers
between-word spaces from ``x0`` gaps. This primitive inserts a single
space between chars whenever the gap between consecutive chars on a line
exceeds ``space_gap_tolerance`` (default 1.5× the trailing char's
width). For most CEDs and curriculum docs this matches pdfplumber's
output; docs with unusual spacing may need the tolerance tuned.
"""

from __future__ import annotations

import io
import logging
import re
from collections import defaultdict
from typing import Any

import pdfplumber

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
)


_HEADING_LINE_CHARS = 80
_DEFAULT_COORD_TOL = 1
_DEFAULT_SPACE_GAP_FACTOR = 1.5


def _parse_page_range(value: Any) -> tuple[int, int] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)) and len(value) == 2:
        start, end = int(value[0]), int(value[1])
    elif isinstance(value, str):
        m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", value)
        if not m:
            return None
        start, end = int(m.group(1)), int(m.group(2))
    else:
        return None
    if start < 1 or end < start:
        return None
    return start, end


def _quantise(value: float, tol: int) -> int:
    if tol <= 0:
        tol = 1
    return int(round(float(value) / tol) * tol)


def _dedup_chars_on_page(chars: list, coord_tol: int) -> tuple[list, int]:
    """Return (unique_chars_in_stream_order, removed_count).

    Preserves the first occurrence of each (qx, qy, text) triple. Other
    occurrences are discarded.
    """
    seen: set = set()
    kept: list = []
    removed = 0
    for c in chars:
        try:
            qx = _quantise(c["x0"], coord_tol)
            qy = _quantise(c["top"], coord_tol)
        except (KeyError, TypeError, ValueError):
            kept.append(c)
            continue
        key = (qx, qy, c["text"])
        if key in seen:
            removed += 1
            continue
        seen.add(key)
        kept.append(c)
    return kept, removed


def _assemble_text_from_chars(chars: list, space_gap_factor: float) -> str:
    """Reassemble text from a list of pdfplumber char dicts.

    Lines are formed by ``round(top)``; chars sorted by ``x0`` within a
    line. A space is inserted between consecutive chars when the gap
    exceeds ``space_gap_factor × char_width``. Lines joined with ``\\n``.
    """
    if not chars:
        return ""
    by_line: dict = defaultdict(list)
    for c in chars:
        try:
            top_key = int(round(float(c["top"])))
        except (KeyError, TypeError, ValueError):
            continue
        by_line[top_key].append(c)

    lines: list[str] = []
    for top_key in sorted(by_line.keys()):
        row = sorted(by_line[top_key], key=lambda c: float(c.get("x0", 0)))
        out_chars: list[str] = []
        prev_x1: float | None = None
        prev_width: float | None = None
        for c in row:
            x0 = float(c.get("x0", 0))
            width = float(c.get("width", 0)) or 1.0
            if prev_x1 is not None:
                gap = x0 - prev_x1
                # insert a space only if the preceding token isn't already
                # a whitespace char and the gap exceeds the tolerance.
                if gap > (prev_width or width) * space_gap_factor and out_chars and not out_chars[-1].isspace():
                    out_chars.append(" ")
            out_chars.append(c.get("text", ""))
            prev_x1 = x0 + width
            prev_width = width
        lines.append("".join(out_chars))
    return "\n".join(lines)


def _slice_by_page_range(
    page_texts: list[str], start_1idx: int, end_1idx: int
) -> tuple[str, tuple[int, int]]:
    n = len(page_texts)
    start = max(1, start_1idx)
    end = min(n, end_1idx)
    if start > n:
        return "", (start, end)
    slice_texts = page_texts[start - 1 : end]
    return "\n\n".join(slice_texts), (start, end)


_NUMBERING_PREFIX_RX = re.compile(r"^(\d+(?:\.\d+)*)\b")


def _leading_heading_token(line: str) -> str:
    s = line.strip()
    if not s:
        return ""
    m = _NUMBERING_PREFIX_RX.match(s)
    if m:
        return f"numbered:{m.group(1).count('.')}"
    if s == s.upper() and len(s.split()) <= 8:
        return "allcaps"
    return "other"


def _slice_by_heading(
    page_texts: list[str],
    heading: str,
    is_regex: bool,
) -> tuple[str, dict[str, Any]]:
    full = "\n\n".join(page_texts)
    lines = full.splitlines()
    heading_idx: int | None = None
    pattern = re.compile(heading) if is_regex else None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or len(s) > _HEADING_LINE_CHARS:
            continue
        if pattern is not None:
            if pattern.search(s):
                heading_idx = i
                break
        else:
            if heading.lower() in s.lower():
                heading_idx = i
                break

    if heading_idx is None:
        return "", {"heading_found": False, "heading_line": None}

    next_idx = len(lines)
    target_prefix_token = _leading_heading_token(lines[heading_idx])
    for j in range(heading_idx + 1, len(lines)):
        s = lines[j].strip()
        if not s or len(s) > _HEADING_LINE_CHARS:
            continue
        if (
            _leading_heading_token(lines[j]) == target_prefix_token
            and s != lines[heading_idx].strip()
        ):
            next_idx = j
            break

    snippet_lines = lines[heading_idx:next_idx]
    return "\n".join(snippet_lines).strip(), {
        "heading_found": True,
        "heading_line": lines[heading_idx].strip(),
        "heading_line_index": heading_idx,
        "next_heading_line_index": next_idx,
    }


class _ListLoggingHandler(logging.Handler):
    def __init__(self, bucket: list[str]) -> None:
        super().__init__()
        self.bucket = bucket

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.bucket.append(self.format(record))
        except Exception:  # noqa: BLE001
            return


class ExtractPdfTextDedupedPrimitive:
    """Extract text from PDF bytes with coordinate-level char dedup.

    Scope:
        - ``page_range`` (optional)
        - ``section_heading`` (optional)
        - ``heading_regex`` (optional flag)
        - ``pdf_dedup_coord_tolerance`` (optional int, default 1) —
          coordinate rounding precision in pixels used to group
          duplicate characters.

    Output: UTF-8 text string. ``summary`` records per-page dedup
    counts and the coord tolerance actually used.
    """

    name = "extract_pdf_text_deduped"
    required_scope_fields: tuple[str, ...] = ()
    optional_scope_fields: tuple[str, ...] = (
        "page_range",
        "section_heading",
        "heading_regex",
        "pdf_dedup_coord_tolerance",
    )
    side_effects: frozenset[str] = frozenset()

    def validate_scope(self, scope) -> None:
        return None

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        if previous is None or previous.output is None:
            return PrimitiveResult(
                output="",
                summary={"status": "no_input"},
                meta={"extract_failure": "no_input"},
            )
        raw = previous.output
        if not isinstance(raw, (bytes, bytearray)):
            return PrimitiveResult(
                output="",
                summary={"status": "input_not_bytes"},
                meta={"extract_failure": "input_not_bytes"},
            )

        resolved_range = (previous.meta or {}).get("resolved_page_range")
        page_range = (
            _parse_page_range(resolved_range)
            if resolved_range is not None
            else _parse_page_range(getattr(scope, "page_range", None))
        )
        section_heading = getattr(scope, "section_heading", None)
        is_regex = bool(getattr(scope, "heading_regex", False))
        coord_tol_raw = getattr(scope, "pdf_dedup_coord_tolerance", None)
        coord_tol = (
            int(coord_tol_raw) if coord_tol_raw is not None else _DEFAULT_COORD_TOL
        )

        warnings: list[str] = []
        handler = _ListLoggingHandler(warnings)
        pdf_logger = logging.getLogger("pdfminer")
        pdf_logger.addHandler(handler)
        previous_level = pdf_logger.level
        pdf_logger.setLevel(logging.WARNING)

        summary: dict[str, Any] = {
            "status": "ok",
            "pdfplumber_version": pdfplumber.__version__,
            "coord_tolerance": coord_tol,
        }
        meta: dict[str, Any] = {}
        try:
            with pdfplumber.open(io.BytesIO(bytes(raw))) as pdf:
                total_pages = len(pdf.pages)
                summary["source_page_count"] = total_pages

                per_page_dedup_counts: list[dict[str, int]] = []
                page_texts: list[str] = []
                for page in pdf.pages:
                    try:
                        chars = page.chars or []
                        before = len(chars)
                        uniq, removed = _dedup_chars_on_page(chars, coord_tol)
                        page_text = _assemble_text_from_chars(
                            uniq, _DEFAULT_SPACE_GAP_FACTOR
                        )
                        page_texts.append(page_text)
                        per_page_dedup_counts.append(
                            {
                                "page": page.page_number,
                                "chars_before": before,
                                "chars_after": before - removed,
                                "chars_removed": removed,
                            }
                        )
                    except Exception as exc:  # noqa: BLE001 — per-page
                        page_texts.append(
                            f"[pdfplumber extraction error on page: {exc}]"
                        )
                        per_page_dedup_counts.append(
                            {
                                "page": page.page_number,
                                "chars_before": 0,
                                "chars_after": 0,
                                "chars_removed": 0,
                                "error": str(exc),
                            }
                        )

                heading_verification: dict[str, Any] | None = None
                extracted_pages: tuple[int, int] | None = None
                extraction_mode: str

                if page_range is not None:
                    text, extracted_pages = _slice_by_page_range(
                        page_texts, page_range[0], page_range[1]
                    )
                    extraction_mode = "page_range"
                    if section_heading:
                        _, hv = _slice_by_heading(
                            page_texts[extracted_pages[0] - 1 : extracted_pages[1]],
                            section_heading,
                            is_regex,
                        )
                        heading_verification = hv
                elif section_heading:
                    text, hv = _slice_by_heading(
                        page_texts, section_heading, is_regex
                    )
                    heading_verification = hv
                    extraction_mode = "section_heading"
                    extracted_pages = (1, total_pages) if text else None
                    if not text:
                        summary["status"] = "heading_not_found"
                else:
                    text = "\n\n".join(page_texts)
                    extraction_mode = "full_document"
                    extracted_pages = (1, total_pages) if total_pages else None

                summary["extraction_mode"] = extraction_mode
                if extracted_pages:
                    summary["pages_extracted"] = list(extracted_pages)
                if heading_verification is not None:
                    summary["heading_verification"] = heading_verification
                summary["chars_out"] = len(text)

                # Dedup totals across the pages actually emitted
                if extracted_pages:
                    pg_slice = per_page_dedup_counts[
                        extracted_pages[0] - 1 : extracted_pages[1]
                    ]
                else:
                    pg_slice = per_page_dedup_counts
                summary["chars_removed_total"] = sum(
                    p.get("chars_removed", 0) for p in pg_slice
                )
                summary["chars_before_total"] = sum(
                    p.get("chars_before", 0) for p in pg_slice
                )
                meta["per_page_dedup_counts"] = pg_slice

                if warnings:
                    summary["pdfplumber_warnings"] = warnings[:5]
                    meta["pdfplumber_warnings"] = warnings

                return PrimitiveResult(output=text, summary=summary, meta=meta)
        except Exception as exc:  # noqa: BLE001
            return PrimitiveResult(
                output="",
                summary={"status": "pdfplumber_open_failed", "error": str(exc)},
                meta={"extract_failure": f"pdfplumber_open_failed: {exc}"},
            )
        finally:
            pdf_logger.removeHandler(handler)
            pdf_logger.setLevel(previous_level)
