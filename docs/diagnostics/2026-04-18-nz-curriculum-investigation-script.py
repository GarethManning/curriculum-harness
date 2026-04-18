"""New Zealand Curriculum Online interaction-pattern investigation
(Session 4a-3 Step 2). Mirrors the Ontario DCP investigation — same
seven-step probe, same artefacts, so the two can be compared.

Target page: Social Sciences Years 4–6 (roughly age-equivalent to
Ontario's Grade 7 History). URL found via search on 2026-04-18.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


URL = (
    "https://newzealandcurriculum.tahurangi.education.govt.nz/"
    "new-zealand-curriculum-online/nzc---social-sciences-years-4---6/"
    "5637290852.p"
)
OUT = Path(__file__).parent / "2026-04-18-nz-curriculum-investigation-artefacts"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> dict:
    findings: dict = {
        "url": URL,
        "viewport": {"width": 1280, "height": 720},
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

        try:
            response = page.goto(URL, wait_until="networkidle", timeout=60000)
            findings["initial_http_status"] = (
                response.status if response else None
            )
        except Exception as exc:  # noqa: BLE001
            findings["initial_http_status"] = f"navigation_error: {exc}"

        body_text = page.content()
        lowered = body_text[:4000].lower()
        if "verify you are human" in lowered or "cloudflare" in lowered:
            findings["bot_detection"] = "challenge_detected"
        elif findings["initial_http_status"] == 403:
            findings["bot_detection"] = "http_403"
        else:
            findings["bot_detection"] = "none_detected"

        page.screenshot(
            path=str(OUT / "01-initial-render.png"), full_page=True
        )

        # Consent modal probe.
        consent_candidates = [
            "#onetrust-accept-btn-handler",
            "button[aria-label*='cookie' i]",
            "button:has-text('Accept')",
            "button:has-text('I accept')",
            "button:has-text('Agree')",
            ".cookie-banner button",
        ]
        consent = {"visible": False}
        for sel in consent_candidates:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    consent = {"selector": sel, "visible": True}
                    break
            except Exception:  # noqa: BLE001
                continue
        findings["consent_modal"] = consent

        # Frame markers.
        findings["frame_markers"] = page.evaluate(
            """() => ({
                root_id_next: !!document.querySelector('#__next'),
                root_id_root: !!document.querySelector('#root'),
                has_nuxt: !!window.__NUXT__,
                has_initial_state: !!window.__INITIAL_STATE__,
                doctitle: document.title,
                scripts_len: document.scripts.length,
                has_angular: !!window.getAllAngularRootElements
            })"""
        )

        # SPA routing before/after — capture URL on an internal link click.
        findings["spa_routing"] = {"url_before": page.url}

        # Dump main.innerText and outerHTML.
        try:
            main_inner = page.eval_on_selector("main", "el => el.innerText")
            (OUT / "main-innertext.txt").write_text(main_inner)
            findings["main_inner_chars"] = len(main_inner)
        except Exception as exc:  # noqa: BLE001
            findings["main_inner_chars"] = f"error: {exc}"
            main_inner = ""

        # Headings.
        headings = page.eval_on_selector_all(
            "h1, h2, h3",
            """els => els.slice(0, 40).map(e => ({
                tag: e.tagName,
                text: (e.innerText || '').trim().slice(0, 140)
            }))""",
        )
        findings["headings"] = headings

        # Toggle / accordion / collapse / aria-expanded probe.
        toggles = page.eval_on_selector_all(
            "[aria-expanded], [class*='accordion' i], [class*='collapse' i], "
            "details > summary, button[aria-controls]",
            """els => els.slice(0, 40).map(e => ({
                tag: e.tagName,
                cls: e.className ? e.className.toString().slice(0, 200) : '',
                text: (e.innerText || '').trim().slice(0, 140),
                aria_expanded: e.getAttribute('aria-expanded'),
                aria_controls: e.getAttribute('aria-controls')
            }))""",
        )
        findings["toggles"] = toggles

        # If toggles exist, click the first visible expand-eligible one
        # and measure timing + revealed content.
        clicked: dict | None = None
        try:
            handles = page.query_selector_all(
                "[aria-expanded='false'], "
                "details:not([open]) > summary, "
                "button[aria-controls]"
            )
            for h in handles:
                try:
                    if not h.is_visible():
                        continue
                    label = (h.inner_text() or "").strip()[:140]
                    pre = h.get_attribute("aria-expanded")
                    controls = h.get_attribute("aria-controls")
                    net_events: list[dict] = []

                    def _on_response(resp, sink=net_events):
                        sink.append(
                            {
                                "url": resp.url,
                                "status": resp.status,
                                "content_type": resp.headers.get(
                                    "content-type", ""
                                ),
                            }
                        )

                    page.on("response", _on_response)
                    t0 = time.time()
                    h.click()
                    try:
                        page.wait_for_load_state(
                            "networkidle", timeout=5000
                        )
                    except Exception:  # noqa: BLE001
                        pass
                    revealed_chars = None
                    if controls:
                        target = page.query_selector(f"#{controls}")
                        if target:
                            revealed_chars = len(target.inner_text() or "")
                    dt = int((time.time() - t0) * 1000)
                    clicked = {
                        "label": label,
                        "aria_expanded_before": pre,
                        "aria_expanded_after": h.get_attribute("aria-expanded"),
                        "aria_controls": controls,
                        "revealed_chars": revealed_chars,
                        "duration_ms": dt,
                        "net_events_same_host": [
                            e
                            for e in net_events
                            if urlparse(e["url"]).netloc
                            == urlparse(URL).netloc
                        ][:8],
                    }
                    break
                except Exception as exc:  # noqa: BLE001
                    clicked = {"click_error": str(exc)}
                    break
        except Exception as exc:  # noqa: BLE001
            clicked = {"probe_error": str(exc)}
        findings["click_test"] = clicked

        findings["spa_routing"]["url_after_click"] = page.url
        page.screenshot(path=str(OUT / "02-after-click.png"), full_page=True)

        # Content container probes.
        container_candidates = [
            "main",
            "article",
            "[role=main]",
            ".content",
            "#content",
            ".curriculum-content",
            "body",
        ]
        cprobe: dict = {}
        for sel in container_candidates:
            try:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text() or ""
                    cprobe[sel] = {
                        "found": True,
                        "inner_text_chars": len(text),
                    }
                else:
                    cprobe[sel] = {"found": False}
            except Exception as exc:  # noqa: BLE001
                cprobe[sel] = {"error": str(exc)}
        findings["content_container_probes"] = cprobe

        findings["console_errors"] = console_errors[:20]

        # Also try related URL to check URL-pattern stability.
        sibling_url = (
            "https://newzealandcurriculum.tahurangi.education.govt.nz/"
            "social-sciences-1-10/5637208398.p"
        )
        try:
            resp = page.goto(
                sibling_url, wait_until="domcontentloaded", timeout=30000
            )
            findings["sibling_url"] = {
                "url": sibling_url,
                "status": resp.status if resp else None,
            }
        except Exception as exc:  # noqa: BLE001
            findings["sibling_url"] = {"url": sibling_url, "error": str(exc)}

        browser.close()

    (OUT / "_findings.json").write_text(
        json.dumps(findings, indent=2, ensure_ascii=False)
    )
    return findings


if __name__ == "__main__":
    main()
