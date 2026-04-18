"""Verify the source-evidence matcher against known-good and known-bad
fixtures before it is trusted on real pipeline output.

Rule: the matcher must distinguish good from bad on these fixtures. If
any assertion in this file fails, the matcher is miscalibrated and
must be fixed before any gate script is run on real data.

Usage:
    python -m eval.test_matcher

Exit codes:
    0 — all assertions passed; matcher is trusted
    1 — one or more assertions failed; do not run gates yet
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from eval.source_evidence_matcher import DEFAULT_THRESHOLD, best_match, match

# Fixture-verification threshold mirrors the matcher's shared default
# (source_evidence_matcher.DEFAULT_THRESHOLD). Known-good pairs must
# land above and deliberately-invented / orphaned pairs must land
# below. If future fixtures require a different value, change the
# source of truth in source_evidence_matcher.py, re-run all gates,
# and append a dated entry to docs/project-log/.
MATCH_THRESHOLD: float = DEFAULT_THRESHOLD

FIXTURE_DIR = Path(__file__).parent / "test_cases"


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _report(name: str, ok: bool, detail: str) -> None:
    flag = "PASS" if ok else "FAIL"
    print(f"[{flag}] {name}")
    if detail:
        for line in detail.splitlines():
            print(f"       {line}")


def test_known_good() -> list[bool]:
    """Every source bullet traces to ≥1 LT above threshold. Every LT
    traces back to ≥1 source bullet above threshold."""
    source = _load(FIXTURE_DIR / "known_good" / "source.json")
    lt_set = _load(FIXTURE_DIR / "known_good" / "lt_set.json")
    bullets: list[str] = source["bullets"]
    lts: list[str] = lt_set["lts"]
    results: list[bool] = []

    # Every bullet covered by ≥1 LT.
    for i, bullet in enumerate(bullets):
        top = best_match(bullet, lts)
        ok = top is not None and top.score >= MATCH_THRESHOLD
        results.append(ok)
        _report(
            f"known-good coverage: bullet {i} has an LT match ≥ {MATCH_THRESHOLD}",
            ok,
            f"bullet = {bullet!r}\n"
            f"best LT = {top.matched_item if top else None!r} (score={top.score if top else 0.0})",
        )

    # Every LT supported by ≥1 bullet.
    for i, lt in enumerate(lts):
        top = best_match(lt, bullets)
        ok = top is not None and top.score >= MATCH_THRESHOLD
        results.append(ok)
        _report(
            f"known-good faithfulness: LT {i} has a source match ≥ {MATCH_THRESHOLD}",
            ok,
            f"LT = {lt!r}\n"
            f"best bullet = {top.matched_item if top else None!r} (score={top.score if top else 0.0})",
        )

    return results


def test_known_bad() -> list[bool]:
    """Orphan bullet (index 4) must have NO LT above threshold. Invented
    LT (index 4) must have NO source match above threshold. The four
    normal bullets/LTs (indices 0–3) must still match above threshold
    (so the matcher isn't just pessimistic)."""
    source = _load(FIXTURE_DIR / "known_bad" / "source.json")
    lt_set = _load(FIXTURE_DIR / "known_bad" / "lt_set.json")
    bullets: list[str] = source["bullets"]
    lts: list[str] = lt_set["lts"]
    expected_orphans = set(source["expected_flags"]["orphan_bullets"])
    expected_invented = set(lt_set["expected_flags"]["invented_lts"])
    results: list[bool] = []

    # Bullets: indices in expected_orphans must score below threshold.
    # All others must score at or above threshold.
    for i, bullet in enumerate(bullets):
        top = best_match(bullet, lts)
        top_score = top.score if top else 0.0
        if i in expected_orphans:
            ok = top_score < MATCH_THRESHOLD
            results.append(ok)
            _report(
                f"known-bad: orphan bullet {i} correctly has no LT match ≥ {MATCH_THRESHOLD}",
                ok,
                f"bullet = {bullet!r}\n"
                f"best LT = {top.matched_item if top else None!r} (score={top_score})",
            )
        else:
            ok = top_score >= MATCH_THRESHOLD
            results.append(ok)
            _report(
                f"known-bad: normal bullet {i} still has an LT match ≥ {MATCH_THRESHOLD}",
                ok,
                f"bullet = {bullet!r}\n"
                f"best LT = {top.matched_item if top else None!r} (score={top_score})",
            )

    # LTs: indices in expected_invented must score below threshold.
    # All others must score at or above threshold.
    for i, lt in enumerate(lts):
        top = best_match(lt, bullets)
        top_score = top.score if top else 0.0
        if i in expected_invented:
            ok = top_score < MATCH_THRESHOLD
            results.append(ok)
            _report(
                f"known-bad: invented LT {i} correctly has no source match ≥ {MATCH_THRESHOLD}",
                ok,
                f"LT = {lt!r}\n"
                f"best bullet = {top.matched_item if top else None!r} (score={top_score})",
            )
        else:
            ok = top_score >= MATCH_THRESHOLD
            results.append(ok)
            _report(
                f"known-bad: normal LT {i} still has a source match ≥ {MATCH_THRESHOLD}",
                ok,
                f"LT = {lt!r}\n"
                f"best bullet = {top.matched_item if top else None!r} (score={top_score})",
            )

    return results


def main() -> int:
    print("== source-evidence matcher — fixture verification ==\n")
    print("known-good set:")
    good = test_known_good()
    print("\nknown-bad set:")
    bad = test_known_bad()

    all_results = good + bad
    passed = sum(1 for r in all_results if r)
    total = len(all_results)
    print(f"\n== {passed}/{total} assertions passed ==")
    if passed == total:
        print("Matcher is trusted to run on real pipeline output.")
        return 0
    print("Matcher FAILED verification. Do not run gates on real data.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
