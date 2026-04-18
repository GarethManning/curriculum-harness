#!/usr/bin/env python3
"""Foundation moment 1 — source → LT coverage (VALIDITY.md assertion a).

**Assertion.** Every source content element in the run's source-proxy
corpus (strand labels + values_basis + Phase 1 rationale + element
lists) traces to at least one learning target above the matcher's
confidence threshold.

**Reads.** `outputs/<run>/<runId>_curriculum_profile_v1.json`,
`..._architecture_v1.json`, `..._learning_targets_v1.json`. Handles
both runId-prefixed and legacy plain filenames.

**Writes.** One JSON report to stdout (or `--out <path>`):
`{coverage_pct, total_source_items, orphan_count, orphans: [...]}`.

**Exit codes.** 0 = all source items covered. 1 = one or more orphans.
2 = could not run (missing artefact).

### Adjacent mechanisms this gate does NOT check

1. **True source fidelity.** The corpus is the pipeline's *own*
   English rendering of the source (see `_run_loader.py`). If Phase 1
   dropped a strand silently, this gate won't notice — it will only
   report coverage against what the pipeline claims the source said.
2. **Grain.** A single coarse LT can "cover" multiple source items
   via shared vocabulary. High coverage is not the same as faithful
   decomposition. See `validate_source_faithfulness.py` for the
   inverse check.
3. **Language.** Matcher is English-only. For non-English sources
   the proxy is built from Phase 1/2 English output; raw source text
   is not used. The felvételi run (Hungarian source) runs in this
   proxy mode.
4. **Threshold tuning.** The threshold is
   `source_evidence_matcher.DEFAULT_THRESHOLD` (0.35 since Session 3a).
   Baseline measurements are captured under this threshold; moving it
   invalidates prior baselines.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make sibling modules importable when run as a script.
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
    lt_statements = [lt.get("statement", "") for lt in arte.learning_targets]
    orphans: list[dict] = []
    per_item: list[dict] = []
    for item in arte.source_corpus:
        top = best_match(item.text, lt_statements)
        top_score = top.score if top else 0.0
        top_text = top.matched_item if top else None
        record = {
            "provenance": item.provenance,
            "text": item.text,
            "best_lt": top_text,
            "best_score": top_score,
        }
        per_item.append(record)
        if top_score < MATCH_THRESHOLD:
            orphans.append(record)
    total = len(arte.source_corpus)
    covered = total - len(orphans)
    coverage_pct = round((covered / total) * 100, 1) if total else 0.0
    return {
        "gate": "validate_source_coverage",
        "run_dir": str(arte.run_dir),
        "threshold": MATCH_THRESHOLD,
        "corpus_mode": arte.corpus_mode,
        "corpus_warning": arte.corpus_warning,
        "total_source_items": total,
        "covered": covered,
        "orphan_count": len(orphans),
        "coverage_pct": coverage_pct,
        "orphans": orphans,
        "per_item": per_item,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", help="path to outputs/<run>/ directory")
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

    if report["orphan_count"] == 0:
        print(
            f"[PASS] validate_source_coverage: {report['coverage_pct']}%"
            f" ({report['covered']}/{report['total_source_items']})",
            file=sys.stderr,
        )
        return 0
    print(
        f"[FAIL] validate_source_coverage: {report['orphan_count']} orphaned"
        f" source items (coverage {report['coverage_pct']}%)",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
