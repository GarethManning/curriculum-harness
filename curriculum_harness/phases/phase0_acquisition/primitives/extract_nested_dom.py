"""Nested-DOM HTML extraction primitive.

Pure capability — given a deep HTML document, navigate to the content
root, optionally narrow to one heading-anchored or container-scoped
sub-section, strip a configurable list of chrome elements, and return
the text content with heading structure preserved.

Site-specific choreography lives in ``HtmlNestedDomScope`` (see
``scope.py``). The primitive itself contains no per-site branching;
if it ever needs ``if site == ...`` to function, that is a design
failure — refactor.

# `<details>` semantics

`<details>` elements are **static HTML**. Their collapsed visual state
is a browser-level rendering default; the contained text is present
in the DOM regardless of whether the element is open or closed. This
is fundamentally different from JavaScript-rendered accordions
(`<div role="accordion">`, custom-element accordions, mat-expansion-
panels) whose collapsed content is *not* in the static HTML and
requires the browser primitive (`fetch_via_browser` +
`click_sequence`) to materialise.

The primitive's `include_details_content` flag (default True) is
explicit so the behaviour is auditable in the manifest's
acquisition trace. Setting it False excludes the inner content of
every `<details>` element while preserving the `<summary>` text — the
right behaviour for sources where collapsed sections are intentionally
out-of-scope (e.g. supplementary downloads on a gov.uk publication).

# Heading-anchor scoping

For pages where a sub-section is delimited by sibling headings rather
than wrapped in a dedicated container element (the gov.uk pattern —
KS3 content lives between `<h2 id="key-stage-3">` and `<h2 id="key-
stage-4">` as flat children of `.govspeak`), pass
``section_anchor_selector="#key-stage-3"`` and let
``section_anchor_stop_selector`` default to the anchor's own tag
(``"h2"``). The primitive walks following siblings from the anchor
through to (but not including) the next element matching the stop
selector.

# Deterministic, no model calls

This module imports only ``bs4`` and the project's primitive base.
There is no fetcher, no network call, no LLM. Input is a UTF-8 HTML
string from the upstream encoding-detection step.
"""

from __future__ import annotations

from typing import Any, Iterable

from bs4 import BeautifulSoup, NavigableString, Tag

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
    ScopeValidationError,
)
from curriculum_harness.phases.phase0_acquisition.session_state import (
    PauseState,
)


# Tags whose textual content is removed by default (overridable via
# scope.exclude_selectors). These are universal "this is markup, not
# content" tags; per-site chrome lives in scope.exclude_selectors.
_DEFAULT_STRIP_TAGS: tuple[str, ...] = ("script", "style", "noscript")


def _to_soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _resolve_root(soup: BeautifulSoup, content_root_selector: str) -> Tag | None:
    matches = soup.select(content_root_selector)
    if not matches:
        return None
    # Multiple matches are unusual on curriculum pages; take the first
    # but record the count in the trace so a downstream review can
    # spot misconfiguration.
    return matches[0]


def _resolve_section(
    root: Tag,
    *,
    section_scope_selector: str | None,
    section_anchor_selector: str | None,
    section_anchor_stop_selector: str | None,
) -> tuple[list[Tag | NavigableString], dict[str, Any]]:
    """Narrow ``root`` to the configured sub-section, if any.

    Returns ``(elements, meta)`` where ``elements`` is the ordered list
    of direct children to extract from. ``meta`` records what
    mechanism was used and what was matched, for the manifest trace.
    """

    if section_scope_selector and section_anchor_selector:
        # The scope model already enforces this exclusivity, but
        # belt-and-braces against future code paths.
        raise ScopeValidationError(
            "extract_nested_dom",
            ["section_scope_selector", "section_anchor_selector"],
            message=(
                "extract_nested_dom: set at most one of "
                "section_scope_selector and section_anchor_selector."
            ),
        )

    if section_scope_selector:
        matches = root.select(section_scope_selector)
        if not matches:
            return [], {
                "section_mechanism": "container",
                "section_scope_selector": section_scope_selector,
                "section_match_count": 0,
            }
        container = matches[0]
        return [container], {
            "section_mechanism": "container",
            "section_scope_selector": section_scope_selector,
            "section_match_count": len(matches),
        }

    if section_anchor_selector:
        anchor_matches = root.select(section_anchor_selector)
        if not anchor_matches:
            return [], {
                "section_mechanism": "heading_anchor",
                "section_anchor_selector": section_anchor_selector,
                "section_anchor_match_count": 0,
            }
        anchor = anchor_matches[0]
        stop_selector = section_anchor_stop_selector or anchor.name
        elements = _walk_anchor_section(anchor, stop_selector)
        return elements, {
            "section_mechanism": "heading_anchor",
            "section_anchor_selector": section_anchor_selector,
            "section_anchor_stop_selector": stop_selector,
            "section_anchor_match_count": len(anchor_matches),
            "section_anchor_element_count": len(elements),
        }

    return list(root.children), {"section_mechanism": "whole_root"}


