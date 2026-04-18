"""Phase 0 manifest spot-check.

Reads a Phase 0 manifest.json and prints a human-readable summary:
source, what was requested, what was acquired, primitive trace, any
errors or user interactions, content preview, content hash, encoding.

This is an inspection tool, not a formal test. The formal comparison
against reference outputs is Session 4b's work.

Usage:
    python scripts/phase0/spot_check.py <path-to-manifest-or-dir>

If a directory is supplied, looks for ``manifest.json`` inside it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


_PREVIEW_HEAD = 500
_PREVIEW_TAIL = 200


def _load_manifest(target: Path) -> tuple[dict[str, Any], Path]:
    if target.is_dir():
        target = target / "manifest.json"
    if not target.exists():
        raise FileNotFoundError(f"Manifest not found at: {target}")
    with target.open(encoding="utf-8") as f:
        return json.load(f), target


def _truncate(value: Any, n: int = 160) -> str:
    s = str(value)
    return s if len(s) <= n else s[: n - 1] + "…"


def _render(manifest: dict[str, Any], manifest_path: Path) -> str:
    out: list[str] = []

    out.append("=" * 72)
    out.append(f"Phase 0 manifest spot-check — {manifest_path}")
    out.append("=" * 72)
    out.append("")

    out.append(f"Source reference : {manifest.get('source_reference')}")
    out.append(f"Source type      : {manifest.get('source_type')}")
    out.append(f"Phase 0 version  : {manifest.get('phase0_version')}")
    out.append(f"Timestamp        : {manifest.get('timestamp')}")
    out.append(f"Content hash     : {manifest.get('content_hash')}")
    out.append(f"Detection hash   : {manifest.get('detection_hash')}")
    out.append(f"Encoding detected: {manifest.get('encoding_detected')}")
    if manifest.get("encoding_failure"):
        out.append(f"Encoding failure : {manifest['encoding_failure']}")
    pathologies = manifest.get("known_pathology_handling") or []
    if pathologies:
        out.append(f"Pathologies      : {', '.join(pathologies)}")
    else:
        out.append("Pathologies      : (none)")
    memos = manifest.get("investigation_memo_refs") or []
    if memos:
        out.append("Investigation memos:")
        for ref in memos:
            out.append(f"  - {ref}")
    if manifest.get("notes"):
        out.append(f"Notes            : {manifest['notes']}")
    out.append("")

    out.append("-- Scope requested --")
    scope = manifest.get("scope_requested") or {}
    for key in sorted(scope.keys()):
        val = scope[key]
        if val is None or val == "" or val is False:
            continue
        out.append(f"  {key}: {_truncate(val)}")
    out.append("")

    out.append("-- Scope acquired --")
    acquired = manifest.get("scope_acquired") or {}
    for key in sorted(acquired.keys()):
        if key == "verification_excerpt" and isinstance(acquired[key], dict):
            ve = acquired[key]
            out.append(f"  {key}:")
            out.append(f"    line_count : {ve.get('line_count')}")
            out.append(f"    first_chars: {_truncate(ve.get('first_chars'), 200)}")
            out.append(f"    last_chars : {_truncate(ve.get('last_chars'), 120)}")
            continue
        out.append(f"  {key}: {_truncate(acquired[key])}")
    out.append("")

    out.append("-- Primitive sequence --")
    for i, name in enumerate(manifest.get("primitive_sequence") or [], start=1):
        out.append(f"  {i}. {name}")
    out.append("")

    out.append("-- Acquisition trace --")
    for i, entry in enumerate(manifest.get("acquisition_trace") or [], start=1):
        out.append(
            f"  [{i}] {entry.get('primitive')}  "
            f"({entry.get('duration_ms', 0)} ms)"
        )
        if entry.get("error"):
            out.append(f"      ERROR: {entry['error']}")
        for k, v in (entry.get("outputs_summary") or {}).items():
            out.append(f"      {k}: {_truncate(v)}")
        if entry.get("user_interaction"):
            ui = entry["user_interaction"]
            out.append(
                f"      user_interaction: {ui.get('needed', '')[:100]}…"
            )
    out.append("")

    user_interactions = manifest.get("user_interactions") or []
    if user_interactions:
        out.append("-- User interactions --")
        for i, ui in enumerate(user_interactions, start=1):
            out.append(f"  [{i}] {ui.get('primitive')}: {ui.get('needed')}")
            if ui.get("request_file"):
                out.append(f"      request_file: {ui['request_file']}")
            if ui.get("provided_file"):
                out.append(f"      provided_file: {ui['provided_file']}")
            out.append(f"      resolved: {ui.get('resolved')}")
        out.append("")

    verification_trace = manifest.get("verification_trace") or []
    out.append("-- Verification trace --")
    if not verification_trace:
        out.append("  (none — this artefact predates schema 0.3.0)")
    else:
        for i, entry in enumerate(verification_trace, start=1):
            out.append(
                f"  [{i}] {entry.get('primitive')} -> "
                f"verdict: {entry.get('verdict')}"
            )
            for c in entry.get("checks_run") or []:
                passed = c.get("passed")
                flagged = c.get("flagged")
                status = (
                    "FAIL" if not passed else ("flag" if flagged else "ok")
                )
                out.append(
                    f"      {c.get('name'):25s} "
                    f"value={c.get('value')!s:10s} "
                    f"threshold={c.get('threshold')!s:10s} [{status}]"
                )
            samples = (entry.get("details") or {}).get(
                "sample_failures"
            ) or []
            for s in samples[:3]:
                out.append(
                    f"      sample line {s.get('line_index')}: "
                    f"{_truncate(s.get('preview'), 100)}"
                )
    out.append("")

    out.append("-- Content files --")
    for p in manifest.get("content_files") or []:
        out.append(f"  {p}")
    out.append("")

    out.append("-- Content preview --")
    content_files = manifest.get("content_files") or []
    if not content_files:
        out.append("  (no content files written)")
    else:
        manifest_dir = manifest_path.parent
        for p in content_files:
            cp = Path(p)
            if not cp.is_absolute():
                cp_rel = manifest_dir / cp
                if cp_rel.exists():
                    cp = cp_rel
            if not cp.exists():
                out.append(f"  [missing] {p}")
                continue
            text = cp.read_text(encoding="utf-8")
            out.append(f"  {cp}  ({len(text)} chars)")
            out.append("")
            head = text[:_PREVIEW_HEAD].rstrip()
            out.append("  --- first " + str(_PREVIEW_HEAD) + " chars ---")
            for line in head.splitlines():
                out.append(f"  | {line}")
            out.append("")
            tail = text[-_PREVIEW_TAIL:].lstrip()
            out.append("  --- last " + str(_PREVIEW_TAIL) + " chars ---")
            for line in tail.splitlines():
                out.append(f"  | {line}")
    out.append("")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        help="Path to manifest.json or the directory containing it.",
    )
    args = parser.parse_args(argv)

    target = Path(args.target)
    manifest, path = _load_manifest(target)
    print(_render(manifest, path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
