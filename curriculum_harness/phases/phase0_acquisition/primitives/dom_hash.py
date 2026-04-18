"""DOM-level content-hash primitive (Session 4a-3 Step 4).

Runs directly after ``fetch_via_browser`` on JS-rendered source types.
Hashes the full rendered HTML so that downstream consumers can detect
"the page shape changed" independently of "the extracted text changed"
— for example, a JS SPA that renders identical visible text but swaps
an accordion for a tab control would have a different ``dom_hash`` and
the same ``content_hash``.

The rendered HTML is carried through the pipeline via
``previous.meta['rendered_html']``. This primitive does not read or
transform ``previous.output`` — it passes the output through unchanged
so the next primitive (``extract_css_selector``) receives the rendered
HTML to extract text from.

Deterministic. No model calls. No side effects.
"""

from __future__ import annotations

import hashlib

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
)


class DomHashPrimitive:
    name = "dom_hash"
    required_scope_fields: tuple[str, ...] = ()
    optional_scope_fields: tuple[str, ...] = ()
    side_effects: frozenset[str] = frozenset()

    def validate_scope(self, scope) -> None:
        return None

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        rendered_html: str = ""
        if previous is not None:
            # Prefer the dedicated meta field; fall back to output for
            # robustness if a future primitive renames the meta key.
            rendered_html = (
                previous.meta.get("rendered_html") or str(previous.output or "")
            )
        digest = hashlib.sha256(rendered_html.encode("utf-8")).hexdigest()
        passthrough_output = (
            previous.output if previous is not None else ""
        )
        passthrough_meta = dict(previous.meta) if previous is not None else {}
        passthrough_meta["dom_hash"] = digest
        return PrimitiveResult(
            output=passthrough_output,
            summary={
                "dom_hash": digest,
                "rendered_html_bytes": len(rendered_html),
            },
            meta=passthrough_meta,
        )
