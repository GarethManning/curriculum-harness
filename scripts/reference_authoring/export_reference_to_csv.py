"""Export a reference corpus as three source-prefixed CSV files.

Reads ``kud.json``, ``lts.json``, ``band_statements.json``,
``observation_indicators.json``, ``competency_clusters.json``, and
``progression_structure.json`` from a reference-corpus directory and
produces three CSVs in the same directory:

1. ``<prefix>-kud.csv`` — one row per KUD item; halted blocks
   appended at the bottom with ``kud_column = HALTED``.
2. ``<prefix>-learning-targets.csv`` — one row per LT, with band
   statements inlined for Type 1/2 LTs and left empty for Type 3 LTs
   (Type 3 LTs carry observation indicators in the third file).
   Band columns use the source's native band labels (Progression Step
   1-5 for Welsh CfW; Grade 7 for a single-grade Common Core or
   Ontario source; etc.). Multi-band sources produce one column per
   band; single-band sources produce one band column.
3. ``<prefix>-observation-indicators.csv`` — one row per (Type-3 LT,
   band) combination. For multi-band sources each Type 3 LT produces
   one row per band; for single-band sources each Type 3 LT produces
   one row. Parent prompts and developmental-conversation protocol
   appear on the FIRST band row per LT only to avoid redundancy.

The export is a pure view over the corpus JSON; it runs no pipeline
stages and does not modify any source artefact.

Encoding is UTF-8. Commas and quotes inside cell values are handled
by the stdlib csv module (double-quote wrapping). Newlines inside
cells are replaced with ``;  `` for readability.

Usage:

    python -m scripts.reference_authoring.export_reference_to_csv \\
        --corpus docs/reference-corpus/welsh-cfw-health-wellbeing \\
        --prefix welsh-cfw-hwb
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Any

from curriculum_harness.reference_authoring.progression import (
    band_label_slug,
    load_progression_structure,
)


NEWLINE_REPLACEMENT = ";  "


def _load(path: str) -> dict[str, Any] | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _clean(value: Any) -> str:
    """Normalise a value for a CSV cell.

    - None → empty string.
    - Multi-line strings: newlines replaced with ``;  `` for readability.
    - Anything else: stringified.
    """
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\n", NEWLINE_REPLACEMENT)
    return s.strip()


def _join_list(items: list[Any], sep: str = "; ") -> str:
    return _clean(sep.join(str(x) for x in (items or [])))


def _source_excerpt(inventory: dict[str, Any] | None, block_id: str) -> str:
    if not inventory or not block_id:
        return ""
    for b in inventory.get("content_blocks", []):
        if b.get("block_id") == block_id:
            line_start = b.get("line_start")
            line_end = b.get("line_end")
            span = (
                f"L{line_start}"
                if line_start == line_end
                else f"L{line_start}-{line_end}"
            )
            return f"{span}: {b.get('raw_text', '')}"
    return ""


def _cluster_label(cluster: dict[str, Any]) -> str:
    return f"{cluster.get('cluster_id', '')}: {cluster.get('competency_name', '')}".strip(
        ": "
    )


KUD_COLUMN_ORDER = ("know", "understand", "do_skill", "do_disposition")


def export_kud(
    *,
    kud: dict[str, Any],
    inventory: dict[str, Any] | None,
    out_path: str,
) -> int:
    """Write the KUD CSV grouped by ``kud_column`` in the canonical
    order know → understand → do_skill → do_disposition, then HALTED
    blocks at the bottom. Within each group, items are sorted
    alphabetically by ``item_id`` (which reflects source-block order
    because item ids carry the block id as a prefix). Groups are
    separated by a visual blank row whose ``item_id`` is ``---`` and
    whose other columns are empty.
    """
    header = [
        "item_id",
        "kud_column",
        "knowledge_type",
        "assessment_route",
        "content",
        "source_block_id",
        "source_excerpt",
        "classification_stability",
        "underspecification_flag",
        "rationale",
    ]
    empty_cols = [""] * (len(header) - 1)
    separator_row = ["---", *empty_cols]

    # Group items by kud_column, preserving source-block order via item_id.
    grouped: dict[str, list[dict[str, Any]]] = {c: [] for c in KUD_COLUMN_ORDER}
    unknown_column: list[dict[str, Any]] = []
    for item in kud.get("items", []):
        col = item.get("kud_column", "")
        if col in grouped:
            grouped[col].append(item)
        else:
            unknown_column.append(item)
    for col in grouped:
        grouped[col].sort(key=lambda i: i.get("item_id", ""))
    unknown_column.sort(key=lambda i: i.get("item_id", ""))
    halted = sorted(kud.get("halted_blocks", []), key=lambda h: h.get("block_id", ""))

    rows_written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)

        groups_with_content: list[tuple[str, list[Any]]] = []
        for col in KUD_COLUMN_ORDER:
            if grouped[col]:
                groups_with_content.append((col, grouped[col]))
        if unknown_column:
            groups_with_content.append(("__unknown__", unknown_column))
        if halted:
            groups_with_content.append(("HALTED", halted))

        for group_index, (group_name, group_items) in enumerate(groups_with_content):
            if group_index > 0:
                writer.writerow(separator_row)
                rows_written += 1
            if group_name == "HALTED":
                for h in group_items:
                    writer.writerow(
                        [
                            _clean(h.get("block_id")),
                            "HALTED",
                            "",
                            "",
                            _clean(h.get("source_block_raw_text")),
                            _clean(h.get("block_id")),
                            _clean(_source_excerpt(inventory, h.get("block_id", ""))),
                            "",
                            "",
                            _clean(
                                f"{h.get('halt_reason', '')}: {h.get('diagnostic', '')}"
                            ),
                        ]
                    )
                    rows_written += 1
            else:
                for item in group_items:
                    writer.writerow(
                        [
                            _clean(item.get("item_id")),
                            _clean(item.get("kud_column")),
                            _clean(item.get("knowledge_type")),
                            _clean(item.get("assessment_route")),
                            _clean(item.get("content_statement")),
                            _clean(item.get("source_block_id")),
                            _clean(
                                _source_excerpt(
                                    inventory, item.get("source_block_id", "")
                                )
                            ),
                            _clean(item.get("stability_flag")),
                            _clean(item.get("underspecification_flag") or "null"),
                            _clean(item.get("classification_rationale")),
                        ]
                    )
                    rows_written += 1
    return rows_written


def export_lts(
    *,
    clusters: dict[str, Any] | None,
    lts: dict[str, Any],
    band_sets: dict[str, Any] | None,
    band_labels: list[str],
    out_path: str,
) -> int:
    cluster_by_id: dict[str, dict[str, Any]] = {}
    if clusters:
        for c in clusters.get("clusters", []):
            cluster_by_id[c.get("cluster_id", "")] = c
    bands_by_lt: dict[str, dict[str, Any]] = {}
    if band_sets:
        for s in band_sets.get("sets", []):
            bands_by_lt[s.get("lt_id", "")] = s

    band_columns = [band_label_slug(label) for label in band_labels]

    rows_written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        header: list[str] = [
            "competency_cluster",
            "lt_id",
            "lt_name",
            "lt_definition",
            "knowledge_type",
            "assessment_route",
            "lt_stability",
            "kud_items_covered",
            "prerequisites",
        ]
        header.extend(band_columns)
        header.extend(["band_statements_stability", "band_gate_status"])
        writer.writerow(header)
        for lt in lts.get("lts", []):
            cluster = cluster_by_id.get(lt.get("cluster_id", ""), {})
            competency_label = _cluster_label(cluster) if cluster else _clean(
                lt.get("competency_name", "")
            )
            kt = lt.get("knowledge_type", "")
            band_cells: list[str] = []
            if kt == "Type 3":
                band_cells = ["" for _ in band_labels]
                band_stability = ""
                gate_status = "N/A (Type 3)"
            else:
                bset = bands_by_lt.get(lt.get("lt_id", ""))
                if bset is None:
                    band_cells = ["" for _ in band_labels]
                    band_stability = "missing"
                    gate_status = "missing"
                else:
                    by_band: dict[str, str] = {
                        s.get("band", ""): s.get("statement", "")
                        for s in bset.get("statements", [])
                    }
                    band_cells = [_clean(by_band.get(label, "")) for label in band_labels]
                    band_stability = bset.get("stability_flag", "")
                    gate_status = "PASS" if bset.get("quality_gate_passed", True) else "FAIL"
            row: list[str] = [
                _clean(competency_label),
                _clean(lt.get("lt_id")),
                _clean(lt.get("lt_name")),
                _clean(lt.get("lt_definition")),
                _clean(kt),
                _clean(lt.get("assessment_route")),
                _clean(lt.get("stability_flag")),
                _join_list(lt.get("kud_item_ids")),
                _join_list(lt.get("prerequisite_lts")),
            ]
            row.extend(band_cells)
            row.extend([_clean(band_stability), _clean(gate_status)])
            writer.writerow(row)
            rows_written += 1
    return rows_written


def export_observation_indicators(
    *,
    clusters: dict[str, Any] | None,
    lts: dict[str, Any],
    indicator_coll: dict[str, Any] | None,
    band_labels: list[str],
    out_path: str,
) -> int:
    cluster_by_id: dict[str, dict[str, Any]] = {}
    if clusters:
        for c in clusters.get("clusters", []):
            cluster_by_id[c.get("cluster_id", "")] = c
    lt_by_id: dict[str, dict[str, Any]] = {}
    for lt in lts.get("lts", []):
        lt_by_id[lt.get("lt_id", "")] = lt

    band_order: dict[str, int] = {label: i for i, label in enumerate(band_labels)}

    rows_written = 0
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [
                "competency_cluster",
                "lt_id",
                "lt_name",
                "prerequisites",
                "band",
                "indicator_1",
                "indicator_2",
                "indicator_3",
                "self_reflection_prompt",
                "parent_prompt_1",
                "parent_prompt_2",
                "parent_prompt_3",
                "observation_stability",
            ]
        )
        if not indicator_coll:
            return rows_written
        for iset in indicator_coll.get("sets", []):
            lt_id = iset.get("lt_id", "")
            lt = lt_by_id.get(lt_id, {})
            cluster = cluster_by_id.get(lt.get("cluster_id", ""), {})
            competency_label = _cluster_label(cluster) if cluster else _clean(
                lt.get("competency_name", "")
            )
            parent_prompts = iset.get("parent_prompts", []) or []
            parents = parent_prompts + [""] * (3 - len(parent_prompts))
            band_entries = sorted(
                iset.get("bands", []),
                key=lambda b: band_order.get(b.get("band", ""), 99),
            )
            for idx, band in enumerate(band_entries):
                behaviours = band.get("observable_behaviours", []) or []
                indicators = behaviours + [""] * (3 - len(behaviours))
                if idx == 0:
                    p1, p2, p3 = parents[0], parents[1], parents[2]
                else:
                    p1 = p2 = p3 = ""
                writer.writerow(
                    [
                        _clean(competency_label),
                        _clean(lt_id),
                        _clean(lt.get("lt_name")),
                        _join_list(iset.get("prerequisite_lts")),
                        _clean(band.get("band")),
                        _clean(indicators[0]),
                        _clean(indicators[1]),
                        _clean(indicators[2]),
                        _clean(band.get("self_reflection_prompt")),
                        _clean(p1),
                        _clean(p2),
                        _clean(p3),
                        _clean(iset.get("stability_flag")),
                    ]
                )
                rows_written += 1
    return rows_written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        required=True,
        help="Reference-corpus directory containing kud.json, lts.json, etc.",
    )
    parser.add_argument(
        "--prefix",
        required=True,
        help="File-name prefix for the three CSVs (e.g. 'welsh-cfw-hwb').",
    )
    args = parser.parse_args(argv)

    kud = _load(os.path.join(args.corpus, "kud.json"))
    if kud is None:
        print(f"[csv-export] no kud.json in {args.corpus}", flush=True)
        return 2
    inventory = _load(os.path.join(args.corpus, "inventory.json"))
    clusters = _load(os.path.join(args.corpus, "competency_clusters.json"))
    lts = _load(os.path.join(args.corpus, "lts.json"))
    band_sets = _load(os.path.join(args.corpus, "band_statements.json"))
    indicator_coll = _load(os.path.join(args.corpus, "observation_indicators.json"))

    progression_path = os.path.join(args.corpus, "progression_structure.json")
    if not os.path.exists(progression_path):
        print(
            f"[csv-export] missing progression_structure.json at {progression_path}; "
            "the band columns require source-native progression labels and the "
            "exporter does NOT default to A-D. Re-run the pipeline (or copy the "
            "structure file) before exporting.",
            flush=True,
        )
        return 2
    progression = load_progression_structure(progression_path)
    band_labels = list(progression.band_labels)
    if not band_labels:
        print(
            f"[csv-export] progression_structure.json at {progression_path} has no "
            "band_labels; cannot build LT or indicator CSVs.",
            flush=True,
        )
        return 2
    print(
        f"[csv-export] progression: {progression.source_type} | "
        f"{progression.band_count} band(s) | confidence={progression.detection_confidence}",
        flush=True,
    )

    kud_path = os.path.join(args.corpus, f"{args.prefix}-kud.csv")
    lt_path = os.path.join(args.corpus, f"{args.prefix}-learning-targets.csv")
    ind_path = os.path.join(args.corpus, f"{args.prefix}-observation-indicators.csv")

    kud_rows = export_kud(kud=kud, inventory=inventory, out_path=kud_path)
    print(f"[csv-export] {kud_path}: {kud_rows} rows", flush=True)

    if lts is not None:
        lt_rows = export_lts(
            clusters=clusters,
            lts=lts,
            band_sets=band_sets,
            band_labels=band_labels,
            out_path=lt_path,
        )
        print(f"[csv-export] {lt_path}: {lt_rows} rows", flush=True)
    else:
        print("[csv-export] lts.json missing; skipped learning-targets CSV", flush=True)

    if lts is not None and indicator_coll is not None:
        ind_rows = export_observation_indicators(
            clusters=clusters,
            lts=lts,
            indicator_coll=indicator_coll,
            band_labels=band_labels,
            out_path=ind_path,
        )
        print(f"[csv-export] {ind_path}: {ind_rows} rows", flush=True)
    else:
        print(
            "[csv-export] observation_indicators.json or lts.json missing; "
            "skipped observation-indicators CSV",
            flush=True,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
