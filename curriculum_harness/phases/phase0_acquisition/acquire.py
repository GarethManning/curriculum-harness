"""Phase 0 top-level entry point.

``acquire()`` takes a source reference and a scope spec, detects the
source type, selects the appropriate primitive sequence, and runs it.

For deferred source types, ``acquire()`` writes a user-in-the-loop
pause to the output directory with a message explaining that the
primitive is scheduled for a later session, and raises
``Phase0Paused``. The caller can recover by writing ``provided.txt``
containing the scoped content the user produced by hand.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from curriculum_harness.phases.phase0_acquisition.executor import (
    Phase0Paused,
    _write_manifest,
    run_pipeline,
)
from curriculum_harness.phases.phase0_acquisition.manifest import (
    AcquisitionManifest,
    ScopeSpec,
)
from curriculum_harness.phases.phase0_acquisition.sequences import (
    SEQUENCE_BUILDERS,
)
from curriculum_harness.phases.phase0_acquisition.session_state import (
    PauseState,
    write_pause_state,
)
from curriculum_harness.phases.phase0_acquisition.type_detector import (
    DetectionResult,
    SUPPORTED_IN_SESSION_4A_0,
    detect_source_type,
    unsupported_type_pause_message,
)


def acquire(
    *,
    scope: ScopeSpec,
    output_dir: str | Path,
    content_filename: str = "content.txt",
    detection_override: DetectionResult | None = None,
) -> AcquisitionManifest:
    """Detect → route → run. Returns the acquisition manifest.

    Raises ``Phase0Paused`` when the source type is unsupported or a
    primitive requests user-in-the-loop input.
    """

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detection = detection_override or detect_source_type(scope.source_reference)

    (out_dir / "_detection.json").write_text(
        _detection_as_json(detection),
        encoding="utf-8",
    )

    if detection.source_type not in SUPPORTED_IN_SESSION_4A_0:
        pause_dir = out_dir / "_paused"
        pause = PauseState(
            primitive="type_detector",
            reason="unsupported_source_type_in_session_4a_0",
            needed=unsupported_type_pause_message(
                scope.source_reference, detection
            ),
            expected_format="plain_text",
            resume_hint=(
                f"Option A: write `provided.txt` in `{pause_dir}` with "
                "the scoped content you extracted by hand. Option B: "
                "wait for the Session 4a-N primitive for "
                f"`{detection.source_type}`."
            ),
            state_dir=str(pause_dir),
            source_reference=scope.source_reference,
            extra={
                "detected_source_type": detection.source_type,
                "detection_confidence": detection.confidence,
                "detection_rationale": detection.rationale,
                "detection_signals": detection.signals,
            },
        )
        write_pause_state(pause_dir, pause)

        manifest = AcquisitionManifest(
            source_reference=scope.source_reference,
            source_type=detection.source_type,
            scope_requested=scope,
        )
        manifest.notes = (
            f"Phase 0 paused — source type `{detection.source_type}` is "
            "not supported in Session 4a-0."
        )
        _write_manifest(manifest, out_dir)
        raise Phase0Paused(
            manifest,
            str(pause_dir),
            f"Unsupported source_type: {detection.source_type}",
        )

    builder = SEQUENCE_BUILDERS[detection.source_type]
    primitives = builder(scope)
    manifest = run_pipeline(
        source_reference=scope.source_reference,
        source_type=detection.source_type,
        scope=scope,
        primitives=primitives,
        output_dir=out_dir,
        content_filename=content_filename,
    )
    return manifest


def _detection_as_json(detection: DetectionResult) -> str:
    import json

    payload: dict[str, Any] = {
        "source_type": detection.source_type,
        "confidence": detection.confidence,
        "rationale": detection.rationale,
        "is_supported_now": detection.is_supported_now,
        "signals": detection.signals,
    }
    return json.dumps(payload, indent=2, sort_keys=True)
