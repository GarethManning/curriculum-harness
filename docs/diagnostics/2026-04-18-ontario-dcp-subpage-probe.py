"""Probe an Ontario DCP per-expectation sub-page (e.g. /a/a1) to
document what lives there, so the investigation memo can say whether
overall-expectations-only vs. full-strand is a scope or primitive
question.
"""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


URLS = [
    "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/grades/g7-history/a/a1",
    "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/grades/g7-history/a/a3",
    "https://www.dcp.edu.gov.on.ca/en/curriculum/elementary-sshg/grades/g7-history/b/b3",
]

OUT = Path(__file__).parent / "2026-04-18-ontario-dcp-investigation-artefacts"


def main() -> None:
    samples: list[dict] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Curriculum-Harness/0.1",
        )
        page = context.new_page()
        for url in URLS:
            resp = page.goto(url, wait_until="networkidle", timeout=45000)
            inner = page.eval_on_selector("main", "el => el.innerText")
            samples.append(
                {
                    "url": url,
                    "status": resp.status if resp else None,
                    "main_inner_text_chars": len(inner),
                    "first_600_chars": inner[:600],
                }
            )
        browser.close()
    (OUT / "subpages.json").write_text(
        json.dumps(samples, indent=2, ensure_ascii=False)
    )


if __name__ == "__main__":
    main()
