"""PDF-text extraction primitive (pdfplumber backend).

Takes raw PDF bytes from the previous primitive and returns UTF-8 text.
Scope-capable from day one: optional ``page_range`` and
``section_heading`` parameters constrain extraction; full-document
extraction is the default when neither is supplied.

Side-effect tag: none (pure computation over bytes in memory).

Deterministic — no model calls. pdfplumber performs the layout analysis
and text extraction; this primitive is a thin wrapper that records
provenance in ``summary``/``meta``.

## Scope handling

- ``page_range`` (``[start, end]``, 1-indexed inclusive, or legacy
  ``"start-end"`` string): extract only those pages.
- ``section_heading`` (literal or regex; ``heading_regex`` toggles
  interpretation): locate the heading in the document text and extract
  from that heading to the next same-or-higher heading, or to end of
  document if no later heading found.
- If both are supplied, ``page_range`` wins; ``section_heading`` is
  recorded as verification-only (was the heading found within the
  requested pages?) in the primitive trace.
- If neither is supplied, extract the entire document.
"""

from __future__ import annotations

import io
import logging
import re
from typing import Any

import pdfplumber

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
)


_HEADING_LINE_CHARS = 80


def _parse_page_range(value: Any) -> tuple[int, int] | None:
    """Return ``(start, end)`` 1-indexed inclusive, or ``None``."""

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


def _extract_page_texts(pdf: pdfplumber.PDF) -> list[str]:
    """Per-page text list. Swallow per-page failures to a marker line."""

    texts: list[str] = []
    for page in pdf.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception as exc:  # noqa: BLE001 — per-page fallibility expected
            texts.append(f"[pdfplumber extraction error on page: {exc}]")
    return texts


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


def _slice_by_heading(
    page_texts: list[str],
    heading: str,
    is_regex: bool,
) -> tuple[str, dict[str, Any]]:
    """Extract from the heading line to the next same-level heading.

    Same-level heuristic: the next line anywhere in the document whose
    stripped text starts with the same leading token type as the target
    heading (same leading numbering prefix, or another all-caps short
    line when the target heading is all-caps). Failing a heuristic
    match, extract from the heading to end of document.
    """

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
        return "", {
            "heading_found": False,
            "heading_line": None,
        }

    next_idx = len(lines)
    target_prefix_token = _leading_heading_token(lines[heading_idx])
    for j in range(heading_idx + 1, len(lines)):
        s = lines[j].strip()
        if not s or len(s) > _HEADING_LINE_CHARS:
            continue
        if _leading_heading_token(lines[j]) == target_prefix_token and s != lines[heading_idx].strip():
            next_idx = j
            break

    snippet_lines = lines[heading_idx:next_idx]
    return "\n".join(snippet_lines).strip(), {
        "heading_found": True,
        "heading_line": lines[heading_idx].strip(),
        "heading_line_index": heading_idx,
        "next_heading_line_index": next_idx,
    }


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


class ExtractPdfTextPrimitive:
    """Extract UTF-8 text from PDF bytes using pdfplumber.

    Scope:
        - ``page_range`` (optional): list ``[start, end]`` or string
          ``"start-end"`` (1-indexed inclusive).
        - ``section_heading`` (optional): heading to scope by.
        - ``heading_regex`` (optional flag): interpret heading as regex.

    Output: UTF-8 text string. ``summary``/``meta`` record the PDF's
    total page count, the pages actually extracted, character count,
    and any pdfplumber warnings captured via a logging handler.
    """

    name = "extract_pdf_text"
    required_scope_fields: tuple[str, ...] = ()
    optional_scope_fields: tuple[str, ...] = (
        "page_range",
        "section_heading",
        "heading_regex",
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

        # Prefer a resolved_page_range carried forward by a preceding
        # resolve_section_scope primitive (multi_section_pdf path) over
        # the scope-declared range. The resolved range is always [start, end]
        # derived from the TOC and is the authoritative answer for scoped
        # multi-section extractions.
        resolved_range = (previous.meta or {}).get("resolved_page_range")
        page_range = (
            _parse_page_range(resolved_range)
            if resolved_range is not None
            else _parse_page_range(getattr(scope, "page_range", None))
        )
        section_heading = getattr(scope, "section_heading", None)
        is_regex = bool(getattr(scope, "heading_regex", False))

        warnings: list[str] = []
        handler = _ListLoggingHandler(warnings)
        pdf_logger = logging.getLogger("pdfminer")
        pdf_logger.addHandler(handler)
        previous_level = pdf_logger.level
        pdf_logger.setLevel(logging.WARNING)

        summary: dict[str, Any] = {"status": "ok", "pdfplumber_version": pdfplumber.__version__}
        meta: dict[str, Any] = {}
        try:
            with pdfplumber.open(io.BytesIO(bytes(raw))) as pdf:
                total_pages = len(pdf.pages)
                summary["source_page_count"] = total_pages
                page_texts = _extract_page_texts(pdf)

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
                if warnings:
                    summary["pdfplumber_warnings"] = warnings[:5]
                    meta["pdfplumber_warnings"] = warnings

                return PrimitiveResult(output=text, summary=summary, meta=meta)
        except Exception as exc:  # noqa: BLE001 — surface primitive-level
            return PrimitiveResult(
                output="",
                summary={"status": "pdfplumber_open_failed", "error": str(exc)},
                meta={"extract_failure": f"pdfplumber_open_failed: {exc}"},
            )
        finally:
            pdf_logger.removeHandler(handler)
            pdf_logger.setLevel(previous_level)


class _ListLoggingHandler(logging.Handler):
    def __init__(self, bucket: list[str]) -> None:
        super().__init__()
        self.bucket = bucket

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.bucket.append(self.format(record))
        except Exception:  # noqa: BLE001
            return
