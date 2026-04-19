"""Re-cluster an existing reference corpus's KUD without regenerating downstream artefacts.

Reads ``inventory.json`` and ``kud.json`` from ``--corpus``, runs
``cluster_competencies_sync`` with the requested ``--model``, and writes
the resulting cluster set to ``competency_clusters.json``.

Intended for probe runs (escalating cluster model when Haiku clustering
is unstable) before committing to a full ``--resume-from-kud`` pipeline
run. The cluster-set JSON carries the model + runs + stability flag so
the caller can judge whether to proceed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from curriculum_harness.reference_authoring.lt.cluster_competencies import (
    cluster_competencies_sync,
)
from curriculum_harness.reference_authoring.types import (
    ContentBlock,
    HaltedBlock,
    KUDItem,
    ReferenceKUD,
    SourceInventory,
    dump_json,
)


def _load_inventory(path: str) -> SourceInventory:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return SourceInventory(
        source_slug=raw["source_slug"],
        snapshot_path=raw["snapshot_path"],
        manifest_content_hash=raw["manifest_content_hash"],
        phase0_version=raw["phase0_version"],
        source_reference=raw["source_reference"],
        content_blocks=[ContentBlock(**b) for b in raw["content_blocks"]],
    )


def _load_kud(path: str) -> ReferenceKUD:
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return ReferenceKUD(
        source_slug=raw["source_slug"],
        snapshot_path=raw["snapshot_path"],
        classification_model=raw.get("classification_model", ""),
        classification_temperature=raw.get("classification_temperature", 0.3),
        self_consistency_runs=raw.get("self_consistency_runs", 3),
        items=[KUDItem(**i) for i in raw["items"]],
        halted_blocks=[HaltedBlock(**h) for h in raw["halted_blocks"]],
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--model", default=None, help="Override cluster model")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument(
        "--out-name",
        default="competency_clusters.json",
        help="Output filename within the corpus directory.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    load_dotenv()
    inventory = _load_inventory(os.path.join(args.corpus, "inventory.json"))
    kud = _load_kud(os.path.join(args.corpus, "kud.json"))
    kwargs = {"runs": args.runs}
    if args.model:
        kwargs["model"] = args.model
    print(
        f"[cluster_only] clustering {len(kud.items)} KUD items "
        f"(runs={args.runs}, model={args.model or 'default'})",
        flush=True,
    )
    cs = cluster_competencies_sync(inventory, kud, **kwargs)
    out_path = os.path.join(args.corpus, args.out_name)
    dump_json(cs.to_dict(), out_path)
    print(
        f"[cluster_only] clusters={len(cs.clusters)} "
        f"flag={cs.overall_stability_flag} → {out_path}",
        flush=True,
    )
    for d in cs.overall_stability_diagnostics:
        print(f"[cluster_only]   - {d}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
