"""Build a ``SourceInventory`` from a Phase 0 run-snapshot.

Verbatim extraction only. The inventory holds the source's content
blocks with source-position metadata and heading hierarchy. No
interpretation, no classification, no content transformation beyond
reassembling mid-sentence line breaks introduced by HTML-to-text
extraction (the block's ``raw_text`` preserves the reassembled
verbatim content; the original line span is preserved in
``line_start``/``line_end``).

The pipeline does not consult the run-snapshot's ``verification_trace``
classifications — those are Phase 0 pre-classification and would
contaminate the independent KUD classifier downstream.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from curriculum_harness.reference_authoring.types import (
    ContentBlock,
    SourceInventory,
)

_SENTENCE_TERMINATORS = (".", "!", "?", '"', "'", "”", "’", "”")
_BULLET_PATTERNS = (
    re.compile(r"^[•·●◦▪–—-]\s+"),
    re.compile(r"^[a-zA-Z]\)\s+"),
    re.compile(r"^\d+\)\s+"),
    re.compile(r"^[ivxlcdm]+\.\s+", re.IGNORECASE),
)
_NUMBERED_HEADING = re.compile(r"^\d+(?:\.\d+)*\.\s+[A-Z]")


def _is_all_caps_heading(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 4:
        return False
    letters = [c for c in stripped if c.isalpha()]
    if not letters:
        return False
    if not all(c.isupper() for c in letters):
        return False
    # Reject if it's a one-or-two-word shout that's more plausibly inline
    # emphasis — enforce at least some space or the full line is caps.
    return True


def _is_numbered_heading(line: str) -> bool:
    return bool(_NUMBERED_HEADING.match(line.strip()))


def _is_heading(line: str) -> tuple[bool, int]:
    """Return (is_heading, depth)."""
    if _is_all_caps_heading(line):
        return True, 1
    if _is_numbered_heading(line):
        return True, 2
    return False, 0


def _is_bullet(line: str) -> bool:
    s = line.lstrip()
    for pat in _BULLET_PATTERNS:
        if pat.match(s):
            return True
    return False


def _ends_with_terminator(line: str) -> bool:
    s = line.rstrip()
    if not s:
        return False
    return s.endswith(_SENTENCE_TERMINATORS)


def _is_continuation(prev_line: str, current_line: str) -> bool:
    """Decide if ``current_line`` is a mid-sentence continuation of ``prev_line``.

    HTML-to-text extraction commonly splits sentences across lines in the
    middle of a word (e.g. Welsh CfW extraction produces "empathy" as its
    own line). These are joined into the preceding block rather than
    split into separate blocks.
    """
    prev = prev_line.rstrip()
    curr = current_line.lstrip()
    if not prev or not curr:
        return False
    prev_term = prev.endswith(_SENTENCE_TERMINATORS)
    # Line consisting only of punctuation — always a continuation.
    if not any(c.isalnum() for c in curr):
        return True
    if prev_term:
        return False
    # Line starts with punctuation (comma, etc.) — mid-sentence continuation.
    if not curr[0].isalnum():
        return True
    # Lowercase first character — mid-sentence continuation.
    if curr[0].islower():
        return True
    # Very short fragment when the previous line hasn't terminated.
    if len(curr.split()) <= 2:
        return True
    return False


def _classify_block_type(line: str) -> str:
    is_head, _depth = _is_heading(line)
    if is_head:
        return "heading"
    if _is_bullet(line):
        return "bullet"
    return "statement"


def _slug_from_snapshot_path(snapshot_path: str) -> str:
    base = os.path.basename(os.path.normpath(snapshot_path))
    # Strip leading "YYYY-MM-DD-session-Na-N-" style dating if present.
    stripped = re.sub(r"^\d{4}-\d{2}-\d{2}-session-[^-]+-(?:\d+-)?", "", base)
    stripped = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stripped)
    return stripped or base


def build_inventory_from_snapshot(snapshot_path: str) -> SourceInventory:
    """Build a ``SourceInventory`` from a Phase 0 run-snapshot directory.

    Args:
        snapshot_path: Path to a ``docs/run-snapshots/<slug>/`` directory
            containing ``content.txt`` and ``manifest.json``.

    Returns:
        ``SourceInventory`` with verbatim content blocks and metadata.
    """
    snapshot_path = os.path.normpath(snapshot_path)
    content_path = os.path.join(snapshot_path, "content.txt")
    manifest_path = os.path.join(snapshot_path, "manifest.json")
    if not os.path.exists(content_path):
        raise FileNotFoundError(f"missing content.txt at {content_path}")
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"missing manifest.json at {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest: dict[str, Any] = json.load(fh)

    with open(content_path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    lines = raw.split("\n")
    # Drop a single trailing empty-line artefact from newline-terminated files.
    if lines and lines[-1] == "":
        lines = lines[:-1]

    blocks: list[ContentBlock] = []
    heading_stack: dict[int, str] = {}

    def _current_heading_path() -> list[str]:
        return [heading_stack[d] for d in sorted(heading_stack)]

    current_lines: list[str] = []
    current_start: int = 0
    current_type: str = ""

    def _flush() -> None:
        if not current_lines:
            return
        joined = " ".join(s.strip() for s in current_lines).strip()
        # Collapse multi-space runs introduced by join-with-space.
        joined = re.sub(r"\s+", " ", joined)
        if not joined:
            return
        block_id = f"blk_{len(blocks) + 1:04d}"
        blocks.append(
            ContentBlock(
                block_id=block_id,
                raw_text=joined,
                block_type=current_type or "statement",
                line_start=current_start,
                line_end=current_start + len(current_lines) - 1,
                heading_path=_current_heading_path(),
            )
        )

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line
        stripped = line.strip()
        if not stripped:
            _flush()
            current_lines = []
            current_type = ""
            continue

        is_head, depth = _is_heading(line)
        if is_head:
            # Flush current accumulator, emit heading as its own block,
            # and update the running heading stack at the detected depth.
            _flush()
            current_lines = []
            block_id = f"blk_{len(blocks) + 1:04d}"
            # Reset deeper stack levels when a shallower heading appears.
            for d in list(heading_stack):
                if d >= depth:
                    heading_stack.pop(d)
            blocks.append(
                ContentBlock(
                    block_id=block_id,
                    raw_text=stripped,
                    block_type="heading",
                    line_start=idx,
                    line_end=idx,
                    heading_path=_current_heading_path() + [stripped],
                )
            )
            heading_stack[depth] = stripped
            current_type = ""
            continue

        if current_lines and _is_continuation(current_lines[-1], line):
            current_lines.append(stripped)
        else:
            _flush()
            current_lines = [stripped]
            current_start = idx
            current_type = _classify_block_type(line)

    _flush()

    inventory = SourceInventory(
        source_slug=_slug_from_snapshot_path(snapshot_path),
        snapshot_path=snapshot_path,
        manifest_content_hash=str(manifest.get("content_hash", "")),
        phase0_version=str(manifest.get("phase0_version", "")),
        source_reference=str(manifest.get("source_reference", "")),
        content_blocks=blocks,
    )
    return inventory
