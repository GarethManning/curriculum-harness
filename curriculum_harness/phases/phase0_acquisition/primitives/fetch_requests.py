"""HTTP fetch primitive using ``requests``.

Side-effect tag: ``network``. Respects ``robots.txt`` (best-effort —
we fetch /robots.txt once per host and cache per-process). Sends a
transparent user-agent identifying the tool.

Returns raw bytes (not str) so the downstream ``encoding_detection``
primitive can pick up the declared-encoding + body and produce a
UTF-8 string deterministically.
"""

from __future__ import annotations

import urllib.robotparser
from urllib.parse import urlparse

import requests

from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
    check_required_scope,
)


USER_AGENT = (
    "Curriculum-Harness/0.1 "
    "(+https://github.com/GarethManning/curriculum-harness)"
)

_ROBOTS_CACHE: dict[str, urllib.robotparser.RobotFileParser] = {}


def _robots_allows(url: str, user_agent: str = USER_AGENT) -> tuple[bool, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return True, "non_http_scheme"
    key = f"{parsed.scheme}://{parsed.netloc}"
    rp = _ROBOTS_CACHE.get(key)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{key}/robots.txt")
        try:
            rp.read()
        except Exception as exc:  # noqa: BLE001 — robots.txt absent == allow
            _ROBOTS_CACHE[key] = rp
            return True, f"robots_unreadable: {exc}"
        _ROBOTS_CACHE[key] = rp
    try:
        allowed = rp.can_fetch(user_agent, url)
        return allowed, "allowed" if allowed else "disallowed_by_robots"
    except Exception as exc:  # noqa: BLE001
        return True, f"robots_check_error: {exc}"


class FetchRequestsPrimitive:
    name = "fetch_requests"
    required_scope_fields: tuple[str, ...] = ("url",)
    optional_scope_fields: tuple[str, ...] = ()
    side_effects: frozenset[str] = frozenset({"network"})

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    def validate_scope(self, scope) -> None:
        check_required_scope(self.name, scope, self.required_scope_fields)

    def run(self, scope, previous: PrimitiveResult | None) -> PrimitiveResult:
        url = getattr(scope, "url", None) or getattr(
            scope, "source_reference", None
        )

        allowed, robots_reason = _robots_allows(url)
        if not allowed:
            return PrimitiveResult(
                output=None,
                summary={
                    "status": "blocked_by_robots",
                    "robots_reason": robots_reason,
                    "url": url,
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

        declared = resp.encoding
        content_type = resp.headers.get("content-type", "")

        return PrimitiveResult(
            output=resp.content,
            summary={
                "status": "ok",
                "http_status": resp.status_code,
                "final_url": resp.url,
                "content_type": content_type,
                "declared_encoding": declared,
                "bytes": len(resp.content),
                "robots_reason": robots_reason,
            },
            meta={
                "declared_encoding": declared,
                "final_url": resp.url,
                "http_status": resp.status_code,
                "content_type": content_type,
            },
        )
