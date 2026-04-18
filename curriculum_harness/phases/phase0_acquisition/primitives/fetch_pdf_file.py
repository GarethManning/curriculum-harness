"""PDF-bytes acquisition primitive.

Accepts either an HTTP(S) URL or a local filesystem path in
``scope.source_reference`` (with ``scope.url`` taking precedence if set
for URL acquisition). Returns raw PDF bytes to the next primitive.

Side-effect tag: ``network`` for URL sources, ``fs_read`` for local
paths. Respects robots.txt (best-effort, per-host cached) for URL
acquisition. Sends the same transparent user-agent as
``fetch_requests``.

Deterministic: no model calls, no content interpretation. Downstream
``extract_pdf_text`` is responsible for turning the bytes into text
with pdfplumber.
"""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import requests

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
    ScopeValidationError,
)
from curriculum_harness.phases.phase0_acquisition.primitives.fetch_requests import (
    USER_AGENT,
    _robots_allows,
)


_PDF_MAGIC = b"%PDF-"


def _is_url(reference: str) -> bool:
    parsed = urlparse(reference)
    return parsed.scheme in {"http", "https"}


class FetchPdfFilePrimitive:
    """Fetch a PDF by URL or load it from a local file path.

    Scope:
        - ``source_reference`` (required): URL or local filesystem path.
        - ``url`` (optional): if set, overrides ``source_reference`` for
          URL acquisition.

    Output: raw PDF bytes. ``meta`` carries fetch provenance —
    ``final_url`` (URL case) or ``source_path`` (file case), content
    type, HTTP status, and a ``content_type_mismatch`` flag when a URL
    fetch returns something other than ``application/pdf``.
    """

    name = "fetch_pdf_file"
    required_scope_fields: tuple[str, ...] = ("source_reference",)
    optional_scope_fields: tuple[str, ...] = ("url",)
    side_effects: frozenset[str] = frozenset({"network", "fs_read"})

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout

    def validate_scope(self, scope) -> None:
        ref = getattr(scope, "url", None) or getattr(scope, "source_reference", None)
        if not ref or not str(ref).strip():
            raise ScopeValidationError(self.name, ["source_reference"])

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        # PDF scope variants in 0.5.0 only have ``source_reference``;
        # legacy or HTML-typed scopes may also expose ``url``.
        reference = getattr(scope, "url", None) or scope.source_reference
        if _is_url(reference):
            return self._run_url(reference)
        return self._run_path(reference)

    def _run_url(self, url: str) -> PrimitiveResult:
        allowed, robots_reason = _robots_allows(url)
        if not allowed:
            return PrimitiveResult(
                output=None,
                summary={
                    "status": "blocked_by_robots",
                    "robots_reason": robots_reason,
                    "url": url,
                    "source_kind": "url",
                },
                meta={"fetch_blocked_by_robots": True},
            )

        resp = requests.get(
            url,
            timeout=self.timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        content_bytes = resp.content
        looks_like_pdf = content_bytes[:5] == _PDF_MAGIC
        content_type_mismatch = not (
            "pdf" in content_type.lower() or looks_like_pdf
        )

        return PrimitiveResult(
            output=content_bytes,
            summary={
                "status": "ok",
                "source_kind": "url",
                "http_status": resp.status_code,
                "final_url": resp.url,
                "content_type": content_type,
                "bytes": len(content_bytes),
                "robots_reason": robots_reason,
                "content_type_mismatch": content_type_mismatch,
                "pdf_magic_ok": looks_like_pdf,
            },
            meta={
                "source_kind": "url",
                "final_url": resp.url,
                "http_status": resp.status_code,
                "content_type": content_type,
                "content_type_mismatch": content_type_mismatch,
                "pdf_magic_ok": looks_like_pdf,
            },
        )

    def _run_path(self, reference: str) -> PrimitiveResult:
        path = Path(reference).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"PDF path does not exist: {path}")
        if not path.is_file():
            raise IsADirectoryError(f"PDF path is not a file: {path}")
        data = path.read_bytes()
        looks_like_pdf = data[:5] == _PDF_MAGIC
        return PrimitiveResult(
            output=data,
            summary={
                "status": "ok",
                "source_kind": "path",
                "source_path": str(path),
                "bytes": len(data),
                "pdf_magic_ok": looks_like_pdf,
            },
            meta={
                "source_kind": "path",
                "source_path": str(path),
                "pdf_magic_ok": looks_like_pdf,
            },
        )