def _walk_anchor_section(anchor: Tag, stop_selector: str) -> list[Tag | NavigableString]:
    """Take the anchor and following siblings until a stop element.

    The stop selector is matched against each sibling — the first
    sibling whose ``Tag.name`` equals the stop selector (or whose
    own ``select_one(stop_selector)`` would match the sibling itself)
    terminates the section. The terminator is *not* included.
    """

    out: list[Tag | NavigableString] = [anchor]
    sibling = anchor.next_sibling
    while sibling is not None:
        if isinstance(sibling, Tag):
            if _sibling_matches_stop(sibling, stop_selector):
                break
        out.append(sibling)
        sibling = sibling.next_sibling
    return out


def _sibling_matches_stop(sibling: Tag, stop_selector: str) -> bool:
    """Stop heuristic.

    Two-step: bare tag-name match (the common case — stop on the next
    `h2`) plus a selector match against the sibling itself. The latter
    catches CSS-classed stop conditions like ``"section.next-stage"``
    where a tag-name check would not be enough.
    """

    if sibling.name == stop_selector:
        return True
    try:
        return bool(sibling.select_one(f":scope.{stop_selector.lstrip('.')}")) and (
            stop_selector.startswith(".")
            and stop_selector.lstrip(".") in (sibling.get("class") or [])
        )
    except Exception:  # noqa: BLE001 — defensive
        return False


def _strip_excluded(
    elements: Iterable[Tag | NavigableString],
    exclude_selectors: list[str],
) -> dict[str, int]:
    """In-place removal of elements matching the exclude selectors.

    Returns a count summary so the manifest trace can record what was
    dropped (load-bearing for the chrome-exclusion verification check
    in Step 8).
    """

    counts: dict[str, int] = {}
    for selector in exclude_selectors:
        total = 0
        for el in elements:
            if not isinstance(el, Tag):
                continue
            for match in el.select(selector):
                match.decompose()
                total += 1
            # Also handle the case where the element itself matches.
            if el.parent is not None and el in el.parent.find_all(True):
                if _element_matches_selector(el, selector):
                    el.decompose()
                    total += 1
        counts[selector] = total
    return counts


def _element_matches_selector(el: Tag, selector: str) -> bool:
    """Whether ``el`` itself (not its descendants) matches ``selector``."""

    parent = el.parent
    if parent is None:
        return False
    return any(m is el for m in parent.select(selector))


def _strip_default_tags(elements: Iterable[Tag | NavigableString]) -> int:
    """Always strip <script>/<style>/<noscript>; return total dropped."""

    total = 0
    for el in elements:
        if not isinstance(el, Tag):
            continue
        for tag_name in _DEFAULT_STRIP_TAGS:
            for m in el.find_all(tag_name):
                m.decompose()
                total += 1
    return total


