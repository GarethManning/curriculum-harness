"""Session 4a-4.5 Step 6 — regression from cached raw content.

Reads a Phase 0 manifest (schema 0.6.0), loads the cached raw content
referenced by ``raw_content_files``, replays the post-fetch primitive
sequence against the cached bytes, and checks the regenerated
``content_hash`` equals the stored value byte-for-byte.

Re-fetching from the (sometimes-unavailable) origin is deliberately
avoided — the whole point of raw-content caching is that future
regression tests can run without network access to the source.

Local-file ``source_reference`` entries are validated at start: the
referenced path must exist and its current SHA-256 must match the
stored hash. On failure, a ``LocalSourceReferenceInvalid`` error is
reported for that artefact (path missing vs hash drifted), and
processing continues with the next artefact rather than halting.

Usage:

    python -m scripts.phase0.regression_from_cache
        [--manifest <path>]
        [--report <path>]
        [--snapshot-glob <glob>]

Default: scans ``docs/run-snapshots/2026-04-18-session-4a-4-5-*``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from curriculum_harness.phases.phase0_acquisition.manifest import (
    AcquisitionManifest,
    ScopeSpec,
)
from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
)
from curriculum_harness.phases.phase0_acquisition.sequences import (
    SEQUENCE_BUILDERS,
)


REPO = Path(__file__).resolve().parents[2]


class LocalSourceReferenceInvalid(Exception):
    """Raised when a source_reference path is missing or its hash drifted.

    Carries a ``kind`` attribute distinguishing the two failure modes:
    ``missing_path`` (file gone) vs ``hash_drift`` (file present but
    bytes changed since the manifest was written).
    """

    def __init__(self, kind: str, message: str):
        self.kind = kind
        super().__init__(message)


# Fetch-primitive names that the replay path substitutes for. Knowing
# the set lets the replay loop skip any fetch primitive the sequence
# builder included, since the cached bytes already stand in for its
# output.
_FETCH_PRIMITIVES: frozenset[str] = frozenset(
    {"fetch_requests", "fetch_pdf_file", "fetch_via_browser"}
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_source_references(
    manifest: AcquisitionManifest,
) -> list[dict[str, Any]]:
    """Re-hash every ``source_reference`` entry and compare to stored hash.

    Returns a list of error dicts (empty if all valid). Does not raise;
    callers decide whether a drift should abort or continue.
    """

    errors: list[dict[str, Any]] = []
    for rcf in manifest.raw_content_files:
        if rcf.file_type != "source_reference":
            continue
        ref_path = Path(rcf.path)
        if not ref_path.exists():
            errors.append(
                {
                    "kind": "missing_path",
                    "path": str(ref_path),
                    "detail": "Referenced local source no longer exists.",
                }
            )
            continue
        current_hash = _sha256_file(ref_path)
        if current_hash != rcf.hash:
            errors.append(
                {
                    "kind": "hash_drift",
                    "path": str(ref_path),
                    "stored_hash": rcf.hash,
                    "current_hash": current_hash,
                    "detail": (
                        "Referenced local source bytes have changed since "
                        "the manifest was written."
                    ),
                }
            )
    return errors


def _fetch_requests_replay(raw_bytes: bytes) -> PrimitiveResult:
    """Synthesise a fetch_requests-shaped result from cached bytes.

    The post-fetch primitives consume ``previous.output`` (the raw
    bytes) and ``previous.meta['declared_encoding']`` +
    ``content_type``. Encoding detection falls through to chardet when
    declared_encoding is None, which matches the original path when
    the cached manifest doesn't pin a declared encoding.
    """

    return PrimitiveResult(
        output=raw_bytes,
        summary={"status": "ok", "bytes": len(raw_bytes), "replay": True},
        meta={
            "declared_encoding": None,
            "final_url": None,
            "http_status": 200,
            "content_type": "text/html",
            "replayed_from_cache": True,
        },
    )


def _fetch_pdf_replay(raw_bytes: bytes, source_kind: str) -> PrimitiveResult:
    return PrimitiveResult(
        output=raw_bytes,
        summary={
            "status": "ok",
            "source_kind": source_kind,
            "bytes": len(raw_bytes),
            "replay": True,
        },
        meta={
            "source_kind": source_kind,
            "pdf_magic_ok": raw_bytes[:5] == b"%PDF-",
            "replayed_from_cache": True,
        },
    )


def _fetch_via_browser_replay(rendered_html: str) -> PrimitiveResult:
    """Synthesise a fetch_via_browser-shaped result from a cached DOM.

    Carries ``rendered_html`` in both ``output`` and ``meta`` so both
    ``dom_hash`` (reads meta) and ``extract_css_selector`` (reads
    output / meta) see the same bytes the browser originally produced.
    """

    rendered_bytes = rendered_html.encode("utf-8")
    rendered_hash = hashlib.sha256(rendered_bytes).hexdigest()
    # Re-emit the same raw_content shape fetch_via_browser emits, so
    # dom_hash's equivalence check passes as in the live run.
    raw_content = [
        {
            "filename": "raw_rendered.html",
            "bytes": rendered_bytes,
            "file_type": "rendered_html",
            "hash": rendered_hash,
            "bytes_count": len(rendered_bytes),
        }
    ]
    return PrimitiveResult(
        output=rendered_html,
        summary={
            "status": "ok",
            "rendered_html_bytes": len(rendered_html),
            "replay": True,
        },
        meta={
            "final_url": None,
            "http_status": 200,
            "rendered_html": rendered_html,
            "rendered_html_hash": rendered_hash,
            "rendered_html_bytes": len(rendered_html),
            "fetched_bytes": len(rendered_html),
            "raw_content": raw_content,
            "replayed_from_cache": True,
        },
    )


def _load_cached_primary(manifest: AcquisitionManifest) -> dict[str, Any]:
    """Locate the manifest's primary cached raw input and load its bytes.

    Returns a dict with keys ``file_type``, ``path``, and either
    ``bytes`` (for cached files) or nothing for a missing cache.
    Raises ``LocalSourceReferenceInvalid`` when the primary input is a
    source_reference and its hash has drifted.
    """

    priority = [
        "rendered_html",
        "source_pdf",
        "source_html",
        "source_reference",
    ]
    by_type: dict[str, Any] = {}
    for rcf in manifest.raw_content_files:
        by_type.setdefault(rcf.file_type, rcf)
    chosen = None
    for ft in priority:
        if ft in by_type:
            chosen = by_type[ft]
            break
    if chosen is None:
        raise FileNotFoundError(
            "Manifest has no primary raw_content entry "
            "(rendered_html | source_pdf | source_html | source_reference)."
        )

    # source_reference validation is the common-case failure path.
    if chosen.file_type == "source_reference":
        ref_path = Path(chosen.path)
        if not ref_path.exists():
            raise LocalSourceReferenceInvalid(
                "missing_path",
                f"Referenced local source no longer exists: {ref_path}",
            )
        current_hash = _sha256_file(ref_path)
        if current_hash != chosen.hash:
            raise LocalSourceReferenceInvalid(
                "hash_drift",
                (
                    f"Referenced local source bytes drifted: {ref_path} "
                    f"stored={chosen.hash} current={current_hash}"
                ),
            )
        return {
            "file_type": chosen.file_type,
            "path": str(ref_path),
            "bytes": ref_path.read_bytes(),
        }

    cache_path = Path(chosen.path)
    if not cache_path.exists():
        raise FileNotFoundError(
            f"Cached raw content missing on disk: {cache_path}"
        )
    current_hash = _sha256_file(cache_path)
    if current_hash != chosen.hash:
        raise RuntimeError(
            "Cached raw content hash drifted on disk: "
            f"{cache_path} stored={chosen.hash} current={current_hash}"
        )
    return {
        "file_type": chosen.file_type,
        "path": str(cache_path),
        "bytes": cache_path.read_bytes(),
    }


def _replay_sequence(
    manifest: AcquisitionManifest, cached: dict[str, Any]
) -> PrimitiveResult:
    """Run the post-fetch primitives against the cached raw input."""

    scope = manifest.scope_requested
    source_type = manifest.source_type
    builder = SEQUENCE_BUILDERS.get(source_type)
    if builder is None:
        raise ValueError(f"No sequence builder for source_type: {source_type}")
    sequence = builder(scope)

    # Synthesise the fetch-output PrimitiveResult that the first
    # non-fetch primitive will consume as ``previous``.
    file_type = cached["file_type"]
    raw_bytes: bytes = cached["bytes"]
    if file_type == "rendered_html":
        previous = _fetch_via_browser_replay(raw_bytes.decode("utf-8"))
    elif file_type == "source_html":
        previous = _fetch_requests_replay(raw_bytes)
    elif file_type == "source_pdf":
        previous = _fetch_pdf_replay(raw_bytes, source_kind="url")
    elif file_type == "source_reference":
        # For source_reference we assume PDF (the only case that uses
        # this file_type today). If this ever fires for an HTML
        # reference, extend the synthesis accordingly.
        previous = _fetch_pdf_replay(raw_bytes, source_kind="path")
    else:
        raise ValueError(f"Unsupported cache file_type for replay: {file_type}")

    source_metrics: dict[str, Any] = {"fetched_bytes": len(raw_bytes)}
    result = previous
    for prim in sequence:
        if prim.name in _FETCH_PRIMITIVES:
            # Skip: the cached bytes already stand in for this step's
            # output.
            continue
        result.meta["_source_metrics"] = dict(source_metrics)
        prim.validate_scope(scope)
        result = prim.run(scope, result)
    return result


def _regression_check(manifest_path: Path) -> dict[str, Any]:
    manifest_dict = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = AcquisitionManifest.model_validate(manifest_dict)

    # 1. Source-reference validation at start for all entries.
    ref_errors = _validate_source_references(manifest)

    # 2. Honour raw_content_unavailable — skip regeneration with note.
    if manifest.raw_content_unavailable and manifest.raw_content_unavailable.value:
        return {
            "manifest": str(manifest_path),
            "source_type": manifest.source_type,
            "outcome": "gapped",
            "reason": manifest.raw_content_unavailable.reason,
            "first_observed_at": manifest.raw_content_unavailable.first_observed_at,
            "source_reference_errors": ref_errors,
        }

    # 3. Run the extraction replay.
    try:
        cached = _load_cached_primary(manifest)
    except LocalSourceReferenceInvalid as exc:
        return {
            "manifest": str(manifest_path),
            "source_type": manifest.source_type,
            "outcome": "local_source_reference_invalid",
            "kind": exc.kind,
            "detail": str(exc),
            "source_reference_errors": ref_errors,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "manifest": str(manifest_path),
            "source_type": manifest.source_type,
            "outcome": "error",
            "detail": f"{type(exc).__name__}: {exc}",
            "source_reference_errors": ref_errors,
        }

    try:
        final_result = _replay_sequence(manifest, cached)
    except Exception as exc:  # noqa: BLE001
        return {
            "manifest": str(manifest_path),
            "source_type": manifest.source_type,
            "outcome": "error",
            "detail": f"{type(exc).__name__}: {exc}",
            "source_reference_errors": ref_errors,
        }

    regen_hash = final_result.meta.get("content_hash") or hashlib.sha256(
        str(final_result.output or "").encode("utf-8")
    ).hexdigest()
    stored_hash = manifest.content_hash or ""
    if regen_hash == stored_hash:
        return {
            "manifest": str(manifest_path),
            "source_type": manifest.source_type,
            "outcome": "clean",
            "content_hash": regen_hash,
            "source_reference_errors": ref_errors,
        }
    return {
        "manifest": str(manifest_path),
        "source_type": manifest.source_type,
        "outcome": "drift",
        "stored_content_hash": stored_hash,
        "regen_content_hash": regen_hash,
        "source_reference_errors": ref_errors,
    }


def _build_report(results: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append(
        "# Phase 0 cache regression report — Session 4a-4.5 Step 6"
    )
    lines.append("")
    lines.append(
        f"Generated: {datetime.now(timezone.utc).isoformat()}"
    )
    lines.append("")
    counts: dict[str, int] = {}
    for r in results:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    lines.append("## Summary")
    for k, v in sorted(counts.items()):
        lines.append(f"- {k}: {v}")
    lines.append("")

    for r in results:
        name = Path(r["manifest"]).parent.name
        lines.append(f"## {name}")
        lines.append(f"- outcome: **{r['outcome']}**")
        lines.append(f"- source_type: {r.get('source_type')}")
        if r["outcome"] == "clean":
            lines.append(
                f"- content_hash: `{r.get('content_hash', '')[:16]}...` — "
                "byte-identical with stored."
            )
        elif r["outcome"] == "gapped":
            lines.append(
                f"- reason: {r.get('reason')}"
            )
            lines.append(
                f"- first_observed_at: {r.get('first_observed_at')}"
            )
        elif r["outcome"] == "drift":
            lines.append(
                f"- stored  : `{r.get('stored_content_hash', '')[:16]}...`"
            )
            lines.append(
                f"- regen   : `{r.get('regen_content_hash', '')[:16]}...`"
            )
        elif r["outcome"] == "local_source_reference_invalid":
            lines.append(f"- kind: {r.get('kind')}")
            lines.append(f"- detail: {r.get('detail')}")
        elif r["outcome"] == "error":
            lines.append(f"- detail: {r.get('detail')}")
        if r.get("source_reference_errors"):
            lines.append(
                f"- source_reference_errors: "
                f"{len(r['source_reference_errors'])}"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=str, default=None)
    parser.add_argument(
        "--snapshot-glob",
        type=str,
        default="docs/run-snapshots/2026-04-18-session-4a-4-5-*",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="docs/project-log/phase0-cache-regression-2026-04-18.md",
    )
    args = parser.parse_args(argv)

    if args.manifest:
        manifest_paths = [REPO / args.manifest]
    else:
        manifest_paths = sorted(REPO.glob(f"{args.snapshot_glob}/manifest.json"))

    if not manifest_paths:
        print(f"No manifests found for glob: {args.snapshot_glob}")
        return 1

    results: list[dict[str, Any]] = []
    for mp in manifest_paths:
        res = _regression_check(mp)
        results.append(res)
        print(
            f"[{res['outcome']}] {mp.parent.name} — "
            f"{res.get('source_type')}"
        )

    report_path = REPO / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_build_report(results), encoding="utf-8")
    print(f"\nReport written to {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
