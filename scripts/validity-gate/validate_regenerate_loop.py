#!/usr/bin/env python3
"""Foundation moment 2 — regenerate loop ran on initial failure
(VALIDITY.md assertion e).

**Assertion.** If any learning target initially failed FAIL_SET
validation during Phase 4, the regenerate loop ran. Either (a) the
retry succeeded and the final LT has no FAIL_SET flags, or (b) the
retry budget was exhausted and the source bullet is in
``human_review_required``, or (c) the LT is a known language-bypass
(non-English source, SOURCE_FAITHFULNESS_FAIL-only) and ships flagged
with an explicit ``SOURCE_LANGUAGE_BYPASS`` annotation.

Status: implemented (Session 3c, 2026-04-18). Reads the
``<runId>_regeneration_events_v1.json`` artefact that Phase 4 emits.

**Reads.** ``<runId>_learning_targets_v1.json`` plus
``<runId>_regeneration_events_v1.json`` (both Session 3c artefacts).

**Writes.** JSON report with per-LT regeneration history plus the gap
list (any LT that ships with FAIL_SET flags but has no corresponding
regeneration event or human-review entry).

**Exit codes.** 0 = every FAIL_SET-flagged LT has a matching
regeneration record (success, human-review, or language-bypass); 1 =
gap detected; 2 = could not run (missing artefacts).

### Adjacent mechanisms this gate does NOT check

1. **Retry quality.** If every retry burned the budget on
   near-identical text (REGENERATION_NEAR_IDENTICAL annotation on
   every attempt), the gate still records the event; it does not
   judge whether the retry prompt was effective.
2. **Whether language-bypass is appropriate.** The gate trusts
   Phase 1's language detection. If `source_language="en"` was
   mis-detected for a non-English source, the gate will hold Phase 4
   to English-matcher retries and flag the LT as un-regenerated.
3. **FAIL_SET membership.** The gate uses Phase 4's FAIL_SET
   verbatim. If that set is ever tuned to silence a noisy flag, this
   gate follows suit — it does not second-guess set membership.
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

from _run_loader import _find_json, _load_json  # noqa: E402

# Keep this in lockstep with Phase 4's FAIL_SET. Duplicating the set
# here is intentional: the gate must be runnable without importing the
# harness (which pulls in httpx, langgraph, etc.).
FAIL_SET: frozenset[str] = frozenset({
    "SOURCE_FAITHFULNESS_FAIL",
    "EXCEEDS_WORD_LIMIT",
    "COMPOUND_TYPE",
    "EMBEDDED_EXAMPLE",
    "DISPOSITION_RUBRIC_ERROR",
    "MISSING_I_CAN_FORMAT",
    "MISSING_LT_STATEMENT",
})

SOURCE_LANGUAGE_BYPASS_ANNOTATION = "SOURCE_LANGUAGE_BYPASS"


def run(run_dir: str) -> dict:
    run_p = Path(run_dir)
    if not run_p.is_dir():
        raise FileNotFoundError(f"run directory does not exist: {run_p}")

    lts_path = _find_json(run_p, "learning_targets_v1.json")
    if lts_path is None:
        raise FileNotFoundError(
            f"no learning_targets_v1.json in {run_p} — gate cannot run"
        )
    lts_doc = _load_json(lts_path) or {}
    lts = lts_doc.get("learning_targets") or []

    regen_path = _find_json(run_p, "regeneration_events_v1.json")
    if regen_path is None:
        raise FileNotFoundError(
            f"no regeneration_events_v1.json in {run_p} — gate cannot run "
            "(Session 3c artefact; regenerate the run under the Session "
            "3c harness to produce it)"
        )
    regen_doc = _load_json(regen_path) or {}
    events = regen_doc.get("regeneration_events") or []
    human_review = regen_doc.get("human_review_required") or []

    # Build an index of final statements covered by the event log.
    event_by_final_statement: dict[str, dict] = {}
    event_by_source_label: dict[str, dict] = {}
    for ev in events:
        attempts = ev.get("attempts") or []
        if not attempts:
            continue
        final = str(attempts[-1].get("statement") or "").strip()
        if final:
            event_by_final_statement[final] = ev
        sl = str(ev.get("source_label") or "").strip()
        if sl:
            event_by_source_label[sl] = ev

    human_review_source_ids: set[str] = set()
    for hr in human_review:
        for sbid in hr.get("source_bullet_ids") or []:
            if sbid:
                human_review_source_ids.add(str(sbid))

    # For each LT that ships with FAIL_SET flags, verify it has a
    # coverage story (success, human-review, or language-bypass).
    gaps: list[dict] = []
    covered_success: list[dict] = []
    covered_bypass: list[dict] = []
    covered_exhausted: list[dict] = []
    clean_lts = 0

    for i, lt in enumerate(lts):
        flags = list(lt.get("flags") or [])
        fail_flags = [f for f in flags if f in FAIL_SET]
        if not fail_flags:
            # Still examine whether regeneration ran silently and
            # succeeded — not a gap, but recorded for the report.
            clean_lts += 1
            continue

        stmt = str(lt.get("statement") or "").strip()
        source_label = str(lt.get("kud_source") or "").strip()
        ev = event_by_final_statement.get(stmt) or event_by_source_label.get(
            source_label
        )

        record = {
            "lt_index": i,
            "statement": stmt,
            "final_fail_flags": fail_flags,
            "matched_event_outcome": (
                ev.get("outcome") if ev else None
            ),
            "matched_event_annotations": (
                list(ev.get("annotations") or []) if ev else []
            ),
        }
        if ev is None:
            record["gap_reason"] = (
                "LT ships with FAIL_SET flags but no regeneration event "
                "was recorded for it"
            )
            gaps.append(record)
            continue
        annotations = set(ev.get("annotations") or [])
        if SOURCE_LANGUAGE_BYPASS_ANNOTATION in annotations:
            covered_bypass.append(record)
            continue
        outcome = str(ev.get("outcome") or "")
        if outcome.startswith("success"):
            covered_success.append(record)
            continue
        # Exhausted / near-identical retries — expected if sb ids are
        # also in human_review_required.
        sbids = [
            str(x) for x in (ev.get("source_bullet_ids") or [])
        ]
        if any(x in human_review_source_ids for x in sbids) or not sbids:
            covered_exhausted.append(record)
        else:
            record["gap_reason"] = (
                "LT has regeneration event with exhausted outcome but "
                "source bullet not in human_review_required — budget "
                "exhausted silently"
            )
            gaps.append(record)

    total = len(lts)
    return {
        "gate": "validate_regenerate_loop",
        "run_dir": str(run_p),
        "total_lts": total,
        "clean_lts": clean_lts,
        "failed_with_event_success": len(covered_success),
        "failed_with_language_bypass": len(covered_bypass),
        "failed_with_human_review": len(covered_exhausted),
        "gaps": gaps,
        "regeneration_events_count": len(events),
        "human_review_required_count": len(human_review),
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

    if not report["gaps"]:
        print(
            f"[PASS] validate_regenerate_loop: "
            f"clean={report['clean_lts']}, "
            f"success-after-retry={report['failed_with_event_success']}, "
            f"language-bypass={report['failed_with_language_bypass']}, "
            f"human-review={report['failed_with_human_review']}",
            file=sys.stderr,
        )
        return 0
    print(
        f"[FAIL] validate_regenerate_loop: {len(report['gaps'])} LTs ship "
        "with FAIL_SET flags that have no regeneration record",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
