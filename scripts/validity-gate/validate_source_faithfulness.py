#!/usr/bin/env python3
"""Foundation moment 1 — LT no-invention / source faithfulness
(VALIDITY.md assertion b).

**Assertion.** Every learning target traces back to at least one
element of the source-proxy corpus above the matcher's confidence
threshold. LTs with no source match are flagged as potentially
invented.

**Reads.** Same artefacts as `validate_source_coverage.py`.

**Writes.** JSON report: `{total_lts, potentially_invented: [...],
invented_count, faithfulness_pct}`.

**Exit codes.** 0 = no potentially-invented LTs. 1 = one or more
flagged. 2 = could not run.

### Known test case

The felvételi run (`outputs/palya-felveteli-2026-04-17/`) contains an
LT at index 0 that introduces "factorial" / "factorials", which is
not in the source proxy (see `docs/diagnostics/2026-04-17-session-1-
diagnosis.md` Q5.1 and REVIEW.md §2). This gate must flag that LT.
If it doesn't, the gate or the matcher is miscalibrated.

### Adjacent mechanisms this gate does NOT check

1. **Semantic vs lexical invention.** An LT can match source
   vocabulary while introducing a new construct. A cleverer
   invention that reuses source vocabulary can evade this gate.
2. **Domain drift.** An LT in the wrong subject still runs through
   the matcher as if it belonged; the result is usually "low score →
   flagged as invented", but the failure reason reported is wrong.
3. **Corroboration count.** A single weak source match is enough to
   clear the gate. No requirement that the LT trace to multiple
   converging source items.
4. **Proxy-ceiling.** The corpus is the pipeline's English rendering
   of the source. An LT that faithfully derives from a bullet present
   in the raw source but absent from the proxy will be flagged as
   invented when it isn't. Baseline noise floor comes from this.
5. **Threshold shared with coverage gate** via
   `source_evidence_matcher.DEFAULT_THRESHOLD` (0.35 since Session 3a).
   If the two gates ever need different thresholds, split them here.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _run_loader import load_run  # noqa: E402

from eval.source_evidence_matcher import DEFAULT_THRESHOLD, best_match  # noqa: E402

MATCH_THRESHOLD = DEFAULT_THRESHOLD


def run(run_dir: str) -> dict:
    arte = load_run(run_dir)
    source_texts = [it.text for it in arte.source_corpus]
    invented: list[dict] = []
    per_lt: list[dict] = []
    for i, lt in enumerate(arte.learning_targets):
        stmt = lt.get("statement", "")
        top = best_match(stmt, source_texts)
        top_score = top.score if top else 0.0
        top_prov = (
            arte.source_corpus[top.matched_index].provenance
            if top
            else None
        )
        record = {
            "lt_index": i,
            "statement": stmt,
            "best_source_provenance": top_prov,
            "best_source_text": top.matched_item if top else None,
            "best_score": top_score,
        }
        per_lt.append(record)
        if top_score < MATCH_THRESHOLD:
            invented.append(record)
    total = len(arte.learning_targets)
    faithful = total - len(invented)
    faithfulness_pct = round((faithful / total) * 100, 1) if total else 0.0
    return {
        "gate": "validate_source_faithfulness",
        "run_dir": str(arte.run_dir),
        "threshold": MATCH_THRESHOLD,
        "corpus_mode": arte.corpus_mode,
        "corpus_warning": arte.corpus_warning,
        "total_lts": total,
        "faithful": faithful,
        "invented_count": len(invented),
        "faithfulness_pct": faithfulness_pct,
        "potentially_invented": invented,
        "per_lt": per_lt,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--out", help="write JSON report here (default: stdout)")
    args = ap.parse_args()

    try:
        report = run(args.run_dir)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    out = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(out)
    else:
        print(out)

    if report.get("corpus_warning"):
        print(f"[WARN] {report['corpus_warning']}", file=sys.stderr)

    if report["invented_count"] == 0:
        print(
            f"[PASS] validate_source_faithfulness: {report['faithfulness_pct']}%"
            f" ({report['faithful']}/{report['total_lts']})",
            file=sys.stderr,
        )
        return 0
    print(
        f"[FAIL] validate_source_faithfulness: {report['invented_count']}"
        f" potentially invented LTs"
        f" (faithfulness {report['faithfulness_pct']}%)",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
