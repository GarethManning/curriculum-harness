#!/usr/bin/env python3
"""Foundation moment 1 — architecture diagnosis verifiability
(VALIDITY.md assertion c).

**Assertion.** Every strand label in the run's architecture diagnosis
traces to some independent source evidence above the matcher's
confidence threshold. Strands with no independent support are flagged
as unverifiable.

**How "independent" is defined here.** The full source-proxy corpus
includes strand labels and their values_basis — a strand would
trivially match itself. For this gate we build an *independent*
corpus that excludes the strand being checked: only the Phase 1
`curriculum_profile` items (`rationale`, `pages_note`, `format`) and
the OTHER strands' labels + values_basis count as independent evidence.

**Reads.** Same artefacts as `validate_source_coverage.py`.

**Writes.** JSON report: `{total_strands, unverifiable_count,
unverifiable: [...]}`.

**Exit codes.** 0 = all strands verifiable. 1 = one or more
unverifiable. 2 = could not run.

### Adjacent mechanisms this gate does NOT check

1. **Values_basis authorship.** The values_basis strings are authored
   by Phase 2 itself; they are not primary-source evidence. Scoring a
   strand against its *own* values_basis is explicitly excluded by
   the independent-corpus construction, but scoring against OTHER
   strands' values_basis counts — which is Phase-2-internal coherence
   rather than source-fidelity. The adjacent-mechanism consequence:
   this gate catches strands that are wildly outlying from the
   pipeline's own world-view, not strands that are collectively
   hallucinated.
2. **Level model and scoping strategy.** Out of scope for this gate.
   The brief is strand-label focused; level_model / scoping_strategy
   verifiability is a follow-up.
3. **Label generality.** A maximally generic label ("Reasoning",
   "Skills") will match lots of text and trivially pass. See
   adjacent mechanism #1 in the matcher docstring.
4. **Language.** English-only matcher. For non-English sources the
   gate reads Phase 1/2 English rendering, same as the other
   foundation-moment-1 gates.
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


def _strand_label_list(architecture: dict | None) -> list[tuple[str, str]]:
    """Return [(label, provenance), ...] for every strand we can find.

    Handles both the v1.2+ shape (`strands[]`) and the legacy shape
    (element lists). A run produced by an older harness version may
    have only the element lists and no strands[].
    """
    if not architecture:
        return []
    out: list[tuple[str, str]] = []
    for i, s in enumerate(architecture.get("strands") or []):
        label = s.get("label") or ""
        if label:
            out.append((label, f"architecture.strands[{i}].label"))
    if out:
        return out
    for key in (
        "hierarchical_elements",
        "horizontal_elements",
        "dispositional_elements",
    ):
        for j, el in enumerate(architecture.get(key) or []):
            if el:
                out.append((el, f"architecture.{key}[{j}]"))
    return out


def _independent_corpus(
    arte,  # RunArtefacts
    exclude_strand_index: int | None,
) -> list[str]:
    """Build a source-proxy corpus that excludes the given strand (so a
    strand can't trivially match itself)."""
    texts: list[str] = []
    for item in arte.source_corpus:
        # Exclude the item that IS this strand's own label+values_basis.
        if (
            exclude_strand_index is not None
            and item.provenance
            == f"architecture.strands[{exclude_strand_index}].label+values_basis"
        ):
            continue
        texts.append(item.text)
    return texts


def run(run_dir: str) -> dict:
    arte = load_run(run_dir)
    strands = _strand_label_list(arte.architecture)
    unverifiable: list[dict] = []
    per_strand: list[dict] = []

    for i, (label, prov) in enumerate(strands):
        # Index in strands[] corresponds to i IF we pulled from strands[].
        # If we fell back to element lists, there is no strands[] index
        # to exclude — the exclusion is then a no-op.
        exclude_i = i if (arte.architecture or {}).get("strands") else None
        corpus = _independent_corpus(arte, exclude_i)
        top = best_match(label, corpus)
        top_score = top.score if top else 0.0
        record = {
            "strand_index": i,
            "label": label,
            "provenance": prov,
            "best_evidence_text": top.matched_item if top else None,
            "best_score": top_score,
        }
        per_strand.append(record)
        if top_score < MATCH_THRESHOLD:
            unverifiable.append(record)

    total = len(strands)
    verifiable = total - len(unverifiable)
    verifiability_pct = round((verifiable / total) * 100, 1) if total else 0.0
    return {
        "gate": "validate_architecture_diagnosis",
        "run_dir": str(arte.run_dir),
        "threshold": MATCH_THRESHOLD,
        "corpus_mode": arte.corpus_mode,
        "corpus_warning": arte.corpus_warning,
        "total_strands": total,
        "verifiable": verifiable,
        "unverifiable_count": len(unverifiable),
        "verifiability_pct": verifiability_pct,
        "unverifiable": unverifiable,
        "per_strand": per_strand,
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

    if report["unverifiable_count"] == 0:
        print(
            f"[PASS] validate_architecture_diagnosis:"
            f" {report['verifiability_pct']}%"
            f" ({report['verifiable']}/{report['total_strands']})",
            file=sys.stderr,
        )
        return 0
    print(
        f"[FAIL] validate_architecture_diagnosis:"
        f" {report['unverifiable_count']} unverifiable strand(s)"
        f" (verifiability {report['verifiability_pct']}%)",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
