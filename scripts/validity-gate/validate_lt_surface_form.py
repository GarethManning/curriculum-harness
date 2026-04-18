#!/usr/bin/env python3
"""Foundation moment 2 — learning-target surface form
(VALIDITY.md assertion d).

**Assertion.** Every emitted learning target satisfies the surface-form
contract — max word count, single-construct only, no embedded examples,
stem matching the active ``lt_statement_format`` (``i_can`` by default,
``outcome_statement`` for higher-ed syllabi, ``competency_descriptor``
for competency-framework rows).

Status: implemented (Session 3c, 2026-04-18). The regeneration loop
live in Phase 4 means surface-form failures are now regeneratable — a
final LT set with surviving surface-form failures indicates either an
exhausted retry budget (surfaced in `human_review_required`) or a
non-English source for which SOURCE_FAITHFULNESS_FAIL regeneration was
bypassed.

**Reads.** ``<runId>_learning_targets_v1.json`` plus the run config's
``curriculumProfile`` (to resolve the active format) via the
``<runId>_curriculum_profile_v1.json`` artefact. Optionally reads
``<runId>_regeneration_events_v1.json`` to cross-reference LTs that
were knowingly shipped flagged (language bypass).

**Writes.** JSON report:
``{total_lts, surface_form_failures: [...], failure_count,
surface_form_pct, language_bypass_count}``.

**Exit codes.** 0 = every LT passes surface-form (or was language-
bypassed with a SOURCE_FAITHFULNESS_FAIL-only reason). 1 = one or more
LTs ship with an un-bypassed surface-form failure. 2 = could not run.

### Adjacent mechanisms this gate does NOT check

1. **Semantic compound detection.** The naive "and"-splitter catches
   some compound LTs but treats "analyse and evaluate" (two distinct
   constructs) the same as "read and write" (sometimes a single
   construct). Upgrade path: a richer compound detector.
2. **Format appropriateness to the source.** If a config sets
   ``lt_statement_format = "i_can"`` on a document that should be
   ``outcome_statement``, this gate accepts whatever the config says.
   The mismatch is a Phase 1 profile-resolution problem, not a
   surface-form problem.
3. **Verifying regeneration actually ran.** That is gate (e)'s job
   (``validate_regenerate_loop.py``). This gate only checks the final
   LT set.
4. **Cross-LT duplication.** Two LTs with the same statement are both
   surface-form-valid; this gate says nothing about corpus-level
   uniqueness.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
ROOT = HERE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from _run_loader import _find_json, _load_json  # noqa: E402

# Shared with Phase 4 — surface-form rule constants live in one place.
ICAN_PREFIX = "I can "
MAX_WORDS = 25

VERB_HINTS = (
    " analyze ",
    " explain ",
    " describe ",
    " compare ",
    " evaluate ",
    " demonstrate ",
    " identify ",
    " interpret ",
    " apply ",
    " create ",
    " solve ",
    " use ",
    " understand ",
    " assess ",
    " revise ",
)


def _resolve_fmt(profile: dict | None) -> str:
    profile = profile or {}
    oc = profile.get("output_conventions") or {}
    fmt = str(oc.get("lt_statement_format", "")).strip().lower()
    if fmt in ("i_can", "outcome_statement", "competency_descriptor"):
        return fmt
    fam = str(profile.get("document_family", "")).strip().lower()
    if fam == "higher_ed_syllabus":
        return "outcome_statement"
    return "i_can"


def _surface_failures(stmt: str, fmt: str) -> list[str]:
    """Return the list of surface-form failure flags for a statement.

    Mirrors `curriculum_harness.phases.phase4_lt_generation._validate_lt`
    for the FAIL_SET subset relevant to surface form (not source
    faithfulness or type-compound).
    """
    s = (stmt or "").strip()
    flags: list[str] = []
    if not s:
        flags.append("MISSING_LT_STATEMENT")
        return flags
    words = s.split()
    if len(words) > MAX_WORDS:
        flags.append("EXCEEDS_WORD_LIMIT")
    if fmt == "i_can":
        if not s.startswith(ICAN_PREFIX):
            flags.append("MISSING_I_CAN_FORMAT")
    elif fmt == "outcome_statement":
        if s.lower().startswith("i can "):
            flags.append("LT_FORMAT_EXPECTATION_MISMATCH")
    elif fmt == "competency_descriptor":
        low = s.lower()
        if low.startswith("i can ") or low.startswith("i "):
            flags.append("LT_FORMAT_EXPECTATION_MISMATCH")
    if re.search(r"\([^)]+\)", s):
        flags.append("EMBEDDED_EXAMPLE")
    if fmt == "i_can" and " and " in s.lower():
        parts = re.split(r"\s+and\s+", s.lower(), maxsplit=1)
        if len(parts) == 2:
            v0 = any(v in f" {parts[0]} " for v in VERB_HINTS)
            v1 = any(v in f" {parts[1]} " for v in VERB_HINTS)
            if v0 and v1:
                flags.append("POSSIBLE_COMPOUND")
    return flags


# FAIL_SET subset relevant to surface form only. POSSIBLE_COMPOUND and
# LT_FORMAT_EXPECTATION_MISMATCH are warnings (not in FAIL_SET).
SURFACE_FAIL_SET: frozenset[str] = frozenset({
    "MISSING_LT_STATEMENT",
    "EXCEEDS_WORD_LIMIT",
    "MISSING_I_CAN_FORMAT",
    "EMBEDDED_EXAMPLE",
})


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

    profile = _load_json(_find_json(run_p, "curriculum_profile_v1.json"))
    fmt = _resolve_fmt(profile)

    regen_path = _find_json(run_p, "regeneration_events_v1.json")
    regen_doc = _load_json(regen_path) if regen_path else None
    regen_events = (regen_doc or {}).get("regeneration_events") or []
    # Which LT statements were shipped with language-bypass? They will
    # carry SOURCE_FAITHFULNESS_FAIL but no surface-form failure — the
    # bypass does not excuse surface-form failures.
    bypass_statements: set[str] = set()
    for ev in regen_events:
        if "SOURCE_LANGUAGE_BYPASS" in (ev.get("annotations") or []):
            attempts = ev.get("attempts") or []
            if attempts:
                bypass_statements.add(
                    str(attempts[-1].get("statement") or "").strip()
                )

    failures: list[dict] = []
    bypass_count = 0
    for i, lt in enumerate(lts):
        stmt = str(lt.get("statement", ""))
        row_fmt = (
            str(lt.get("lt_statement_format") or "").strip().lower() or fmt
        )
        detected = _surface_failures(stmt, row_fmt)
        surface_fails = [f for f in detected if f in SURFACE_FAIL_SET]
        if not surface_fails:
            if stmt.strip() in bypass_statements:
                bypass_count += 1
            continue
        failures.append(
            {
                "lt_index": i,
                "statement": stmt,
                "format": row_fmt,
                "surface_failures": surface_fails,
                "language_bypass": stmt.strip() in bypass_statements,
            }
        )

    total = len(lts)
    passing = total - len(failures)
    surface_form_pct = round((passing / total) * 100, 1) if total else 0.0
    return {
        "gate": "validate_lt_surface_form",
        "run_dir": str(run_p),
        "total_lts": total,
        "surface_form_pct": surface_form_pct,
        "passing": passing,
        "failure_count": len(failures),
        "language_bypass_count": bypass_count,
        "surface_form_failures": failures,
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

    if report["failure_count"] == 0:
        print(
            f"[PASS] validate_lt_surface_form: "
            f"{report['surface_form_pct']}% "
            f"({report['passing']}/{report['total_lts']})",
            file=sys.stderr,
        )
        return 0
    print(
        f"[FAIL] validate_lt_surface_form: "
        f"{report['failure_count']} LTs fail surface-form "
        f"(surface-form {report['surface_form_pct']}%)",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
