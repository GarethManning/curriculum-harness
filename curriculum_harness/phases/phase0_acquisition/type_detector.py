"""Phase 0 source-type detector.

Classifies a source reference (URL or local path) into one of the
supported source-type tags, so the Phase 0 executor can route it to the
right primitive sequence.

Detection tags (stable, version 0.1):

- ``static_html_linear``  — HTML page whose content sits in the
  server-rendered HTML (no JS framework shell). Handled by Session 4a-0.
- ``flat_pdf_linear``     — PDF with a single linear section, no
  multi-section TOC. Primitive: pending (Session 4a-1+).
- ``multi_section_pdf``   — PDF whose TOC spans multiple major
  sections. Primitive: pending.
- ``js_rendered_progressive_disclosure`` — HTML whose content is
  injected client-side (React/Vue/Angular shell, empty body). Primitive:
  pending.
- ``html_nested_dom``     — HTML with deeply nested / tabbed content
  that linear extraction cannot handle cleanly. Primitive: pending.
- ``unknown``             — detection inconclusive.

Model-call policy: this module is the ONLY place in Phase 0 where a
model call is permitted, and only for classification tie-breaking.
Extraction primitives must remain deterministic. Session 4a-0 does not
yet invoke a model — detection is heuristic only. The hook is defined
so later sessions can add it without re-threading the architecture.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

import httpx

from curriculum_harness.phases.phase0_acquisition.manifest import SourceType


SUPPORTED_SOURCE_TYPES: tuple[SourceType, ...] = (
    "static_html_linear",
    "flat_pdf_linear",
)

SUPPORTED_IN_SESSION_4A_0: tuple[SourceType, ...] = SUPPORTED_SOURCE_TYPES


@dataclass
class DetectionResult:
    source_type: SourceType
    confidence: Literal["high", "medium", "low"]
    rationale: str
    signals: dict[str, Any] = field(default_factory=dict)
    is_supported_now: bool = False


_JS_FRAMEWORK_MARKERS = (
    re.compile(rb"""<div[^>]+id=["']root["']""", re.I),
    re.compile(rb"""<div[^>]+id=["']app["']""", re.I),
    re.compile(rb"""<div[^>]+id=["']__next["']""", re.I),
    re.compile(rb"""__NUXT__""", re.I),
    re.compile(rb"""window\.__INITIAL_STATE__""", re.I),
    re.compile(rb"""data-reactroot""", re.I),
)

_TEXT_STRIP_TAGS = re.compile(
    rb"(?is)<(script|style|noscript)[^>]*>.*?</\1>",
)
_TAG_STRIP = re.compile(rb"(?is)<[^>]+>")


def _looks_like_html(body: bytes) -> bool:
    head = body[:4000].lstrip().lower()
    if not head:
        return False
    if head.startswith((b"<!", b"<html", b"<?xml")):
        return True
    if b"<!doctype html" in head[:200]:
        return True
    if b"<head" in head[:4000] or b"<body" in head[:4000]:
        return True
    return False


def _rough_visible_text_ratio(body: bytes) -> float:
    """Proportion of rendered-text bytes to total bytes.

    A JS-rendered SPA shell typically has a very thin ratio (mostly JS
    bundles, tiny <div id="root"/>). A static HTML page has a fatter
    ratio. Not used alone — combined with framework markers.
    """

    if not body:
        return 0.0
    stripped = _TEXT_STRIP_TAGS.sub(b" ", body)
    stripped = _TAG_STRIP.sub(b" ", stripped)
    visible = stripped.strip()
    return len(visible) / max(len(body), 1)


def _has_js_framework_markers(body: bytes) -> list[str]:
    hits: list[str] = []
    head_and_top = body[:80_000]
    for rx in _JS_FRAMEWORK_MARKERS:
        m = rx.search(head_and_top)
        if m:
            hits.append(m.group(0).decode("latin-1", errors="replace"))
    return hits


