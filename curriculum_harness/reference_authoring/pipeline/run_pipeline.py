"""Reference-authoring pipeline entry point.

Sequences (full): inventory → KUD classifier → KUD gates → competency
clustering → LT generator → Type 1/2 band statements + Type 3
observation indicators → extended quality report → output.

Supports ``--resume-from-kud``: skip inventory + KUD classification
and read the existing ``inventory.json`` and ``kud.json`` from
``--out``. This is the 4b-2 default path for Welsh CfW (KUD was
produced in 4b-1 and accepted post-review).

Writes the following artefacts to the output directory:

- ``inventory.json`` (unless resuming): full ``SourceInventory``.
- ``kud.json`` (unless resuming): full ``ReferenceKUD``.
- ``quality_report.md`` / ``quality_report.json``: extended gate and
  stage results.
- ``competency_clusters.json``: competency cluster set.
- ``lts.json``: LT set.
- ``band_statements.json``: Type 1/2 band progressions.
- ``observation_indicators.json``: Type 3 observation indicator sets.

If any halting gate fails OR any generation stage produces zero output
where output is required (e.g. no LTs), the pipeline exits with a
non-zero status and the partial artefacts are preserved for diagnosis.
No retry loop, no cleanup pass, no paper-overs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

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
from curriculum_harness.reference_authoring.lt.cluster_competencies import (
    cluster_competencies_sync,
)
from curriculum_harness.reference_authoring.lt.generate_lts import (
    generate_lts_sync,
)
from curriculum_harness.reference_authoring.lt.generate_band_statements import (
    generate_band_statements_sync,
)
from curriculum_harness.reference_authoring.lt.generate_observation_indicators import (
    generate_observation_indicators_sync,
)
from curriculum_harness.reference_authoring.types import (
    ContentBlock,
    HaltedBlock,
    KUDItem,
    ReferenceKUD,
    SourceInventory,
    dump_json,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot",
        required=False,
        default=None,
        help="Path to a Phase 0 run-snapshot directory containing content.txt and manifest.json. Required unless --resume-from-kud is set.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output directory for the reference corpus (will be created).",
    )
    parser.add_argument(
        "--resume-from-kud",
        action="store_true",
        help="Skip inventory + KUD classification; read existing inventory.json and kud.json from --out and proceed from competency clustering onwards.",
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
    parser.add_argument(
        "--skip-lts",
        action="store_true",
        help="Stop after KUD gates (legacy 4b-1 behaviour).",
    )
    return parser.parse_args(argv)


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


def _stage_summary_markdown(
    *,
    kud_report_md: str,
    cluster_set: Any,
    lt_set: Any,
    band_coll: Any,
    indicator_coll: Any,
) -> str:
    lines: list[str] = []
    lines.append(kud_report_md.rstrip())
    lines.append("")
    lines.append("## Stage: competency clustering")
    lines.append("")
    lines.append(f"- clusters: **{len(cluster_set.clusters)}**")
    lines.append(f"- overall stability flag: `{cluster_set.overall_stability_flag}`")
    if cluster_set.overall_stability_diagnostics:
        lines.append("- diagnostics:")
        for d in cluster_set.overall_stability_diagnostics:
            lines.append(f"  - {d}")
    lines.append("- per-cluster stability:")
    for c in cluster_set.clusters:
        lines.append(
            f"  - `{c.cluster_id}` ({c.competency_name}): {c.stability_flag} — "
            f"{len(c.kud_item_ids)} items, dkt={c.dominant_knowledge_type}"
        )
    lines.append("")
    lines.append("## Stage: LT generation")
    lines.append("")
    lines.append(f"- LTs: **{len(lt_set.lts)}** (halted clusters: {len(lt_set.halted_clusters)})")
    kt_counts = {"Type 1": 0, "Type 2": 0, "Type 3": 0}
    for lt in lt_set.lts:
        kt_counts[lt.knowledge_type] = kt_counts.get(lt.knowledge_type, 0) + 1
    lines.append(
        f"- knowledge-type split: Type 1={kt_counts['Type 1']}, "
        f"Type 2={kt_counts['Type 2']}, Type 3={kt_counts['Type 3']}"
    )
    stability_counts: dict[str, int] = {}
    for lt in lt_set.lts:
        stability_counts[lt.stability_flag] = stability_counts.get(lt.stability_flag, 0) + 1
    lines.append(f"- LT stability: {dict(stability_counts)}")
    if lt_set.halted_clusters:
        lines.append("- halted clusters:")
        for h in lt_set.halted_clusters:
            lines.append(f"  - `{h.get('cluster_id')}`: {h.get('halt_reason')} — {h.get('diagnostic', '')}")
    lines.append("")
    lines.append("## Stage: Type 1/2 band statements")
    lines.append("")
    lines.append(f"- band sets: **{len(band_coll.sets)}** (halted LTs: {len(band_coll.halted_lts)})")
    b_stability: dict[str, int] = {}
    for s in band_coll.sets:
        b_stability[s.stability_flag] = b_stability.get(s.stability_flag, 0) + 1
    lines.append(f"- stability: {dict(b_stability)}")
    if band_coll.halted_lts:
        lines.append("- halted:")
        for h in band_coll.halted_lts:
            lines.append(f"  - `{h.get('lt_id')}`: {h.get('halt_reason')} — {h.get('diagnostic', '')}")
    lines.append("")
    lines.append("## Stage: Type 3 observation indicators")
    lines.append("")
    lines.append(f"- indicator sets: **{len(indicator_coll.sets)}** (halted LTs: {len(indicator_coll.halted_lts)})")
    i_stability: dict[str, int] = {}
    for s in indicator_coll.sets:
        i_stability[s.stability_flag] = i_stability.get(s.stability_flag, 0) + 1
    lines.append(f"- stability: {dict(i_stability)}")
    if indicator_coll.halted_lts:
        lines.append("- halted:")
        for h in indicator_coll.halted_lts:
            lines.append(f"  - `{h.get('lt_id')}`: {h.get('halt_reason')} — {h.get('diagnostic', '')}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    load_dotenv()
    os.makedirs(args.out, exist_ok=True)

    inventory_path = os.path.join(args.out, "inventory.json")
    kud_path = os.path.join(args.out, "kud.json")

    if args.resume_from_kud:
        if not os.path.exists(inventory_path) or not os.path.exists(kud_path):
            print(
                f"[refauth] --resume-from-kud requires existing {inventory_path} and {kud_path}",
                flush=True,
            )
            return 2
        print(f"[refauth] resuming from existing KUD at {kud_path}", flush=True)
        inventory = _load_inventory(inventory_path)
        kud = _load_kud(kud_path)
    else:
        if not args.snapshot:
            print("[refauth] --snapshot is required unless --resume-from-kud is set", flush=True)
            return 2
        print(f"[refauth] inventory: reading {args.snapshot}", flush=True)
        inventory = build_inventory_from_snapshot(args.snapshot)
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
        dump_json(kud.to_dict(), kud_path)
        print(
            f"[refauth] kud: {len(kud.items)} items, {len(kud.halted_blocks)} halted blocks → {kud_path}",
            flush=True,
        )

    source_domain = args.domain or ("dispositional" if args.dispositional else "hierarchical")
    print(
        f"[refauth] KUD gates (dispositional={args.dispositional}, domain={source_domain})",
        flush=True,
    )
    report = run_kud_gates(
        inventory,
        kud,
        source_is_dispositional=args.dispositional,
        source_domain=source_domain,
    )
    kud_report_md = quality_report_to_markdown(report)
    report_json_path = os.path.join(args.out, "quality_report.json")
    dump_json(report.to_dict(), report_json_path)

    if report.halted_by:
        report_path = os.path.join(args.out, "quality_report.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(kud_report_md)
        print(
            f"[refauth] HALTED by KUD gate `{report.halted_by}`. "
            "Output preserved for diagnosis; exiting non-zero.",
            flush=True,
        )
        return 2

    if args.skip_lts:
        report_path = os.path.join(args.out, "quality_report.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(kud_report_md)
        print("[refauth] --skip-lts set; stopping after KUD gates.", flush=True)
        return 0

    print("[refauth] competency clustering (3x self-consistency)", flush=True)
    cluster_set = cluster_competencies_sync(inventory, kud, runs=args.runs)
    dump_json(cluster_set.to_dict(), os.path.join(args.out, "competency_clusters.json"))
    print(
        f"[refauth] clusters: {len(cluster_set.clusters)}; "
        f"overall={cluster_set.overall_stability_flag}",
        flush=True,
    )
    if cluster_set.overall_stability_flag == "cluster_unreliable":
        print("[refauth] HALTED: clustering unreliable.", flush=True)
        report_path = os.path.join(args.out, "quality_report.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(kud_report_md)
        return 2

    print("[refauth] LT generation (3x self-consistency)", flush=True)
    lt_set = generate_lts_sync(kud, cluster_set, runs=args.runs)
    dump_json(lt_set.to_dict(), os.path.join(args.out, "lts.json"))
    print(
        f"[refauth] LTs: {len(lt_set.lts)} (halted clusters: {len(lt_set.halted_clusters)})",
        flush=True,
    )
    if not lt_set.lts:
        print("[refauth] HALTED: no LTs produced.", flush=True)
        report_path = os.path.join(args.out, "quality_report.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(kud_report_md)
        return 2

    print("[refauth] Type 1/2 band statements (3x self-consistency)", flush=True)
    band_coll = generate_band_statements_sync(lt_set, runs=args.runs)
    dump_json(band_coll.to_dict(), os.path.join(args.out, "band_statements.json"))
    print(
        f"[refauth] band sets: {len(band_coll.sets)} (halted: {len(band_coll.halted_lts)})",
        flush=True,
    )

    print("[refauth] Type 3 observation indicators (3x self-consistency)", flush=True)
    indicator_coll = generate_observation_indicators_sync(lt_set, runs=args.runs)
    dump_json(indicator_coll.to_dict(), os.path.join(args.out, "observation_indicators.json"))
    print(
        f"[refauth] indicator sets: {len(indicator_coll.sets)} "
        f"(halted: {len(indicator_coll.halted_lts)})",
        flush=True,
    )

    extended_md = _stage_summary_markdown(
        kud_report_md=kud_report_md,
        cluster_set=cluster_set,
        lt_set=lt_set,
        band_coll=band_coll,
        indicator_coll=indicator_coll,
    )
    report_path = os.path.join(args.out, "quality_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(extended_md)
    print(f"[refauth] extended quality report → {report_path}", flush=True)

    print("[refauth] pipeline complete.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