def _handle_details(
    elements: Iterable[Tag | NavigableString],
    *,
    include_details_content: bool,
) -> dict[str, int]:
    """Inventory `<details>` elements and optionally hide their content.

    With ``include_details_content=True`` (the default) the elements are
    left intact — `<details>` content is static HTML and BeautifulSoup
    extracts it by default. The function only counts them for the
    trace.

    With ``include_details_content=False``, the inner content of each
    `<details>` is removed but the `<summary>` text is preserved,
    matching the visual experience of a closed-by-default disclosure.
    """

    found = 0
    summaries_kept = 0
    for el in elements:
        if not isinstance(el, Tag):
            continue
        for d in el.find_all("details"):
            found += 1
            if include_details_content:
                continue
            summary = d.find("summary")
            if summary is not None:
                summaries_kept += 1
                # Replace the <details> with just its <summary>.
                summary.extract()
                d.replace_with(summary)
            else:
                d.decompose()
    return {"details_found": found, "details_summaries_kept": summaries_kept}


def _extract_text(
    elements: Iterable[Tag | NavigableString],
    *,
    preserve_headings: bool,
) -> str:
    """Walk the surviving DOM and emit text with heading structure intact.

    BeautifulSoup's ``get_text(separator="\\n", strip=True)`` already
    preserves block-level boundaries as newlines. Heading preservation
    is achieved by inserting a blank line before every heading tag the
    walker encounters, which downstream tooling can use to detect
    section boundaries without re-parsing the HTML.
    """

    parts: list[str] = []
    for el in elements:
        if isinstance(el, Tag):
            if preserve_headings:
                # Insert a marker newline before each heading.
                for h in el.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                    h.insert_before("\n\n")
            text = el.get_text(separator="\n", strip=True)
            if text:
                parts.append(text)
        elif isinstance(el, NavigableString):
            s = str(el).strip()
            if s:
                parts.append(s)
    return "\n\n".join(parts)


