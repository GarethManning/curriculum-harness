"""Ontario DCP interaction-pattern investigation (Session 4a-3 Step 1).

Launches headless Chromium against the Grade 7 History strands page and
records the information the `fetch_via_browser` primitive's scope schema
will need to know: consent modals, SPA routing, accordion selectors,
per-click timing, network-driven reveals, bot-detection signals,
URL-pattern generalisation to other grade/subject pages.

Output: writes `_findings.json` and screenshots to the same directory
as this script. The findings are then summarised by hand in the
companion memo `2026-04-18-ontario-dcp-investigation.md`.

Deterministic. No model calls.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


URL = (
    "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/"
    "grades/g7-history/strands"
)

OUT_DIR = Path(__file__).parent / "2026-04-18-ontario-dcp-investigation-artefacts"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> dict:
    findings: dict = {
        "url": URL,
        "viewport": {"width": 1280, "height": 720},
        "consent_modal": None,
        "spa_routing": None,
        "initial_http_status": None,
        "selectors": {},
        "click_timing": [],
        "network_activity_on_click": [],
        "bot_detection": None,
        "console_errors": [],
        "url_patterns": [],
        "headings_found": [],
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Curriculum-Harness/0.1 (+https://github.com/"
                "GarethManning/curriculum-harness)"
            ),
        )
        page = context.new_page()

        console_errors: list[str] = []
        page.on(
            "console",
            lambda msg: console_errors.append(f"{msg.type}: {msg.text}")
            if msg.type == "error"
            else None,
        )

        # Step A — navigate + initial screenshot + HTTP status.
        try:
            response = page.goto(URL, wait_until="networkidle", timeout=45000)
            findings["initial_http_status"] = (
                response.status if response else None
            )
        except Exception as exc:  # noqa: BLE001
            findings["initial_http_status"] = f"navigation_error: {exc}"

        # Bot-detection probe: 403, challenge strings.
        body_text = page.content()
        lowered = body_text[:4000].lower()
        if "verify you are human" in lowered or "cloudflare" in lowered:
            findings["bot_detection"] = "challenge_detected"
        elif findings["initial_http_status"] == 403:
            findings["bot_detection"] = "http_403"
        else:
            findings["bot_detection"] = "none_detected"

        page.screenshot(path=str(OUT_DIR / "01-initial-render.png"))

        # Step B — consent modal check.
        consent_candidates = [
            "#onetrust-accept-btn-handler",
            "button[aria-label*='cookie' i]",
            "button:has-text('Accept')",
            "button:has-text('I accept')",
            "button:has-text('Agree')",
            ".cookie-banner button",
        ]
        for sel in consent_candidates:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    findings["consent_modal"] = {
                        "selector": sel,
                        "visible": True,
                    }
                    break
            except Exception:  # noqa: BLE001
                continue
        if findings["consent_modal"] is None:
            findings["consent_modal"] = {"visible": False}

        # Step C — SPA routing test: capture URL pre-/post-interaction.
        findings["spa_routing"] = {"url_before": page.url}

        # Step D — identify selectors for Grade 7 History content.
        heading_handles = page.query_selector_all("h1, h2, h3")
        headings = []
        for h in heading_handles[:30]:
            try:
                text = (h.inner_text() or "").strip()
                if text:
                    headings.append(text)
            except Exception:  # noqa: BLE001
                continue
        findings["headings_found"] = headings

        # Try to locate accordion-like toggles by common role/aria patterns.
        candidate_groups = [
            ("aria-expanded buttons", "button[aria-expanded]"),
            ("details/summary", "details > summary"),
            ("aria-controls buttons", "button[aria-controls]"),
            ("heading-level buttons", "h2 button, h3 button, h4 button"),
        ]
        selector_probe: dict = {}
        for label, sel in candidate_groups:
            try:
                els = page.query_selector_all(sel)
                selector_probe[label] = {
                    "selector": sel,
                    "count": len(els),
                    "sample_text": (
                        [
                            ((e.inner_text() or "").strip()[:80])
                            for e in els[:6]
                        ]
                        if els
                        else []
                    ),
                }
            except Exception as exc:  # noqa: BLE001
                selector_probe[label] = {"error": str(exc)}
        findings["selectors"]["toggle_probes"] = selector_probe

        # Main content container probe.
        container_candidates = [
            "main",
            "article",
            "[role=main]",
            ".curriculum-content",
            ".strand",
            ".strands",
            "#content",
        ]
        container_probe = {}
        for sel in container_candidates:
            try:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text() or ""
                    container_probe[sel] = {
                        "found": True,
                        "inner_text_chars": len(text),
                    }
                else:
                    container_probe[sel] = {"found": False}
            except Exception as exc:  # noqa: BLE001
                container_probe[sel] = {"error": str(exc)}
        findings["selectors"]["content_container_probes"] = container_probe

        # Step E — click one toggle and measure timing.
        # Pick the first visible aria-expanded button, if any.
        clicked = False
        try:
            btns = page.query_selector_all("button[aria-expanded]")
            for b in btns:
                if not b.is_visible():
                    continue
                pre = b.get_attribute("aria-expanded")
                label = (b.inner_text() or "").strip()[:120]
                network_events: list[dict] = []

                def _on_request(req, sink=network_events):
                    sink.append({"phase": "request", "url": req.url})

                def _on_response(resp, sink=network_events):
                    sink.append(
                        {
                            "phase": "response",
                            "url": resp.url,
                            "status": resp.status,
                            "content_type": (
                                resp.headers.get("content-type", "")
                            ),
                        }
                    )

                page.on("request", _on_request)
                page.on("response", _on_response)

                t0 = time.time()
                b.click()
                # Wait for any in-flight activity to settle (briefly).
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:  # noqa: BLE001
                    pass
                post = b.get_attribute("aria-expanded")
                controls = b.get_attribute("aria-controls")
                revealed_text_chars = None
                if controls:
                    target = page.query_selector(f"#{controls}")
                    if target:
                        revealed_text_chars = len(target.inner_text() or "")
                dt = int((time.time() - t0) * 1000)

                findings["click_timing"].append(
                    {
                        "label": label,
                        "aria_expanded_before": pre,
                        "aria_expanded_after": post,
                        "aria_controls": controls,
                        "revealed_chars": revealed_text_chars,
                        "duration_ms": dt,
                    }
                )
                findings["network_activity_on_click"] = [
                    e
                    for e in network_events
                    if urlparse(e.get("url", "")).netloc
                    == urlparse(URL).netloc
                ][:10]
                clicked = True
                break
        except Exception as exc:  # noqa: BLE001
            findings["click_timing"].append({"error": str(exc)})

        if not clicked:
            findings["click_timing"].append(
                {"note": "no_visible_aria_expanded_buttons_found"}
            )

        findings["spa_routing"]["url_after_click"] = page.url

        page.screenshot(path=str(OUT_DIR / "02-after-click.png"))

        # Step F — URL-pattern generalisation: sample another grade/subject.
        other_urls = [
            "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/grades/g7-geography/strands",
            "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/grades/g5-history/strands",
        ]
        for ou in other_urls:
            try:
                resp = page.goto(ou, wait_until="domcontentloaded", timeout=30000)
                findings["url_patterns"].append(
                    {
                        "url": ou,
                        "status": resp.status if resp else None,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                findings["url_patterns"].append(
                    {"url": ou, "error": str(exc)}
                )

        findings["console_errors"] = console_errors[:20]
        browser.close()

    out_file = OUT_DIR / "_findings.json"
    out_file.write_text(json.dumps(findings, indent=2, ensure_ascii=False))
    print(f"wrote {out_file}")
    return findings


if __name__ == "__main__":
    main()
