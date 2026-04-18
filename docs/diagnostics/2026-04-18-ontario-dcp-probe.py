"""Deeper Ontario DCP probe — understand the DOM structure when the
first generic probe found no aria-expanded toggles but content text is
present. Dumps sample DOM slices to disk for manual reading.
"""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


URL = (
    "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/"
    "grades/g7-history/strands"
)
OUT = Path(__file__).parent / "2026-04-18-ontario-dcp-investigation-artefacts"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
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
        page.goto(URL, wait_until="networkidle", timeout=60000)

        # Save full HTML of <main>.
        main_html = page.eval_on_selector(
            "main", "el => el.outerHTML"
        )
        (OUT / "main.html").write_text(main_html)

        # Dump all buttons and a sampling of their attributes.
        btns = page.eval_on_selector_all(
            "button",
            """els => els.map(e => ({
                text: (e.innerText || '').trim().slice(0, 120),
                id: e.id,
                cls: e.className,
                aria_expanded: e.getAttribute('aria-expanded'),
                aria_controls: e.getAttribute('aria-controls'),
                data_target: e.getAttribute('data-target'),
                data_bs_toggle: e.getAttribute('data-bs-toggle')
            }))""",
        )
        (OUT / "buttons.json").write_text(json.dumps(btns, indent=2))

        # Dump all anchor links — many accordion patterns are <a>.
        anchors = page.eval_on_selector_all(
            "a",
            """els => els.map(e => ({
                text: (e.innerText || '').trim().slice(0, 120),
                href: e.getAttribute('href'),
                cls: e.className,
                aria_expanded: e.getAttribute('aria-expanded'),
                aria_controls: e.getAttribute('aria-controls'),
                role: e.getAttribute('role')
            })).slice(0, 80)""",
        )
        (OUT / "anchors.json").write_text(json.dumps(anchors, indent=2))

        # Elements with any kind of "expand" / "toggle" / "accordion" class.
        toggles = page.eval_on_selector_all(
            "[class*='expand'], [class*='toggle'], [class*='accordion'], "
            "[class*='collapse'], [aria-expanded]",
            """els => els.map(e => ({
                tag: e.tagName,
                text: (e.innerText || '').trim().slice(0, 120),
                cls: e.className,
                aria_expanded: e.getAttribute('aria-expanded'),
                aria_controls: e.getAttribute('aria-controls'),
                role: e.getAttribute('role')
            })).slice(0, 40)""",
        )
        (OUT / "toggles.json").write_text(json.dumps(toggles, indent=2))

        # Sample first 2000 chars of main.innerText.
        inner = page.eval_on_selector("main", "el => el.innerText")
        (OUT / "main-innertext.txt").write_text(inner)

        # Look for SPA / framework root markers.
        frame_markers = page.evaluate(
            """() => ({
                root_id_next: !!document.querySelector('#__next'),
                root_id_root: !!document.querySelector('#root'),
                has_nuxt: !!window.__NUXT__,
                has_initial_state: !!window.__INITIAL_STATE__,
                doctitle: document.title,
                scripts_len: document.scripts.length
            })"""
        )
        (OUT / "frame-markers.json").write_text(
            json.dumps(frame_markers, indent=2)
        )
        browser.close()
        print("wrote", OUT)


if __name__ == "__main__":
    main()