class ExtractNestedDomPrimitive:
    """Phase 0 primitive for ``html_nested_dom`` extraction.

    Reads ``HtmlNestedDomScope`` (see ``scope.py``):

    - ``content_root_selector`` (required)
    - ``exclude_selectors`` (optional)
    - ``section_scope_selector`` OR ``section_anchor_selector``
      (optional; mutually exclusive)
    - ``section_anchor_stop_selector`` (optional; defaults to
      ``section_anchor_selector``'s own tag name)
    - ``include_details_content`` (default True)
    - ``preserve_headings`` (default True)
    """

    name = "extract_nested_dom"
    required_scope_fields: tuple[str, ...] = ("content_root_selector",)
    optional_scope_fields: tuple[str, ...] = (
        "exclude_selectors",
        "section_scope_selector",
        "section_anchor_selector",
        "section_anchor_stop_selector",
        "include_details_content",
        "preserve_headings",
    )
    side_effects: frozenset[str] = frozenset()

    def validate_scope(self, scope) -> None:
        root = getattr(scope, "content_root_selector", None)
        if not root or not str(root).strip():
            raise ScopeValidationError(
                self.name,
                ["content_root_selector"],
                message=(
                    "extract_nested_dom requires `content_root_selector` "
                    "(the CSS selector for the deep content container)."
                ),
            )

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        html = "" if previous is None else str(previous.output or "")
        soup = _to_soup(html)
        root = _resolve_root(soup, scope.content_root_selector)
        if root is None:
            pause = PauseState(
                primitive=self.name,
                reason="content_root_no_match",
                needed=(
                    f"`extract_nested_dom`: `content_root_selector` "
                    f"`{scope.content_root_selector}` matched no elements "
                    "in the fetched HTML. Inspect the page in a browser "
                    "(view-source) and pick a selector that does match. "
                    "The investigation memo for this source should record "
                    "the working selector chain."
                ),
                expected_format="scope_fields",
                resume_hint=(
                    "Edit `content_root_selector` in the scope and re-run."
                ),
                state_dir="_paused",
                source_reference=getattr(scope, "url", "")
                or getattr(scope, "source_reference", ""),
                extra={"content_root_selector": scope.content_root_selector},
            )
            return PrimitiveResult(
                output="",
                summary={
                    "status": "no_root_match",
                    "content_root_selector": scope.content_root_selector,
                    "html_bytes": len(html),
                },
                meta={
                    "extract_nested_dom_root_match_count": 0,
                    "pause_request": pause,
                },
            )

        # Surface multi-match for content_root in the trace as a soft
        # signal — does not pause but the v3 review wanted it visible.
        root_match_count = len(soup.select(scope.content_root_selector))

        elements, section_meta = _resolve_section(
            root,
            section_scope_selector=getattr(scope, "section_scope_selector", None),
            section_anchor_selector=getattr(scope, "section_anchor_selector", None),
            section_anchor_stop_selector=getattr(
                scope, "section_anchor_stop_selector", None
            ),
        )
        if not elements:
            tried_selector = (
                getattr(scope, "section_scope_selector", None)
                or getattr(scope, "section_anchor_selector", None)
            )
            mech = section_meta.get("section_mechanism", "?")
            pause = PauseState(
                primitive=self.name,
                reason="section_scope_no_match",
                needed=(
                    f"`extract_nested_dom`: section scoping ({mech}) with "
                    f"selector `{tried_selector}` matched no elements "
                    f"under content root `{scope.content_root_selector}`. "
                    "Either the page structure shifted or the selector "
                    "is wrong. Verify against view-source and update the "
                    "scope. To extract the whole content root with no "
                    "section narrowing, clear the section_* fields."
                ),
                expected_format="scope_fields",
                resume_hint=(
                    "Edit `section_scope_selector` or "
                    "`section_anchor_selector` (one only) in the scope "
                    "and re-run, OR clear both to extract the whole root."
                ),
                state_dir="_paused",
                source_reference=getattr(scope, "url", "")
                or getattr(scope, "source_reference", ""),
                extra={
                    "section_mechanism": mech,
                    "section_selector": tried_selector,
                    "content_root_selector": scope.content_root_selector,
                },
            )
            return PrimitiveResult(
                output="",
                summary={
                    "status": "no_section_match",
                    "content_root_selector": scope.content_root_selector,
                    **section_meta,
                },
                meta={
                    "extract_nested_dom_root_match_count": root_match_count,
                    "pause_request": pause,
                    **section_meta,
                },
            )

        excluded = _strip_excluded(
            elements, getattr(scope, "exclude_selectors", None) or []
        )
        default_stripped = _strip_default_tags(elements)
        details_meta = _handle_details(
            elements,
            include_details_content=bool(
                getattr(scope, "include_details_content", True)
            ),
        )
        text = _extract_text(
            elements,
            preserve_headings=bool(getattr(scope, "preserve_headings", True)),
        )

        # Empty extraction after exclusions is a recoverable error —
        # the chrome list probably over-stripped.
        if not text.strip():
            pause = PauseState(
                primitive=self.name,
                reason="extracted_content_empty_after_exclusions",
                needed=(
                    "`extract_nested_dom`: extracted text is empty after "
                    "`exclude_selectors` were applied. The chrome list "
                    "is probably too aggressive — review the strip counts "
                    f"in the trace ({excluded}) and tighten the "
                    "exclude_selectors so they target only chrome, not "
                    "the content body."
                ),
                expected_format="scope_fields",
                resume_hint=(
                    "Reduce `exclude_selectors` and re-run. The investigation "
                    "memo for this source should be the source of truth for "
                    "the chrome list."
                ),
                state_dir="_paused",
                source_reference=getattr(scope, "url", "")
                or getattr(scope, "source_reference", ""),
                extra={"exclude_counts": excluded},
            )
            return PrimitiveResult(
                output="",
                summary={
                    "status": "empty_after_exclusions",
                    "exclude_counts": excluded,
                    **details_meta,
                    **section_meta,
                },
                meta={
                    "extract_nested_dom_root_match_count": root_match_count,
                    "pause_request": pause,
                    "extract_nested_dom_excluded": excluded,
                },
            )

        return PrimitiveResult(
            output=text,
            summary={
                "status": "ok",
                "content_root_selector": scope.content_root_selector,
                "chars_out": len(text),
                "exclude_counts": excluded,
                "default_tags_stripped": default_stripped,
                "root_match_count": root_match_count,
                **details_meta,
                **section_meta,
            },
            meta={
                "extract_nested_dom_root_match_count": root_match_count,
                "extract_nested_dom_section_meta": section_meta,
                "extract_nested_dom_excluded": excluded,
                "extract_nested_dom_details": details_meta,
            },
        )
