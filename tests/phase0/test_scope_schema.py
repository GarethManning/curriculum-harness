"""Adversarial tests for the Phase 0 0.5.0 scope schema.

Covers Session 4a-4 Step 7's required cases:

1. Construct a valid HtmlNestedDomScope — succeeds.
2. Construct an HtmlNestedDomScope missing required fields — fails.
3. Construct a JsRenderedProgressiveDisclosureScope with PDF-only
   `page_range` — fails (extra="forbid" cross-type smuggling check).
4. Load a 0.4.0 manifest and verify forward-compat upgrade is
   value-stable.
5. Load a 0.5.0 manifest and verify round-trip (load → save → load)
   produces byte-identical JSON.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from curriculum_harness.phases.phase0_acquisition.manifest import (
    AcquisitionManifest,
)
from curriculum_harness.phases.phase0_acquisition.scope import (
    FlatPdfLinearScope,
    HtmlNestedDomScope,
    JsRenderedProgressiveDisclosureScope,
    MultiSectionPdfScope,
    StaticHtmlLinearScope,
    parse_scope,
)


# ---------------------------------------------------------------------------
# Per-variant construction
# ---------------------------------------------------------------------------


def test_html_nested_dom_scope_valid_construction():
    s = HtmlNestedDomScope(
        url="https://example.com/page",
        content_root_selector=".content",
        exclude_selectors=["nav", "footer"],
        section_anchor_selector="#section",
    )
    assert s.source_type == "html_nested_dom"
    assert s.content_root_selector == ".content"
    # source_reference auto-populated from url
    assert s.source_reference == "https://example.com/page"
    assert s.include_details_content is True
    assert s.preserve_headings is True


def test_html_nested_dom_scope_missing_url_fails():
    with pytest.raises(ValidationError):
        HtmlNestedDomScope(content_root_selector=".content")


def test_html_nested_dom_scope_missing_content_root_fails():
    with pytest.raises(ValidationError):
        HtmlNestedDomScope(url="https://example.com/")


def test_html_nested_dom_scope_both_section_mechanisms_fails():
    """Setting both section_scope_selector and section_anchor_selector
    is a configuration error caught at construction time."""

    with pytest.raises(ValidationError) as exc_info:
        HtmlNestedDomScope(
            url="https://example.com/",
            content_root_selector=".content",
            section_scope_selector=".sub",
            section_anchor_selector="#anchor",
        )
    assert "mutually exclusive" in str(exc_info.value)


def test_html_nested_dom_scope_stop_without_anchor_fails():
    with pytest.raises(ValidationError) as exc_info:
        HtmlNestedDomScope(
            url="https://example.com/",
            content_root_selector=".content",
            section_anchor_stop_selector="h2",
        )
    assert "section_anchor_stop_selector" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Cross-type field smuggling rejected (extra="forbid")
# ---------------------------------------------------------------------------


def test_js_rendered_scope_rejects_page_range():
    """page_range is a PDF-only field; placing it on a JS scope must
    fail at construction so the error surfaces at the call site, not
    silently in the primitive."""

    with pytest.raises(ValidationError) as exc_info:
        JsRenderedProgressiveDisclosureScope(
            url="https://example.com/",
            wait_for_selector="main",
            css_selector="main",
            page_range=[1, 5],
        )
    msg = str(exc_info.value)
    assert "page_range" in msg
    assert (
        "extra" in msg.lower()
        or "not permitted" in msg.lower()
        or "forbidden" in msg.lower()
    )


def test_static_html_scope_rejects_pdf_dedup():
    with pytest.raises(ValidationError):
        StaticHtmlLinearScope(
            url="https://example.com/",
            css_selector="main",
            pdf_dedup_coords=True,
        )


def test_flat_pdf_scope_rejects_url_field():
    """FlatPdfLinearScope identifies the source via source_reference;
    a stray url field is rejected to prevent ambiguity."""

    with pytest.raises(ValidationError):
        FlatPdfLinearScope(
            source_reference="/tmp/foo.pdf",
            url="https://example.com/foo.pdf",
        )


def test_html_nested_dom_scope_rejects_wait_for_selector():
    with pytest.raises(ValidationError):
        HtmlNestedDomScope(
            url="https://example.com/",
            content_root_selector=".content",
            wait_for_selector="main",
        )


def test_static_html_requires_one_extractor_field():
    """StaticHtmlLinearScope requires one of css_selector or
    heading_text — neither alone fails."""

    with pytest.raises(ValidationError) as exc_info:
        StaticHtmlLinearScope(url="https://example.com/")
    assert "css_selector" in str(exc_info.value) or "heading_text" in str(
        exc_info.value
    )


def test_multi_section_pdf_requires_one_scoping_field():
    with pytest.raises(ValidationError) as exc_info:
        MultiSectionPdfScope(source_reference="/tmp/foo.pdf")
    assert "page_range" in str(exc_info.value) or "section_" in str(
        exc_info.value
    )


# ---------------------------------------------------------------------------
# Forward-compatible 0.4.0 deserialiser
# ---------------------------------------------------------------------------


def test_parse_scope_upgrades_0_4_0_static_html():
    """A 0.4.0-shaped scope dict (no source_type, with all union fields)
    is upgraded to the right variant via fallback_source_type."""

    raw = {
        "source_reference": "https://example.com/page",
        "url": "https://example.com/page",
        "css_selector": "main",
        "heading_text": None,
        "heading_regex": False,
        "follow_links": False,
        "page_range": None,  # PDF-only field — must be dropped silently
        "pdf_dedup_coords": False,  # default, dropped
        "pdf_dedup_coord_tolerance": 1,  # default, dropped
        "section_heading": None,
        "section_identifier": None,
    }
    s = parse_scope(raw, fallback_source_type="static_html_linear")
    assert isinstance(s, StaticHtmlLinearScope)
    assert s.url == "https://example.com/page"
    assert s.css_selector == "main"
    assert s.source_reference == "https://example.com/page"


def test_parse_scope_upgrades_0_4_0_pdf_with_page_range():
    raw = {
        "source_reference": "/tmp/foo.pdf",
        "url": None,
        "page_range": [40, 55],
        "section_heading": "Foundations",
        "pdf_dedup_coords": True,
        "pdf_dedup_coord_tolerance": 1,
    }
    s = parse_scope(raw, fallback_source_type="flat_pdf_linear")
    assert isinstance(s, FlatPdfLinearScope)
    assert s.page_range == [40, 55]
    assert s.section_heading == "Foundations"
    assert s.pdf_dedup_coords is True


def test_parse_scope_upgrades_0_4_0_with_url_only_in_source_reference():
    """Defensive 0.4.0 path: url is null in scope, source_reference
    carries the URL. Must populate url from source_reference for
    URL-based variants."""

    raw = {
        "source_reference": "https://example.com/page",
        "url": None,
        "css_selector": "main",
    }
    s = parse_scope(raw, fallback_source_type="static_html_linear")
    assert isinstance(s, StaticHtmlLinearScope)
    assert s.url == "https://example.com/page"


def test_parse_scope_rejects_non_default_unknown_field():
    """A 0.4.0 scope smuggling a non-default field meaningful only to
    a different source type must NOT silently lose data — the
    discriminator dispatch raises a clear validation error."""

    raw = {
        "source_reference": "/tmp/foo.pdf",
        "page_range": [1, 5],
        "wait_for_selector": "main",  # JS-only, non-default
    }
    with pytest.raises(ValidationError):
        parse_scope(raw, fallback_source_type="flat_pdf_linear")


# ---------------------------------------------------------------------------
# Manifest 0.4.0 → 0.5.0 round-trip
# ---------------------------------------------------------------------------


_MINIMAL_0_4_0_MANIFEST = {
    "source_reference": "https://example.com/page",
    "source_type": "static_html_linear",
    "scope_requested": {
        # 0.4.0 flat shape (no source_type field on scope; all union
        # fields nullable on the model)
        "source_reference": "https://example.com/page",
        "url": "https://example.com/page",
        "css_selector": "main",
        "heading_text": None,
        "heading_regex": False,
        "follow_links": False,
        "page_range": None,
        "section_heading": None,
        "section_identifier": None,
        "pdf_dedup_coords": False,
        "pdf_dedup_coord_tolerance": 1,
        "notes": "0.4.0-shaped fixture",
    },
    "primitive_sequence": ["fetch_requests", "extract_css_selector"],
    "content_files": [],
    "phase0_version": "0.4.0",
}


def test_manifest_loads_0_4_0_and_upgrades_scope_in_place():
    m = AcquisitionManifest.model_validate(_MINIMAL_0_4_0_MANIFEST)
    assert m.scope_requested.source_type == "static_html_linear"
    assert isinstance(m.scope_requested, StaticHtmlLinearScope)
    assert m.scope_requested.url == "https://example.com/page"
    assert m.scope_requested.notes == "0.4.0-shaped fixture"


def test_manifest_round_trip_0_5_0_byte_identical():
    """Load → dump → load → dump produces byte-identical JSON.

    Pydantic's deterministic JSON serialisation is the contract here;
    if model_dump_json adds non-deterministic ordering or whitespace,
    downstream content-hash workflows would break.
    """

    m1 = AcquisitionManifest.model_validate(_MINIMAL_0_4_0_MANIFEST)
    json1 = json.dumps(m1.model_dump(mode="json"), indent=2, sort_keys=True)

    m2 = AcquisitionManifest.model_validate(json.loads(json1))
    json2 = json.dumps(m2.model_dump(mode="json"), indent=2, sort_keys=True)

    assert json1 == json2

    # And the scope_requested round-trips via the discriminated union.
    assert isinstance(m2.scope_requested, StaticHtmlLinearScope)
    assert m1.scope_requested.model_dump() == m2.scope_requested.model_dump()


def test_manifest_round_trip_html_nested_dom_variant():
    """Same round-trip property for the html_nested_dom variant."""

    raw = {
        "source_reference": "https://gov.example/page",
        "source_type": "html_nested_dom",
        "scope_requested": {
            "source_type": "html_nested_dom",
            "url": "https://gov.example/page",
            "content_root_selector": ".govspeak",
            "section_anchor_selector": "#key-stage-3",
            "exclude_selectors": [".cookie", ".footer"],
            "preserve_headings": True,
            "include_details_content": True,
            "source_reference": "https://gov.example/page",
        },
        "primitive_sequence": ["fetch_requests", "extract_nested_dom"],
        "content_files": [],
        "phase0_version": "0.5.0",
    }
    m1 = AcquisitionManifest.model_validate(raw)
    j1 = json.dumps(m1.model_dump(mode="json"), indent=2, sort_keys=True)
    m2 = AcquisitionManifest.model_validate(json.loads(j1))
    j2 = json.dumps(m2.model_dump(mode="json"), indent=2, sort_keys=True)
    assert j1 == j2
    assert isinstance(m2.scope_requested, HtmlNestedDomScope)
    assert m2.scope_requested.section_anchor_selector == "#key-stage-3"
