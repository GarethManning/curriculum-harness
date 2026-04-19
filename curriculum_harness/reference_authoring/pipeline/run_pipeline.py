"""Reference-authoring pipeline entry point.

Sequences: inventory → KUD classifier → quality gates → output.

Writes three artefacts to the output directory:

- ``inventory.json``: full ``SourceInventory`` with content blocks.
- ``kud.json``: full ``ReferenceKUD`` with items, halted blocks, and
  per-run self-consistency records.
- ``quality_report.md``: human-readable gate results.

If any halting gate fails, the pipeline exits with a non-zero status
and the incomplete artefacts are preserved for diagnosis. No retry
loop, no cleanup pass, no paper-overs.
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from curriculum_harness.reference_authoring.gates.kud_gates import (
    quality_report_to_markdown,
    run_kud_gates,
)
from curriculum_harness.reference_authoring.inventory import (
    build_inventory_from_snapshot,
)
from curriculum_harness.reference_authoring.kud.classify_kud import (
    classify_inventory_sync,
    DEFAULT_MODEL,
    DEFAULT_RUNS,
    DEFAULT_TEMPERATURE,
)
from curriculum_harness.reference_authoring.types import dump_json


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot",
        required=True,
        help="Path to a Phase 0 run-snapshot directory containing content.txt and manifest.json",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for the reference corpus (will be created).",
    )
    parser.add_argument(
        "--dispositional",
        action="store_true",
        help="Declare the source as a dispositional-domain anchor (enables Type 3 distribution check; also sets domain to 'dispositional' if --domain is unset).",
    )
    parser.add_argument(
        "--domain",
        choices=("hierarchical", "horizontal", "dispositional"),
        default=None,
        help="Source domain for the artefact-count-ratio gate. If omitted, inferred from --dispositional (True → dispositional, False → hierarchical).",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model ID for KUD classification (default {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=DEFAULT_RUNS,
        help=f"Self-consistency runs per block (default {DEFAULT_RUNS})",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Classification sampling temperature (default {DEFAULT_TEMPERATURE})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    load_dotenv()
    os.makedirs(args.out, exist_ok=True)

    print(f"[refauth] inventory: reading {args.snapshot}", flush=True)
    inventory = build_inventory_from_snapshot(args.snapshot)
    inventory_path = os.path.join(args.out, "inventory.json")
    dump_json(inventory.to_dict(), inventory_path)
    print(
        f"[refauth] inventory: {len(inventory.content_blocks)} blocks → {inventory_path}",
        flush=True,
    )

    print(
        f"[refauth] classifying with model={args.model} runs={args.runs} temperature={args.temperature}",
        flush=True,
    )
    kud = classify_inventory_sync(
        inventory,
        model=args.model,
        temperature=args.temperature,
        runs=args.runs,
    )
    kud_path = os.path.join(args.out, "kud.json")
    dump_json(kud.to_dict(), kud_path)
    print(
        f"[refauth] kud: {len(kud.items)} items, {len(kud.halted_blocks)} halted blocks → {kud_path}",
        flush=True,
    )

    source_domain = args.domain or ("dispositional" if args.dispositional else "hierarchical")
    print(
        f"[refauth] running quality gates (dispositional={args.dispositional}, domain={source_domain})",
        flush=True,
    )
    report = run_kud_gates(
        inventory,
        kud,
        source_is_dispositional=args.dispositional,
        source_domain=source_domain,
    )
    report_md = quality_report_to_markdown(report)
    report_path = os.path.join(args.out, "quality_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report_md)
    report_json_path = os.path.join(args.out, "quality_report.json")
    dump_json(report.to_dict(), report_json_path)
    print(f"[refauth] quality report → {report_path}", flush=True)

    if report.halted_by:
        print(
            f"[refauth] HALTED by gate `{report.halted_by}`. "
            "Output preserved for diagnosis; exiting non-zero.",
            flush=True,
        )
        return 2
    print("[refauth] all halting gates passed.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
