"""Heading-section extraction primitive.

For HTML pages where the target section is identified by a stable
heading (``<h1>``..``<h6>``) rather than a unique CSS selector. Returns
the text content between the matched heading and the next heading at
the same or higher level.

Deterministic. No model calls.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
    check_required_scope,
)


_HEADING_LEVELS = ("h1", "h2", "h3", "h4", "h5", "h6")
_STRIP = ("script", "style", "noscript", "nav", "footer", "header")


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _strip_chrome(soup: BeautifulSoup) -> None:
    for tag_name in _STRIP:
        for tag in soup.find_all(tag_name):
            tag.decompose()


def _find_heading(
    soup: BeautifulSoup,
    heading_text: str,
    is_regex: bool,
) -> Tag | None:
    if is_regex:
        pattern = re.compile(heading_text, flags=re.I)
        for h in soup.find_all(_HEADING_LEVELS):
            if pattern.search(h.get_text(strip=True)):
                return h
        return None
    target = heading_text.strip().lower()
    for h in soup.find_all(_HEADING_LEVELS):
        if h.get_text(strip=True).lower() == target:
            return h
    # fallback: loose contains match
    for h in soup.find_all(_HEADING_LEVELS):
        if target in h.get_text(strip=True).lower():
            return h
    return None


def _collect_until_next_heading(start: Tag) -> list[Tag]:
    start_level = int(start.name[1])
    collected: list[Tag] = []
    for sib in start.find_all_next():
        if sib.name in _HEADING_LEVELS:
            level = int(sib.name[1])
            if level <= start_level:
                break
        collected.append(sib)
    return collected


class ExtractHeadingSectionPrimitive:
    name = "extract_heading_section"
    required_scope_fields: tuple[str, ...] = ("heading_text",)
    optional_scope_fields: tuple[str, ...] = ("heading_regex",)
    side_effects: frozenset[str] = frozenset()

    def validate_scope(self, scope) -> None:
        check_required_scope(self.name, scope, self.required_scope_fields)

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        html = "" if previous is None else str(previous.output or "")
        heading_text = scope.heading_text
        is_regex = bool(getattr(scope, "heading_regex", False))
        soup = _soup(html)
        _strip_chrome(soup)

        heading = _find_heading(soup, heading_text, is_regex)
        if heading is None:
            return PrimitiveResult(
                output="",
                summary={
                    "status": "heading_not_found",
                    "heading_text": heading_text,
                    "is_regex": is_regex,
                },
                meta={"heading_match": False},
            )

        texts = [heading.get_text(separator="\n", strip=True)]
        for sib in _collect_until_next_heading(heading):
            t = sib.get_text(separator="\n", strip=True)
            if t:
                texts.append(t)
        combined = "\n\n".join(texts)
        return PrimitiveResult(
            output=combined,
            summary={
                "status": "ok",
                "heading_text": heading_text,
                "heading_level": heading.name,
                "chars_out": len(combined),
            },
            meta={"heading_match": True, "heading_level": heading.name},
        )
