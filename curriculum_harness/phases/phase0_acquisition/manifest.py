"""Phase 0 manifest schema.

Every acquisition produces two kinds of artefact:

- A manifest JSON with metadata (this module's ``AcquisitionManifest``).
- One or more content text files referenced by the manifest via path.

The manifest is the source of truth for how an acquisition ran — source
reference, scope requested vs acquired, primitive sequence, per-primitive
trace, content hash, encoding, and any user interactions. Downstream
consumers never read raw URLs; they read manifest + content files.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


SourceType = Literal[
    "static_html_linear",
    "flat_pdf_linear",
    "multi_section_pdf",
    "js_rendered_progressive_disclosure",
    "html_nested_dom",
    "unknown",
]


# Append-only enum of PDF pathologies Phase 0 knows how to handle.
#
# Adding a new value is a deliberate act: it means we have empirically
# observed the pathology in a real source and have chosen a
# deterministic primitive configuration that handles it. Do not add
# speculative values. Manifests may only reference values in this
# enum — the Pydantic model validates on write.
#
# - ``coordinate_level_footer_overlap`` — PDF renders header/footer
#   glyphs twice at near-identical coordinates. Observed in the AP US
#   Gov CED (Session 4a-2a). Handled by
#   ``extract_pdf_text_deduped`` with
#   ``pdf_dedup_coord_tolerance=1``.
# - ``coordinate_level_general_overlap`` — coordinate-level glyph
#   overlap beyond headers/footers (e.g. AODA PDFs with accessibility
#   overlays rendering body text twice). Reserved; not yet observed.
# - ``character_stream_doubling`` — doubling at the content-stream
#   level (Mechanism C in the 4a-2a investigation memo). Reserved;
#   not yet observed in any test source.
# - ``aoda_tagged_content_overlap`` — AODA structure-tagging that
#   produces invisible-text overlap alongside visible text. Reserved.
KnownPathology = Literal[
    "coordinate_level_footer_overlap",
    "coordinate_level_general_overlap",
    "character_stream_doubling",
    "aoda_tagged_content_overlap",
]


class ClickStepWaitFor(BaseModel):
    """Signal a click step waits on before being considered complete.

    ``selector_appears`` — wait for ``value`` (a CSS selector) to be
    present and visible in the DOM.
    ``network_idle`` — wait for the browser to hit a networkidle state
    after the click; ``value`` is ignored and may be empty.

    Session 4a-3 v3 intentionally has no ``timeout_ms`` enum member:
    wait conditions fire on a signal. Timeouts are bounded at the click
    step level and the primitive level, not here.
    """

    type: Literal["selector_appears", "network_idle"]
    value: str = ""


class ClickStep(BaseModel):
    """One entry in the ``fetch_via_browser`` primitive's click_sequence.

    Each click is recorded individually in the manifest trace for
    observability. If a step fails and ``retry_on_fail`` is True, the
    primitive retries the click once after a 1-second backoff before
    pausing Phase 0.

    ``timeout_ms`` bounds the whole step (the click + its wait_for). If
    None, the primitive's overall ``browser_timeout_ms`` is used as the
    bound.
    """

    selector: str
    wait_for: ClickStepWaitFor
    retry_on_fail: bool = True
    timeout_ms: int | None = None


class ScopeSpec(BaseModel):
    """Structured scope specification.

    Free-text scope is rejected by design. Each primitive declares its
    required/optional fields; ``ScopeSpec`` carries the union. Primitives
    validate the subset they need and raise ``ScopeValidationError`` on
    missing fields, which Phase 0 converts to a user-in-the-loop request.
    """

    source_reference: str = Field(
        description="URL or local file path to acquire from.",
    )
    url: str | None = Field(
        default=None,
        description="Explicit URL (overrides source_reference if set).",
    )
    css_selector: str | None = Field(
        default=None,
        description="CSS selector identifying the target content block.",
    )
    heading_text: str | None = Field(
        default=None,
        description="Heading text (or regex) marking the section start.",
    )
    heading_regex: bool = Field(
        default=False,
        description="Interpret heading_text as a regex.",
    )
    page_range: list[int] | str | None = Field(
        default=None,
        description=(
            "PDF page range. Preferred form: ``[start, end]`` (1-indexed, "
            "inclusive on both ends). String form ``'start-end'`` is "
            "accepted for legacy configs."
        ),
    )
    section_heading: str | None = Field(
        default=None,
        description=(
            "Section heading (literal or regex) to scope a PDF extraction. "
            "Used by PDF primitives; interpreted as a regex if "
            "heading_regex is True."
        ),
    )
    section_identifier: str | None = Field(
        default=None,
        description="Source-internal section id. Reserved for future primitives.",
    )
    follow_links: bool = Field(
        default=False,
        description="Whether to follow sub-links into deeper content.",
    )
    notes: str | None = Field(
        default=None,
        description="Human-readable note about why this scope was chosen.",
    )
    pdf_dedup_coords: bool = Field(
        default=False,
        description=(
            "When True, route PDF extraction through the "
            "``extract_pdf_text_deduped`` primitive instead of the fast "
            "``extract_pdf_text`` path. Use for PDFs where the source "
            "renders text twice at identical coordinates (e.g. overlaid "
            "headers/footers). See Session 4a-2a investigation memo."
        ),
    )
    pdf_dedup_coord_tolerance: int = Field(
        default=1,
        description=(
            "Coordinate rounding precision in pixels used by the deduped "
            "extraction primitive to identify overlapping characters. "
            "Only read when ``pdf_dedup_coords`` is True."
        ),
    )
    wait_for_selector: str | None = Field(
        default=None,
        description=(
            "CSS selector that must appear (and be visible) before the "
            "``fetch_via_browser`` primitive proceeds. Distinct from "
            "``css_selector`` (which is the extraction selector) — the "
            "two are often the same CSS string but mean different things "
            "to different primitives. Required for ``fetch_via_browser``."
        ),
    )
    dismiss_modal_selector: str | None = Field(
        default=None,
        description=(
            "CSS selector for a consent modal / cookie banner to dismiss "
            "before extraction. Optional on ``fetch_via_browser``. If the "
            "element is not found or not visible, the primitive continues "
            "without failing — the field is advisory."
        ),
    )
    click_sequence: list[ClickStep] | None = Field(
        default=None,
        description=(
            "Ordered list of clicks the browser primitive performs after "
            "the initial render and modal dismissal. Each step declares a "
            "wait condition (selector_appears or network_idle) that "
            "signals readiness for the next step. One step per click "
            "(observability beats terseness — the Session 4a-3 review "
            "chose this explicitly)."
        ),
    )
    browser_timeout_ms: int = Field(
        default=30000,
        description=(
            "Overall timeout for ``fetch_via_browser`` in milliseconds. "
            "Covers initial navigation, wait_for_selector, modal dismissal, "
            "and per-click step bounds when a step has no explicit "
            "timeout_ms."
        ),
    )

    @field_validator("click_sequence", mode="before")
    @classmethod
    def _coerce_click_sequence(
        cls, value: Any
    ) -> list[ClickStep] | None:
        if value is None:
            return None
        if isinstance(value, list):
            return [
                ClickStep.model_validate(item) if not isinstance(item, ClickStep) else item
                for item in value
            ]
        raise TypeError("click_sequence must be a list")


class UserInteraction(BaseModel):
    """Record of a user-in-the-loop pause and resume."""

    primitive: str
    needed: str
    request_file: str | None = None
    provided_file: str | None = None
    resolved: bool = False
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


class PrimitiveTraceEntry(BaseModel):
    """Per-primitive trace entry in the acquisition trace."""

    primitive: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs_summary: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 0
    error: str | None = None
    user_interaction: UserInteraction | None = None
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


class VerificationEntry(BaseModel):
    """Per-verification-primitive entry in the verification trace.

    Schema 0.3.0 (Session 4a-2a): records what checks ran on
    extracted content and what verdict they returned. Separate from
    ``acquisition_trace`` so downstream consumers can distinguish
    'content was verified clean' from 'content was produced but not
    verified' by inspecting this field alone.
    """

    primitive: str
    verdict: str = Field(
        description="One of: 'clean', 'suspicious', 'failed'.",
    )
    checks_run: list[dict[str, Any]] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


class AcquisitionManifest(BaseModel):
    """Top-level manifest for a single Phase 0 acquisition.

    ``scope_acquired`` is a dict whose canonical shape is:

    - ``chars`` — int, total characters of extracted content.
    - ``verification_excerpt`` — dict with ``first_chars`` (first 200
      characters), ``last_chars`` (last 100 characters) and
      ``line_count``. A lightweight, stable summary for visual
      inspection without reading the full content file.

    ``detection_hash`` is the SHA-256 of the ``_detection.json`` payload
    written alongside the manifest, so the type-detector output is
    tamper-evident and part of the audit trail.
    """

    source_reference: str
    source_type: SourceType
    scope_requested: ScopeSpec
    scope_acquired: dict[str, Any] = Field(default_factory=dict)
    primitive_sequence: list[str] = Field(default_factory=list)
    acquisition_trace: list[PrimitiveTraceEntry] = Field(default_factory=list)
    verification_trace: list[VerificationEntry] = Field(default_factory=list)
    content_files: list[str] = Field(default_factory=list)
    content_hash: str | None = None
    detection_hash: str | None = None
    encoding_detected: str | None = None
    encoding_failure: str | None = None
    user_interactions: list[UserInteraction] = Field(default_factory=list)
    known_pathology_handling: list[KnownPathology] = Field(
        default_factory=list,
        description=(
            "PDF pathologies the acquisition was configured to handle. "
            "Values are drawn from the append-only ``KnownPathology`` "
            "enum. Empty list if none."
        ),
    )
    investigation_memo_refs: list[str] = Field(
        default_factory=list,
        description=(
            "Paths to diagnostic memos relevant to this acquisition "
            "(e.g. a record of the investigation that identified a "
            "pathology). Empty list if none."
        ),
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    phase0_version: str = "0.4.0"
    notes: str | None = None

    def append_trace(self, entry: PrimitiveTraceEntry) -> None:
        self.acquisition_trace.append(entry)
        if entry.primitive not in self.primitive_sequence:
            self.primitive_sequence.append(entry.primitive)
        if entry.user_interaction is not None:
            self.user_interactions.append(entry.user_interaction)

    def append_verification(self, entry: VerificationEntry) -> None:
        self.verification_trace.append(entry)
