"""Resolve a multi-section PDF scope to an explicit page range.

The ``multi_section_pdf`` sequence inserts this primitive between
``detect_toc`` and the extraction primitive. It reads the TOC from the
previous primitive's ``meta['toc']`` and the user's scope spec, then
resolves one of three identifier forms into a concrete
``page_range = [start, end]`` that the downstream extractor can scope
against.

Resolution priority (first non-empty wins):

1. ``scope.page_range`` — explicit wins.
2. ``scope.section_identifier`` — exact TOC-entry title match.
3. ``scope.section_heading`` — case-insensitive prefix / regex match
   against TOC entries.

When the TOC is empty or none of the scope fields match, the
primitive pauses Phase 0 with a user-in-the-loop prompt listing the
available entries (or explaining that the PDF has no detectable
section structure).

The primitive does not mutate the scope; it emits the resolved range
via ``meta['resolved_page_range']`` so the extractor can read it in
preference to ``scope.page_range``. PDF bytes pass through to the
next primitive.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
)
from curriculum_harness.phases.phase0_acquisition.session_state import (
    PauseState,
)


def _compute_sibling_end(
    entries: list[dict], match_index: int, total_pages: int | None = None
) -> int:
    """Return the end page (1-indexed, inclusive) for a matched entry.

    The range runs from the matched entry's page to (next sibling or
    shallower entry's page - 1). If no such later entry exists, end at
    the last known page, or at the matched page + 19 as a safe fallback
    when total_pages is unknown.
    """
    matched = entries[match_index]
    matched_depth = matched["depth"]
    matched_page = matched["page_number"]
    for e in entries[match_index + 1 :]:
        if e["depth"] <= matched_depth:
            return max(matched_page, int(e["page_number"]) - 1)
    if total_pages is not None:
        return total_pages
    return matched_page + 19


def _find_identifier(entries: list[dict], identifier: str) -> int | None:
    target = identifier.strip()
    for i, e in enumerate(entries):
        if e["title"].strip() == target:
            return i
    return None


def _find_heading(entries: list[dict], heading: str, use_regex: bool) -> int | None:
    if use_regex:
        rx = re.compile(heading, re.IGNORECASE)
        for i, e in enumerate(entries):
            if rx.search(e["title"]):
                return i
        return None
    needle = heading.strip().lower()
    # Prefer exact case-insensitive then prefix match.
    for i, e in enumerate(entries):
        if e["title"].strip().lower() == needle:
            return i
    for i, e in enumerate(entries):
        if e["title"].strip().lower().startswith(needle):
            return i
    for i, e in enumerate(entries):
        if needle in e["title"].strip().lower():
            return i
    return None


class ResolveSectionScopePrimitive:
    """Resolve section_identifier / section_heading to a page_range.

    Pass-through: the PDF bytes flow unchanged to the next primitive.
    """

    name = "resolve_section_scope"
    required_scope_fields: tuple[str, ...] = ()
    optional_scope_fields: tuple[str, ...] = (
        "page_range",
        "section_identifier",
        "section_heading",
        "heading_regex",
    )
    side_effects: frozenset[str] = frozenset()

    def __init__(self, *, output_dir: str | None = None) -> None:
        self.output_dir = output_dir

    def validate_scope(self, scope) -> None:
        return None

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        if previous is None:
            raise ValueError("resolve_section_scope requires a previous primitive")
        data = previous.output
        toc_payload = (previous.meta or {}).get("toc") or {}
        entries: list[dict] = toc_payload.get("entries") or []
        total_pages = (
            (previous.meta or {}).get("_source_metrics", {}).get("source_page_count")
        )

        explicit_range = getattr(scope, "page_range", None)
        identifier = getattr(scope, "section_identifier", None)
        heading = getattr(scope, "section_heading", None)
        use_regex = bool(getattr(scope, "heading_regex", False))

        resolved: list[int] | None = None
        resolution_source: str | None = None
        matched_entry: dict | None = None

        if explicit_range:
            if (
                isinstance(explicit_range, (list, tuple))
                and len(explicit_range) == 2
            ):
                resolved = [int(explicit_range[0]), int(explicit_range[1])]
            elif isinstance(explicit_range, str):
                m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", explicit_range)
                if m:
                    resolved = [int(m.group(1)), int(m.group(2))]
            if resolved is not None:
                resolution_source = "explicit_page_range"

        if resolved is None and identifier and entries:
            idx = _find_identifier(entries, identifier)
            if idx is not None:
                matched_entry = entries[idx]
                end = _compute_sibling_end(entries, idx, total_pages)
                resolved = [int(matched_entry["page_number"]), int(end)]
                resolution_source = "section_identifier_match"

        if resolved is None and heading and entries:
            idx = _find_heading(entries, heading, use_regex)
            if idx is not None:
                matched_entry = entries[idx]
                end = _compute_sibling_end(entries, idx, total_pages)
                resolved = [int(matched_entry["page_number"]), int(end)]
                resolution_source = "section_heading_match"

        if resolved is None:
            pause_dir = (
                Path(self.output_dir) / "_paused"
                if self.output_dir
                else Path("_paused")
            )
            pause = PauseState(
                primitive=self.name,
                reason="section_scope_unresolved",
                needed=_render_pause_needed(entries, identifier, heading),
                expected_format="scope_fields",
                resume_hint=(
                    "Add a `page_range`, `section_identifier`, or "
                    "`section_heading` to the scope and re-run Phase 0."
                ),
                state_dir=str(pause_dir),
                source_reference=getattr(scope, "source_reference", ""),
                extra={
                    "toc_entries_count": len(entries),
                    "identifier_tried": identifier,
                    "heading_tried": heading,
                },
            )
            summary = {
                "status": "unresolved",
                "toc_entries_count": len(entries),
            }
            meta = {
                "pause_request": pause,
                "toc": toc_payload,
            }
            return PrimitiveResult(output=data, summary=summary, meta=meta)

        summary = {
            "status": "resolved",
            "resolved_page_range": resolved,
            "resolution_source": resolution_source,
        }
        if matched_entry is not None:
            summary["matched_entry_title"] = matched_entry["title"]
            summary["matched_entry_page"] = matched_entry["page_number"]
        meta: dict[str, Any] = {
            "resolved_page_range": resolved,
            "resolution_source": resolution_source,
            "toc": toc_payload,
        }
        if matched_entry is not None:
            meta["matched_entry"] = matched_entry
        return PrimitiveResult(output=data, summary=summary, meta=meta)


def _render_pause_needed(
    entries: list[dict], identifier: str | None, heading: str | None
) -> str:
    lines: list[str] = []
    lines.append(
        "Phase 0 cannot resolve the requested multi-section PDF scope."
    )
    lines.append("")
    if identifier:
        lines.append(
            f"- `section_identifier` supplied: `{identifier}` — "
            "no TOC entry matched this exact title."
        )
    if heading:
        lines.append(
            f"- `section_heading` supplied: `{heading}` — "
            "no TOC entry matched this pattern."
        )
    if not identifier and not heading:
        lines.append(
            "- No `page_range`, `section_identifier`, or "
            "`section_heading` was supplied."
        )
    lines.append("")
    if entries:
        lines.append("Available top-level TOC entries:")
        lines.append("")
        top = [e for e in entries if e.get("depth", 0) == 0][:40]
        for e in top:
            lines.append(
                f"  - `{e['title']}` (page {e['page_number']})"
            )
        if len(entries) > len(top):
            lines.append(f"  … plus {len(entries) - len(top)} deeper entries.")
    else:
        lines.append(
            "No TOC entries detected. Either the PDF has no usable "
            "section structure or TOC detection failed. Supply "
            "`page_range` explicitly to proceed."
        )
    return "\n".join(lines)