def _classify_html(body: bytes) -> DetectionResult:
    markers = _has_js_framework_markers(body)
    text_ratio = _rough_visible_text_ratio(body)
    signals: dict[str, Any] = {
        "bytes": len(body),
        "text_ratio": round(text_ratio, 4),
        "js_framework_markers": markers[:4],
    }

    if markers and text_ratio < 0.05:
        return DetectionResult(
            source_type="js_rendered_progressive_disclosure",
            confidence="high",
            rationale=(
                "JS framework shell detected and visible-text ratio is "
                "below 5 %; content almost certainly renders client-side."
            ),
            signals=signals,
        )

    if markers and text_ratio < 0.12:
        return DetectionResult(
            source_type="js_rendered_progressive_disclosure",
            confidence="medium",
            rationale=(
                "JS framework markers present with thin rendered text — "
                "likely progressive disclosure."
            ),
            signals=signals,
        )

    # Nested-DOM heuristic: high tag density, many <div> layers.
    tag_count = len(re.findall(rb"<[a-zA-Z]", body))
    div_count = len(re.findall(rb"<div\b", body, flags=re.I))
    signals["tag_count"] = tag_count
    signals["div_count"] = div_count
    if div_count > 1500 and text_ratio < 0.18:
        return DetectionResult(
            source_type="html_nested_dom",
            confidence="medium",
            rationale=(
                "Very high div count with thin visible-text ratio — "
                "nested / tabbed DOM likely; linear extraction risky."
            ),
            signals=signals,
        )

    return DetectionResult(
        source_type="static_html_linear",
        confidence="high" if text_ratio > 0.2 else "medium",
        rationale=(
            "HTML with server-rendered content and no JS framework "
            "shell markers detected."
        ),
        signals=signals,
        is_supported_now=True,
    )


def _classify_pdf(body: bytes) -> DetectionResult:
    """Distinguish flat_pdf_linear from multi_section_pdf by TOC shape.

    Heuristic: look at the first few pages for structural TOC markers
    (runs of dotted leaders, "Contents" / "Table of Contents", numbered
    chapter/section listings). Multi-section: >=3 TOC-like lines with
    page-number anchors.
    """

    signals: dict[str, Any] = {"bytes": len(body)}
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(body))
        n_pages = len(reader.pages)
        signals["n_pages"] = n_pages

        preview_pages = min(6, n_pages)
        preview = ""
        for i in range(preview_pages):
            try:
                preview += (reader.pages[i].extract_text() or "") + "\n"
            except Exception:  # noqa: BLE001 — PDF extraction is flaky
                continue

        low = preview.lower()
        has_toc_heading = bool(
            re.search(r"\b(table of contents|contents)\b", low)
        )
        dot_leader_lines = len(re.findall(r"\.{4,}\s*\d+", preview))
        numbered_sections = len(
            re.findall(r"(?m)^\s*(?:\d+(?:\.\d+)+|[ivxlcdm]+\.)\s+\S", preview)
        )
        signals.update(
            {
                "has_toc_heading": has_toc_heading,
                "dot_leader_lines": dot_leader_lines,
                "numbered_sections": numbered_sections,
            }
        )

        multi_section = (
            (has_toc_heading and dot_leader_lines >= 3)
            or dot_leader_lines >= 6
            or numbered_sections >= 6
        )
        if multi_section or n_pages > 30:
            return DetectionResult(
                source_type="multi_section_pdf",
                confidence="medium",
                rationale=(
                    "PDF with multi-section TOC markers or long page "
                    f"count ({n_pages})."
                ),
                signals=signals,
            )

        return DetectionResult(
            source_type="flat_pdf_linear",
            confidence="medium",
            rationale="Short PDF with no multi-section TOC markers.",
            signals=signals,
        )
    except Exception as exc:  # noqa: BLE001
        signals["pdf_parse_error"] = str(exc)
        # Valid-PDF-magic body that pypdf cannot parse is usually a
        # truncated head-fetch of a large PDF (detector reads ~200 KB;
        # typical CED-sized PDFs are 5 MB+). Fall back to the
        # conservative flat-PDF route with low confidence rather than
        # ``unknown``, since the PDF bytes were recognised on fetch and
        # the flat-PDF sequence fetches the full file itself.
        if body[:5] == b"%PDF-":
            return DetectionResult(
                source_type="flat_pdf_linear",
                confidence="low",
                rationale=(
                    "PDF magic present but pypdf could not parse the "
                    f"truncated head fetch ({exc}). Defaulting to "
                    "flat_pdf_linear; upgrade to multi_section_pdf in a "
                    "later session."
                ),
                signals=signals,
            )
        return DetectionResult(
            source_type="unknown",
            confidence="low",
            rationale=f"PDF parse failed: {exc}",
            signals=signals,
        )


