"""Browser-automation fetch primitive (Session 4a-3).

Pure capability: takes a structured scope (URL, wait_for_selector,
optional modal-dismiss selector, optional click sequence, extraction
selector) and returns the rendered-page HTML plus observability
metadata. Site-specific choreography lives in the scope; this primitive
does not branch on target site.

**Fixed viewport.** 1280 × 720. Non-configurable by design — the
rendered-state hash and extraction are tied to the viewport dimensions,
and leaving it configurable invites silent reproducibility breakage.

**Per-click observability.** ``click_sequence`` is a list of individual
click steps, each traced separately (one entry per click in the
manifest). The Session 4a-3 review chose this explicitly over a terser
single-action DSL: when a Phase 0 run pauses on a click failure, we want
to know which click, not "somewhere in the sequence."

**Bot-detection taxonomy.** The primitive recognises three distinct
failure modes and surfaces each with a specific pause reason, rather
than treating them all as generic HTTP failures:

- ``bot_detection_http_403`` — HTTP 403 on initial navigation. Usually
  means the site's WAF has flagged the user-agent.
- ``bot_detection_challenge_page`` — response body contains Cloudflare
  or "verify you are human" markers in the first 4 KB.
- ``bot_detection_rate_limited`` — HTTP 429, or a ``Retry-After`` header
  present alongside a non-2xx status.

Each pauses Phase 0 for user-in-the-loop intervention rather than
retrying silently.

Deterministic: no model calls. Network side effect. Also writes a PNG
screenshot via the executor (passed back in ``result.meta`` as bytes,
not written directly — the executor owns the output directory).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from playwright.sync_api import (
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

from curriculum_harness.phases.phase0_acquisition.manifest import (
    ClickStep,
    ScopeSpec,
)
from curriculum_harness.phases.phase0_acquisition.primitives.base import (
    PrimitiveResult,
    check_required_scope,
)
from curriculum_harness.phases.phase0_acquisition.session_state import (
    PauseState,
)


USER_AGENT = (
    "Curriculum-Harness/0.1 "
    "(+https://github.com/GarethManning/curriculum-harness)"
)

VIEWPORT = {"width": 1280, "height": 720}

_BOT_CHALLENGE_MARKERS = (
    "verify you are human",
    "cloudflare",
    "checking your browser",
    "attention required",
)


def _bot_detection_signal(
    status: int | None,
    response_headers: dict[str, str],
    body_head: str,
) -> tuple[str, str] | None:
    """Return ``(signal_tag, explanation)`` if bot detection suspected.

    Returns None when no signal is detected.
    """

    lowered = (body_head or "")[:4000].lower()
    if status == 403:
        return (
            "bot_detection_http_403",
            "Initial navigation returned HTTP 403.",
        )
    if status == 429:
        return (
            "bot_detection_rate_limited",
            "Initial navigation returned HTTP 429.",
        )
    if (
        response_headers.get("retry-after")
        and status is not None
        and status >= 300
    ):
        return (
            "bot_detection_rate_limited",
            f"Response carried Retry-After at status {status}.",
        )
    for marker in _BOT_CHALLENGE_MARKERS:
        if marker in lowered:
            return (
                "bot_detection_challenge_page",
                (
                    "Response body contains a challenge marker: "
                    f"'{marker}'."
                ),
            )
    return None


def _pause_for_bot_detection(
    *,
    url: str,
    signal: tuple[str, str],
    status: int | None,
    source_reference: str,
) -> PauseState:
    tag, explanation = signal
    return PauseState(
        primitive="fetch_via_browser",
        reason=tag,
        needed=(
            "The target site appears to be blocking automated access.\n\n"
            f"Signal: `{tag}`\n"
            f"Detail: {explanation}\n"
            f"HTTP status: {status}\n"
            f"URL: {url}\n\n"
            "Options:\n"
            "- Wait and retry later (for rate-limiting).\n"
            "- Manually acquire the scoped content and place it in "
            "`provided.txt` to resume Phase 0.\n"
            "- Contact the site owner if the site should be accessible."
        ),
        expected_format="plain_text",
        resume_hint=(
            "Write `provided.txt` with the scoped content OR wait and "
            "re-invoke Phase 0."
        ),
        state_dir="_paused",
        source_reference=source_reference,
        extra={
            "signal_tag": tag,
            "explanation": explanation,
            "http_status": status,
            "url": url,
        },
    )


def _pause_for_click_failure(
    *,
    url: str,
    step_index: int,
    step: ClickStep,
    error: str,
    source_reference: str,
) -> PauseState:
    return PauseState(
        primitive="fetch_via_browser",
        reason="click_sequence_step_failed",
        needed=(
            f"Click-sequence step {step_index + 1} failed after retry.\n\n"
            f"Selector: `{step.selector}`\n"
            f"Wait-for: `{step.wait_for.type}`"
            + (
                f" (value=`{step.wait_for.value}`)"
                if step.wait_for.value
                else ""
            )
            + f"\nError: {error}\nURL at failure: {url}\n\n"
            "Either provide a corrected scope (different selector / "
            "different wait condition) or `provided.txt` with the "
            "scoped content you extracted manually."
        ),
        expected_format="plain_text",
        resume_hint=(
            "Edit the scope's click_sequence and re-invoke Phase 0, OR "
            "write `provided.txt` to proceed without the click sequence."
        ),
        state_dir="_paused",
        source_reference=source_reference,
        extra={
            "failing_step_index": step_index,
            "selector": step.selector,
            "wait_for_type": step.wait_for.type,
            "wait_for_value": step.wait_for.value,
            "error": error,
        },
    )


def _pause_for_wait_timeout(
    *,
    url: str,
    selector: str,
    error: str,
    source_reference: str,
) -> PauseState:
    return PauseState(
        primitive="fetch_via_browser",
        reason="wait_for_selector_timeout",
        needed=(
            f"The `wait_for_selector` ({selector!r}) never appeared "
            f"on {url} within the timeout.\n\n"
            f"Error: {error}\n\n"
            "Options:\n"
            "- Adjust the scope's `wait_for_selector` to an element that "
            "actually renders on this page.\n"
            "- Increase `browser_timeout_ms` if the page is slow.\n"
            "- Provide the scoped content manually via `provided.txt`."
        ),
        expected_format="plain_text",
        resume_hint=(
            "Edit scope.wait_for_selector and/or scope.browser_timeout_ms "
            "and re-invoke Phase 0."
        ),
        state_dir="_paused",
        source_reference=source_reference,
        extra={"wait_for_selector": selector, "error": error, "url": url},
    )


def _pause_for_navigation_error(
    *, url: str, error: str, source_reference: str
) -> PauseState:
    return PauseState(
        primitive="fetch_via_browser",
        reason="navigation_failed",
        needed=(
            f"Navigation to {url} failed: {error}\n\n"
            "Options:\n"
            "- Check the URL is reachable.\n"
            "- Check network / DNS.\n"
            "- Provide the scoped content manually via `provided.txt`."
        ),
        expected_format="plain_text",
        resume_hint="Fix the network issue or URL and re-invoke Phase 0.",
        state_dir="_paused",
        source_reference=source_reference,
        extra={"url": url, "error": error},
    )


class FetchViaBrowserPrimitive:
    name = "fetch_via_browser"
    required_scope_fields: tuple[str, ...] = (
        "url",
        "wait_for_selector",
    )
    optional_scope_fields: tuple[str, ...] = (
        "dismiss_modal_selector",
        "click_sequence",
        "browser_timeout_ms",
    )
    side_effects: frozenset[str] = frozenset({"network", "fs_write"})

    def __init__(self, headless: bool = True):
        self.headless = headless

    def validate_scope(self, scope: ScopeSpec) -> None:
        check_required_scope(self.name, scope, self.required_scope_fields)

    def run(
        self, scope: ScopeSpec, previous: PrimitiveResult | None
    ) -> PrimitiveResult:
        url = scope.url or scope.source_reference
        overall_timeout_ms = scope.browser_timeout_ms or 30000
        click_sequence = list(scope.click_sequence or [])
        click_events: list[dict[str, Any]] = []
        console_errors: list[str] = []
        modal_dismissed: bool | None = None

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport=VIEWPORT,
                user_agent=USER_AGENT,
            )
            page = context.new_page()
            page.on(
                "console",
                lambda msg: console_errors.append(f"{msg.type}: {msg.text}")
                if msg.type == "error"
                else None,
            )

            # Step 1 — navigation.
            http_status: int | None = None
            response_headers: dict[str, str] = {}
            try:
                response = page.goto(
                    url,
                    timeout=overall_timeout_ms,
                    wait_until="domcontentloaded",
                )
                http_status = response.status if response else None
                if response is not None:
                    response_headers = {
                        k.lower(): v for k, v in response.headers.items()
                    }
            except PlaywrightTimeoutError as exc:
                pause = _pause_for_navigation_error(
                    url=url,
                    error=f"timeout: {exc}",
                    source_reference=scope.source_reference,
                )
                browser.close()
                return PrimitiveResult(
                    output="",
                    summary={
                        "status": "failed",
                        "reason": pause.reason,
                        "url": url,
                    },
                    meta={"pause_request": pause},
                )
            except PlaywrightError as exc:
                pause = _pause_for_navigation_error(
                    url=url,
                    error=str(exc),
                    source_reference=scope.source_reference,
                )
                browser.close()
                return PrimitiveResult(
                    output="",
                    summary={
                        "status": "failed",
                        "reason": pause.reason,
                        "url": url,
                    },
                    meta={"pause_request": pause},
                )

            # Step 2 — bot-detection probe.
            body_head_for_detection = ""
            try:
                body_head_for_detection = page.content()
            except Exception:  # noqa: BLE001
                body_head_for_detection = ""
            bot_signal = _bot_detection_signal(
                http_status, response_headers, body_head_for_detection
            )
            if bot_signal is not None:
                pause = _pause_for_bot_detection(
                    url=url,
                    signal=bot_signal,
                    status=http_status,
                    source_reference=scope.source_reference,
                )
                browser.close()
                return PrimitiveResult(
                    output="",
                    summary={
                        "status": "failed",
                        "reason": pause.reason,
                        "http_status": http_status,
                        "url": url,
                    },
                    meta={"pause_request": pause},
                )

            # Step 3 — wait for the primary content selector.
            try:
                page.wait_for_selector(
                    scope.wait_for_selector,
                    timeout=overall_timeout_ms,
                    state="visible",
                )
            except PlaywrightTimeoutError as exc:
                pause = _pause_for_wait_timeout(
                    url=url,
                    selector=scope.wait_for_selector,
                    error=str(exc),
                    source_reference=scope.source_reference,
                )
                browser.close()
                return PrimitiveResult(
                    output="",
                    summary={
                        "status": "failed",
                        "reason": pause.reason,
                        "wait_for_selector": scope.wait_for_selector,
                    },
                    meta={"pause_request": pause},
                )

            # Step 4 — dismiss modal if one is specified and present.
            if scope.dismiss_modal_selector:
                try:
                    modal = page.query_selector(scope.dismiss_modal_selector)
                    if modal and modal.is_visible():
                        modal.click(timeout=5000)
                        # Give the modal animation a moment to clear.
                        page.wait_for_timeout(300)
                        modal_dismissed = True
                    else:
                        modal_dismissed = False
                except Exception as exc:  # noqa: BLE001
                    # Non-fatal: record the failure but continue.
                    modal_dismissed = False
                    console_errors.append(
                        f"modal_dismiss_error: {exc}"
                    )

            # Step 5 — click sequence, one step at a time with per-step
            # retry-on-fail and per-step timing.
            for idx, step in enumerate(click_sequence):
                step_timeout_ms = step.timeout_ms or overall_timeout_ms
                attempts = 0
                attempts_limit = 2 if step.retry_on_fail else 1
                step_error: str | None = None
                duration_ms = 0
                while attempts < attempts_limit:
                    attempts += 1
                    t0 = time.perf_counter()
                    try:
                        btn = page.query_selector(step.selector)
                        if btn is None:
                            raise PlaywrightError(
                                f"selector_not_found: {step.selector}"
                            )
                        btn.click(timeout=step_timeout_ms)
                        if step.wait_for.type == "selector_appears":
                            page.wait_for_selector(
                                step.wait_for.value,
                                timeout=step_timeout_ms,
                                state="visible",
                            )
                        else:  # network_idle
                            page.wait_for_load_state(
                                "networkidle", timeout=step_timeout_ms
                            )
                        step_error = None
                        duration_ms = int(
                            (time.perf_counter() - t0) * 1000
                        )
                        break
                    except (
                        PlaywrightTimeoutError,
                        PlaywrightError,
                    ) as exc:
                        step_error = f"{type(exc).__name__}: {exc}"
                        duration_ms = int(
                            (time.perf_counter() - t0) * 1000
                        )
                        if attempts < attempts_limit:
                            time.sleep(1.0)
                click_events.append(
                    {
                        "step_index": idx,
                        "selector": step.selector,
                        "wait_for_type": step.wait_for.type,
                        "wait_for_value": step.wait_for.value,
                        "attempts": attempts,
                        "duration_ms": duration_ms,
                        "error": step_error,
                    }
                )
                if step_error is not None:
                    pause = _pause_for_click_failure(
                        url=page.url,
                        step_index=idx,
                        step=step,
                        error=step_error,
                        source_reference=scope.source_reference,
                    )
                    browser.close()
                    return PrimitiveResult(
                        output="",
                        summary={
                            "status": "failed",
                            "reason": pause.reason,
                            "failing_step": idx,
                            "clicks_completed": idx,
                        },
                        meta={
                            "pause_request": pause,
                            "click_events": click_events,
                            "console_errors": console_errors[:20],
                        },
                    )

            # Step 6 — extract rendered HTML + screenshot.
            final_url = page.url
            rendered_html = page.content()
            try:
                screenshot_png = page.screenshot(full_page=True)
            except Exception as exc:  # noqa: BLE001
                console_errors.append(f"screenshot_error: {exc}")
                screenshot_png = b""

            browser.close()

        # Side artefact — the screenshot. The executor writes it to
        # the output directory; we don't own the path.
        side_artefacts: list[dict[str, Any]] = []
        if screenshot_png:
            side_artefacts.append(
                {
                    "filename": "rendered_state.png",
                    "bytes": screenshot_png,
                    "content_type": "image/png",
                    "list_in_content_files": True,
                }
            )

        return PrimitiveResult(
            output=rendered_html,
            summary={
                "status": "ok",
                "final_url": final_url,
                "http_status": http_status,
                "viewport": f"{VIEWPORT['width']}x{VIEWPORT['height']}",
                "rendered_html_bytes": len(rendered_html),
                "click_count": len(click_events),
                "modal_dismissed": modal_dismissed,
                "console_error_count": len(console_errors),
            },
            meta={
                "final_url": final_url,
                "http_status": http_status,
                "viewport": dict(VIEWPORT),
                "user_agent": USER_AGENT,
                "rendered_html_bytes": len(rendered_html),
                "rendered_html": rendered_html,
                "screenshot_png_bytes": len(screenshot_png),
                "click_events": click_events,
                "console_errors": console_errors[:20],
                "modal_dismissed": modal_dismissed,
                "side_artefacts": side_artefacts,
                "fetched_bytes": len(rendered_html),
            },
        )
