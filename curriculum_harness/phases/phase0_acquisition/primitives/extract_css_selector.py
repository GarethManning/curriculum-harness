"""CSS-selector extraction primitive.

Takes a UTF-8 HTML string (the output of ``encoding_detection`` run on
``fetch_requests`` bytes) and returns the plain-text content of elements
matched by a CSS selector. Strips <script>, <style>, <noscript>, and
<nav> / <footer> / <header> by default before extraction.

Deterministic. No model calls.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
    ScopeValidationError,
    check_required_scope,
)


_DEFAULT_STRIP = ("script", "style", "noscript", "nav", "footer", "header")


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _strip_chrome(soup: BeautifulSoup) -> None:
    for tag_name in _DEFAULT_STRIP:
        for tag in soup.find_all(tag_name):
            tag.decompose()


def _element_text(el) -> str:
    # get_text with separator="\n" collapses inline runs to single
    # whitespace but keeps block boundaries as newlines, which the
    # normalise_whitespace primitive downstream will tidy.
    return el.get_text(separator="\n", strip=True)


class ExtractCssSelectorPrimitive:
    name = "extract_css_selector"
    required_scope_fields: tuple[str, ...] = ("css_selector",)
    optional_scope_fields: tuple[str, ...] = ()
    side_effects: frozenset[str] = frozenset()

    def validate_scope(self, scope) -> None:
        # Special case: this primitive's "css_selector" is only required
        # when it is in the active primitive sequence. The scope may
        # instead carry heading_text for the sibling primitive. Accept
        # either.
        if not getattr(scope, "css_selector", None) and not getattr(
            scope, "heading_text", None
        ):
            raise ScopeValidationError(
                self.name,
                ["css_selector"],
                message=(
                    "Primitive 'extract_css_selector' requires "
                    "`css_selector`, or a sibling `extract_heading_section` "
                    "primitive using `heading_text`."
                ),
            )
        # If heading_text is set and css_selector is not, we still need
        # the caller to route to extract_heading_section. That's a
        # wiring error, not a scope error — raise a distinct message.
        check_required_scope(self.name, scope, ("css_selector",))

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        html = "" if previous is None else str(previous.output or "")
        selector = scope.css_selector
        soup = _soup(html)
        _strip_chrome(soup)
        matches = soup.select(selector)
        if not matches:
            return PrimitiveResult(
                output="",
                summary={
                    "status": "no_matches",
                    "selector": selector,
                    "html_bytes": len(html),
                },
                meta={"selector_match_count": 0},
            )
        texts = [_element_text(m) for m in matches]
        combined = "\n\n".join(t for t in texts if t.strip())
        return PrimitiveResult(
            output=combined,
            summary={
                "status": "ok",
                "selector": selector,
                "match_count": len(matches),
                "chars_out": len(combined),
            },
            meta={"selector_match_count": len(matches)},
        )