def _looks_like_pdf(body: bytes, content_type: str) -> bool:
    if "pdf" in content_type.lower():
        return True
    return body[:5] == b"%PDF-"


def _fetch_head(url: str, timeout: float = 20.0) -> tuple[bytes, str]:
    """Fetch up to ~200 KB for detection. Uses httpx (async-free call)."""

    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        headers={
            "User-Agent": (
                "Curriculum-Harness/0.1 "
                "(+https://github.com/GarethManning/curriculum-harness)"
            ),
        },
    ) as client:
        with client.stream("GET", url) as r:
            r.raise_for_status()
            ct = r.headers.get("content-type", "")
            buf = bytearray()
            for chunk in r.iter_bytes():
                buf.extend(chunk)
                if len(buf) >= 200_000:
                    break
            return bytes(buf), ct


def detect_source_type(source_reference: str) -> DetectionResult:
    """Classify a URL or local path.

    For URLs, fetches up to ~200 KB of the body with a GET (HEAD is
    unreliable for content-type). For local files, reads the first 200 KB
    from disk.
    """

    parsed = urlparse(source_reference)
    is_url = parsed.scheme in {"http", "https"}

    if is_url:
        try:
            body, content_type = _fetch_head(source_reference)
        except Exception as exc:  # noqa: BLE001
            return DetectionResult(
                source_type="unknown",
                confidence="low",
                rationale=f"Fetch failed during detection: {exc}",
                signals={"fetch_error": str(exc)},
            )

        if _looks_like_pdf(body, content_type):
            res = _classify_pdf(body)
            res.signals["content_type"] = content_type
            return res

        if _looks_like_html(body):
            res = _classify_html(body)
            res.signals["content_type"] = content_type
            return res

        return DetectionResult(
            source_type="unknown",
            confidence="low",
            rationale="Response is neither recognisable HTML nor PDF.",
            signals={"content_type": content_type, "bytes": len(body)},
        )

    # Local path
    path = Path(source_reference)
    if not path.exists():
        return DetectionResult(
            source_type="unknown",
            confidence="low",
            rationale=f"Local path does not exist: {source_reference}",
        )
    with path.open("rb") as f:
        body = f.read(200_000)
    ext = path.suffix.lower()
    if ext == ".pdf" or body[:5] == b"%PDF-":
        res = _classify_pdf(body)
        res.signals["extension"] = ext
        return res
    if ext in {".html", ".htm"} or _looks_like_html(body):
        res = _classify_html(body)
        res.signals["extension"] = ext
        return res
    return DetectionResult(
        source_type="unknown",
        confidence="low",
        rationale=f"Unrecognised local file extension: {ext}",
        signals={"extension": ext},
    )


def unsupported_type_pause_message(
    source_reference: str,
    detected: DetectionResult,
) -> str:
    """Human-readable user-in-the-loop message for deferred types."""

    supported = ", ".join(f"`{t}`" for t in SUPPORTED_SOURCE_TYPES)
    return (
        f"Phase 0 detected source type `{detected.source_type}` for "
        f"`{source_reference}`.\n\n"
        f"Supported source types: {supported}. The primitive sequence "
        f"for `{detected.source_type}` is deferred to a later session.\n\n"
        "Options while the primitive is pending:\n"
        "- Provide the scoped content manually as plain text (write it "
        "to `provided.txt` in this directory).\n"
        "- Wait for the relevant session to add the primitive.\n\n"
        f"Detection rationale: {detected.rationale}\n"
        f"Detection confidence: {detected.confidence}\n"
    )
