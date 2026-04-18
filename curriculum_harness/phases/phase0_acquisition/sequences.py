"""Per-source-type primitive sequences.

A sequence is an ordered list of primitive instances. The executor runs
them in order; each primitive's output becomes the next primitive's
``previous``. New sequences (one per deferred source type) are added
here in later sessions — the executor and manifest do not change.

- ``static_html_linear``  — Session 4a-0.
- ``flat_pdf_linear``     — Session 4a-1 (this module).
"""

from __future__ import annotations

from curriculum_harness.phases.phase0_acquisition.manifest import ScopeSpec
from curriculum_harness.phases.phase0_acquisition.primitives.base import Primitive
from curriculum_harness.phases.phase0_acquisition.primitives.content_hash import (
    ContentHashPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.encoding_detection import (
    EncodingDetectionPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.extract_css_selector import (
    ExtractCssSelectorPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.extract_heading_section import (
    ExtractHeadingSectionPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.extract_pdf_text import (
    ExtractPdfTextPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.extract_pdf_text_deduped import (
    ExtractPdfTextDedupedPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.detect_toc import (
    DetectTocPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.fetch_pdf_file import (
    FetchPdfFilePrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.fetch_requests import (
    FetchRequestsPrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.normalise_whitespace import (
    NormaliseWhitespacePrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.resolve_section_scope import (
    ResolveSectionScopePrimitive,
)
from curriculum_harness.phases.phase0_acquisition.primitives.verify_extraction_quality import (
    VerifyExtractionQualityPrimitive,
)


def static_html_linear_sequence(scope: ScopeSpec) -> list[Primitive]:
    """Build the ``static_html_linear`` primitive chain for this scope.

    Scope must carry ``url`` and exactly one of ``css_selector`` or
    ``heading_text``. Validation raises ``ScopeValidationError`` via the
    extraction primitive when neither is present — the executor
    converts that to a user-in-the-loop pause asking for the missing
    field.

    Required (for this sequence): ``url`` + one of {``css_selector``,
    ``heading_text``}.
    """

    has_selector = bool(scope.css_selector)
    has_heading = bool(scope.heading_text)

    extractor: Primitive
    if has_selector:
        extractor = ExtractCssSelectorPrimitive()
    elif has_heading:
        extractor = ExtractHeadingSectionPrimitive()
    else:
        # Neither provided — use the CSS-selector primitive, which
        # raises ScopeValidationError on css_selector missing. That
        # drives the executor into a pause with a clear request.
        extractor = ExtractCssSelectorPrimitive()

    return [
        FetchRequestsPrimitive(),
        EncodingDetectionPrimitive(),
        extractor,
        VerifyExtractionQualityPrimitive(mode="raw"),
        NormaliseWhitespacePrimitive(),
        VerifyExtractionQualityPrimitive(mode="normalised"),
        ContentHashPrimitive(),
    ]


def flat_pdf_linear_sequence(scope: ScopeSpec) -> list[Primitive]:
    """Build the ``flat_pdf_linear`` primitive chain.

    Required: ``source_reference`` (URL or local path).
    Optional: ``page_range`` ([start, end] or 'start-end'),
    ``section_heading`` (literal or regex via ``heading_regex``).
    When ``pdf_dedup_coords`` is True, swap in the coordinate-level
    dedup extractor for PDFs with overlaid-text footers
    (Session 4a-2a).

    No ``encoding_detection`` primitive: pdfplumber handles PDF
    encoding internally and emits UTF-8 strings. The executor records
    the absence in the trace via the primitive_sequence list (no
    encoding entry) and the manifest's encoding_detected remains None.
    """

    extractor: Primitive
    if getattr(scope, "pdf_dedup_coords", False):
        extractor = ExtractPdfTextDedupedPrimitive()
    else:
        extractor = ExtractPdfTextPrimitive()

    return [
        FetchPdfFilePrimitive(),
        extractor,
        VerifyExtractionQualityPrimitive(mode="raw"),
        NormaliseWhitespacePrimitive(),
        VerifyExtractionQualityPrimitive(mode="normalised"),
        ContentHashPrimitive(),
    ]


def multi_section_pdf_sequence(scope: ScopeSpec) -> list[Primitive]:
    """Build the ``multi_section_pdf`` primitive chain (Session 4a-2b).

    Scope — one of the following must resolve to a page range:

    - ``page_range`` (explicit wins).
    - ``section_identifier`` (exact TOC-entry title match).
    - ``section_heading`` (case-insensitive prefix / regex match).

    If none is supplied and the TOC is detectable, the
    ``resolve_section_scope`` primitive pauses with a user-in-the-loop
    prompt listing the TOC entries. If none is supplied and no TOC,
    the pause explains that the PDF has no section structure and asks
    for ``page_range`` explicitly.

    Multi-pathology handling (Step 8 resolution): Step 3's Ontario
    pre-check found no coordinate-level pathology in the source, so
    dedup defaults off. ``pdf_dedup_coords=True`` in the scope opts
    into ``extract_pdf_text_deduped`` for sources that do exhibit one.
    Chained multi-pathology dedup would require a new primitive and
    is deferred until a source with multiple confirmed pathologies is
    observed in the test corpus.
    """

    extractor: Primitive
    if getattr(scope, "pdf_dedup_coords", False):
        extractor = ExtractPdfTextDedupedPrimitive()
    else:
        extractor = ExtractPdfTextPrimitive()

    return [
        FetchPdfFilePrimitive(),
        DetectTocPrimitive(),
        ResolveSectionScopePrimitive(),
        extractor,
        VerifyExtractionQualityPrimitive(mode="raw"),
        NormaliseWhitespacePrimitive(),
        VerifyExtractionQualityPrimitive(mode="normalised"),
        ContentHashPrimitive(),
    ]


SEQUENCE_BUILDERS = {
    "static_html_linear": static_html_linear_sequence,
    "flat_pdf_linear": flat_pdf_linear_sequence,
    "multi_section_pdf": multi_section_pdf_sequence,
}
