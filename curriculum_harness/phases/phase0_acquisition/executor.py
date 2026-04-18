"""Phase 0 pipeline executor.

Takes an ordered primitive sequence and a ``ScopeSpec``, runs them in
order, and emits a manifest plus content files to an output directory.
Scope validation failures surface as user-in-the-loop pauses rather than
exceptions to the caller.

This executor is deliberately thin: the primitives carry the logic, and
the manifest carries the history. The executor just wires them.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from curriculum_harness.phases.phase0_acquisition.manifest import (
    AcquisitionManifest,
    PrimitiveTraceEntry,
    ScopeSpec,
    SourceType,
    UserInteraction,
    VerificationEntry,
)
from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    Primitive,
    PrimitiveResult,
    ScopeValidationError,
)
from curriculum_harness.phases.phase0_acquisition.session_state import (
    PauseState,
    write_pause_state,
)


class Phase0Paused(Exception):
    """Raised when Phase 0 pauses for user-in-the-loop input.

    The caller catches this, surfaces the request to the user, and
    re-invokes Phase 0 once the user has written a ``provided.txt`` /
    ``provided.json`` in the pause directory.
    """

    def __init__(self, manifest: AcquisitionManifest, pause_dir: str, message: str):
        self.manifest = manifest
        self.pause_dir = pause_dir
        super().__init__(message)


def _primitive_inputs_summary(scope: ScopeSpec, primitive: Primitive) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for f in primitive.required_scope_fields + primitive.optional_scope_fields:
        val = getattr(scope, f, None)
        if val is None or val == "":
            continue
        out[f] = val if not isinstance(val, str) else val[:200]
    return out


def run_pipeline(
    *,
    source_reference: str,
    source_type: SourceType,
    scope: ScopeSpec,
    primitives: list[Primitive],
    output_dir: str | Path,
    content_filename: str = "content.txt",
    pause_dirname: str = "_paused",
    detection_hash: str | None = None,
) -> AcquisitionManifest:
    """Execute the primitive sequence and write manifest + content.

    Writes:
    - ``<output_dir>/manifest.json``
    - ``<output_dir>/<content_filename>`` (on success)
    - ``<output_dir>/<pause_dirname>/state.json`` + ``request.md`` on pause
    """

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = AcquisitionManifest(
        source_reference=source_reference,
        source_type=source_type,
        scope_requested=scope,
        detection_hash=detection_hash,
    )

    # Running accumulator of source metrics sniffed from primitive
    # summaries (fetched bytes, page counts). Injected into each
    # primitive's ``previous.meta`` under ``_source_metrics`` so
    # downstream primitives (notably ``verify_extraction_quality``'s
    # completeness check) can consume them without every intervening
    # primitive having to forward-propagate fields explicitly.
    source_metrics: dict[str, Any] = {}

    previous: PrimitiveResult | None = None
    for prim in primitives:
        if previous is not None:
            previous.meta["_source_metrics"] = dict(source_metrics)
        entry = PrimitiveTraceEntry(
            primitive=prim.name,
            inputs=_primitive_inputs_summary(scope, prim),
        )
        t0 = time.perf_counter()
        try:
            prim.validate_scope(scope)
            result = prim.run(scope, previous)
        except ScopeValidationError as exc:
            entry.error = f"scope_validation: missing {exc.missing}"
            entry.duration_ms = int((time.perf_counter() - t0) * 1000)

            pause_dir = out_dir / pause_dirname
            pause = PauseState(
                primitive=prim.name,
                reason="scope_missing_required_fields",
                needed=(
                    "Primitive "
                    f"`{prim.name}` requires the following scope fields, "
                    "which are missing or empty:\n"
                    + "\n".join(f"- `{m}`" for m in exc.missing)
                    + "\n\nAdd them to the scope spec and re-run."
                ),
                expected_format="scope_fields",
                resume_hint=(
                    f"Create `provided.json` in `{pause_dir}` with the fields "
                    "above, then re-invoke Phase 0 with the updated scope."
                ),
                state_dir=str(pause_dir),
                source_reference=source_reference,
                extra={"missing_fields": exc.missing, "primitive": prim.name},
            )
            paths = write_pause_state(pause_dir, pause)
            entry.user_interaction = UserInteraction(
                primitive=prim.name,
                needed=pause.needed,
                request_file=paths["request_file"],
            )
            manifest.append_trace(entry)
            _write_manifest(manifest, out_dir)
            raise Phase0Paused(
                manifest,
                str(pause_dir),
                f"Phase 0 paused: scope_validation on {prim.name}",
            ) from exc
        except Exception as exc:
            entry.error = f"{type(exc).__name__}: {exc}"
            entry.duration_ms = int((time.perf_counter() - t0) * 1000)
            manifest.append_trace(entry)
            _write_manifest(manifest, out_dir)
            raise

        entry.duration_ms = int((time.perf_counter() - t0) * 1000)
        entry.outputs_summary = dict(result.summary)

        # Harvest source metrics from this primitive's summary so
        # downstream primitives see an up-to-date accumulator.
        summary = result.summary or {}
        if "bytes" in summary and "fetched_bytes" not in source_metrics:
            source_metrics["fetched_bytes"] = summary["bytes"]
        if "pages_extracted" in summary:
            pe = summary["pages_extracted"]
            if isinstance(pe, (list, tuple)) and len(pe) == 2:
                source_metrics["pages_extracted"] = list(pe)
                source_metrics["pages_extracted_count"] = (
                    int(pe[1]) - int(pe[0]) + 1
                )
        if "source_page_count" in summary:
            source_metrics["source_page_count"] = summary["source_page_count"]

        if result.meta.get("encoding_detected") is not None:
            manifest.encoding_detected = result.meta["encoding_detected"]
        if result.meta.get("encoding_failure"):
            manifest.encoding_failure = result.meta["encoding_failure"]
        if result.meta.get("content_hash"):
            manifest.content_hash = result.meta["content_hash"]
        if result.meta.get("dom_hash"):
            manifest.dom_hash = result.meta["dom_hash"]

        side_artefacts = result.meta.get("side_artefacts") or []
        for artefact in side_artefacts:
            filename = artefact.get("filename")
            payload = artefact.get("bytes")
            if not filename or not isinstance(payload, (bytes, bytearray)):
                continue
            target = out_dir / filename
            target.write_bytes(bytes(payload))
            if artefact.get("list_in_content_files"):
                rel = str(target)
                if rel not in manifest.content_files:
                    manifest.content_files.append(rel)
        if result.meta.get("verification"):
            v = result.meta["verification"]
            manifest.append_verification(
                VerificationEntry(
                    primitive=prim.name,
                    verdict=v.get("verdict", "unknown"),
                    checks_run=v.get("checks", []),
                    details={
                        "sample_failures": v.get("sample_failures", []),
                    },
                )
            )
        if result.meta.get("pause_request"):
            pause: PauseState = result.meta["pause_request"]
            resolved_state_dir = Path(pause.state_dir)
            if not resolved_state_dir.is_absolute():
                resolved_state_dir = out_dir / resolved_state_dir
            pause.state_dir = str(resolved_state_dir)
            paths = write_pause_state(resolved_state_dir, pause)
            entry.user_interaction = UserInteraction(
                primitive=prim.name,
                needed=pause.needed,
                request_file=paths["request_file"],
            )
            manifest.append_trace(entry)
            _write_manifest(manifest, out_dir)
            raise Phase0Paused(
                manifest,
                str(resolved_state_dir),
                f"Phase 0 paused: {pause.reason} on {prim.name}",
            )

        manifest.append_trace(entry)
        previous = result

    final_text = "" if previous is None else str(previous.output or "")
    content_path = out_dir / content_filename
    content_path.write_text(final_text, encoding="utf-8")
    manifest.content_files.append(str(content_path))
    manifest.scope_acquired = {
        "chars": len(final_text),
        "verification_excerpt": _verification_excerpt(final_text),
    }

    _write_manifest(manifest, out_dir)
    return manifest


_VERIFICATION_HEAD_CHARS = 200
_VERIFICATION_TAIL_CHARS = 100


def _verification_excerpt(text: str) -> dict[str, Any]:
    """Canonical verification excerpt written into ``scope_acquired``."""

    if not text:
        return {"first_chars": "", "last_chars": "", "line_count": 0}

    first_chars = text[:_VERIFICATION_HEAD_CHARS]
    if len(text) <= _VERIFICATION_HEAD_CHARS:
        last_chars = ""
    else:
        last_chars = text[-_VERIFICATION_TAIL_CHARS:]
    return {
        "first_chars": first_chars,
        "last_chars": last_chars,
        "line_count": text.count("\n") + (1 if text else 0),
    }


def _write_manifest(manifest: AcquisitionManifest, out_dir: Path) -> None:
    p = out_dir / "manifest.json"
    p.write_text(
        json.dumps(
            manifest.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
