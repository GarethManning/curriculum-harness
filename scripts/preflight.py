#!/usr/bin/env python3
"""REAL wellbeing preflight.

Run at session start. Six checks against the canonical band convention and the
live structured artefacts. Exit 0 on all-pass, 1 on any fail.

Usage:
    python scripts/preflight.py
    python scripts/preflight.py --criterion-bank <path> --unified-data <path> --expected-lts 21
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from band_constants import BAND_LABELS, VALID_BAND_LETTERS

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BANK = (
    REPO_ROOT / "docs" / "reference-corpus" / "real-wellbeing" / "criterion-bank-v5_1.json"
)
DEFAULT_UNIFIED = (
    REPO_ROOT / "docs" / "reference-corpus" / "real-wellbeing" / "unified-wellbeing-data-v6.json"
)
DEFAULT_EXPECTED_LTS = 21

SCRIPTS_DIR = REPO_ROOT / "scripts"
SELF_NAME = "band_constants.py"


def _fmt_pass_fail(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


# ── Check 1 — band_label compliance ────────────────────────────────────────────


def check_band_label_compliance(criteria: list[dict]) -> tuple[bool, str]:
    canonical = set(BAND_LABELS.values())
    compliant = 0
    non_compliant: list[tuple[str, str]] = []
    for c in criteria:
        if "band_label" not in c:
            continue
        label = c["band_label"]
        if label in canonical:
            compliant += 1
        else:
            non_compliant.append((c.get("criterion_id", "<missing id>"), label))
    details = f"{compliant} compliant, {len(non_compliant)} non-compliant"
    if non_compliant:
        sample = "; ".join(
            f"{cid}='{lab}'" for cid, lab in non_compliant[:10]
        )
        details += f". First {min(10, len(non_compliant))}: {sample}"
    return len(non_compliant) == 0, details


# ── Check 2 — LT count ─────────────────────────────────────────────────────────


def check_lt_count(lts: list[dict], expected: int) -> tuple[bool, str]:
    actual = len(lts)
    return actual == expected, f"expected {expected} LTs, got {actual}"


# ── Check 3 — DAG validity on unified data edges ───────────────────────────────


def _collect_edges_from_unified(lts: list[dict]) -> tuple[set[str], list[tuple[str, str]]]:
    """Collect prerequisite edges between LTs from the unified data.

    Each LT may carry prerequisite_lt_ids on a per-band basis; we aggregate
    across bands into a single LT-level prerequisite graph. An edge (u, v) means
    u is prerequisite to v.
    """
    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    for lt in lts:
        lt_id = lt.get("lt_id")
        if not lt_id:
            continue
        nodes.add(lt_id)
        bands = lt.get("bands") or {}
        if isinstance(bands, dict):
            for _band_letter, band_obj in bands.items():
                if not isinstance(band_obj, dict):
                    continue
                for prereq in band_obj.get("prerequisite_lt_ids", []) or []:
                    nodes.add(prereq)
                    edges.append((prereq, lt_id))
    return nodes, edges


def check_dag_validity(lts: list[dict]) -> tuple[bool, str]:
    nodes, edges = _collect_edges_from_unified(lts)
    indeg: dict[str, int] = {n: 0 for n in nodes}
    out: dict[str, list[str]] = {n: [] for n in nodes}
    for u, v in edges:
        out.setdefault(u, []).append(v)
        indeg[v] = indeg.get(v, 0) + 1
        indeg.setdefault(u, indeg.get(u, 0))

    q = deque([n for n, d in indeg.items() if d == 0])
    visited = 0
    while q:
        n = q.popleft()
        visited += 1
        for m in out.get(n, []):
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)

    total = len(indeg)
    if visited == total:
        return True, f"{total} nodes, {len(edges)} edges, topological sort OK"
    remaining = [n for n, d in indeg.items() if d > 0]
    return False, (
        f"cycle detected — {total - visited} nodes remain after toposort. "
        f"Nodes in cycle(s): {sorted(remaining)[:20]}"
    )


# ── Check 4 — schema compliance ────────────────────────────────────────────────


CRITERION_COMMON_FIELDS = {
    "criterion_id",
    "associated_lt_ids",
    "band",
    "band_label",
    "lt_type",
    "strand",
    "criterion_statement",
    "criterion_label",
    "source_kud_item_ids",
    "decomposition_rationale",
    "prerequisite_criterion_ids",
    "prerequisite_edges_detail",
    "schema_version",
}
CRITERION_T1_T2_EXTRA = {"competency_level_descriptors"}
CRITERION_T3_EXTRA = {
    "observation_indicators",
    "confusable_behaviours",
    "absence_indicators",
    "conversation_prompts",
}

LT_REQUIRED_FIELDS = {"lt_id", "lt_name", "competency", "knowledge_type", "bands"}


def check_schema_compliance(
    criteria: list[dict], lts: list[dict]
) -> tuple[bool, str]:
    non_compliant: list[tuple[str, list[str]]] = []
    compliant = 0
    for c in criteria:
        required = set(CRITERION_COMMON_FIELDS)
        lt_type = c.get("lt_type")
        if lt_type in ("Type 1", "Type 2"):
            required |= CRITERION_T1_T2_EXTRA
        elif lt_type == "Type 3":
            required |= CRITERION_T3_EXTRA
        missing = sorted(f for f in required if f not in c)
        if missing:
            non_compliant.append((c.get("criterion_id", "<missing id>"), missing))
        else:
            compliant += 1

    lt_non_compliant: list[tuple[str, list[str]]] = []
    lt_compliant = 0
    for lt in lts:
        missing = sorted(f for f in LT_REQUIRED_FIELDS if f not in lt)
        if missing:
            lt_non_compliant.append((lt.get("lt_id", "<missing id>"), missing))
        else:
            lt_compliant += 1

    ok = not non_compliant and not lt_non_compliant
    details = (
        f"criteria: {compliant} compliant, {len(non_compliant)} non-compliant; "
        f"LTs: {lt_compliant} compliant, {len(lt_non_compliant)} non-compliant"
    )
    if non_compliant:
        sample = "; ".join(
            f"{cid} missing {missing}" for cid, missing in non_compliant[:5]
        )
        details += f". First {min(5, len(non_compliant))} criteria: {sample}"
    if lt_non_compliant:
        sample = "; ".join(
            f"{lid} missing {missing}" for lid, missing in lt_non_compliant[:5]
        )
        details += f". First {min(5, len(lt_non_compliant))} LTs: {sample}"
    return ok, details


# ── Check 5 — field-derivation consistency ────────────────────────────────────


def check_field_derivation(criteria: list[dict]) -> tuple[bool, str]:
    consistent = 0
    inconsistent: list[tuple[str, str, str, str]] = []
    for c in criteria:
        band = c.get("band")
        label = c.get("band_label")
        if band is None or label is None:
            continue
        if band not in BAND_LABELS:
            inconsistent.append(
                (
                    c.get("criterion_id", "<missing id>"),
                    str(band),
                    "<unknown band letter>",
                    label,
                )
            )
            continue
        expected = BAND_LABELS[band]
        if label == expected:
            consistent += 1
        else:
            inconsistent.append(
                (c.get("criterion_id", "<missing id>"), band, expected, label)
            )
    details = f"{consistent} consistent, {len(inconsistent)} inconsistent"
    if inconsistent:
        sample = "; ".join(
            f"{cid} band={b} expected='{e}' actual='{a}'"
            for cid, b, e, a in inconsistent[:10]
        )
        details += f". First {min(10, len(inconsistent))}: {sample}"
    return len(inconsistent) == 0, details


# ── Check 6 — no inline BAND_LABELS dicts in scripts ─────────────────────────


def _scan_py_for_inline_bands(path: Path) -> list[str]:
    """Return human-readable offence strings found in a single .py file.

    Offences:
      (a) any top-level BAND_LABELS = {...} assignment
      (b) any dict literal with keys including at least one of A,B,C,D whose
          value is a string containing "Dragon"
    """
    offences: list[str] = []
    try:
        src = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return offences
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return offences

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign) -> None:
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "BAND_LABELS":
                    offences.append(
                        f"{path}:{node.lineno} top-level BAND_LABELS assignment"
                    )
            self.generic_visit(node)

        def visit_Dict(self, node: ast.Dict) -> None:
            band_keys_found: list[str] = []
            short_dragon_value = False
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value in ("A", "B", "C", "D"):
                    band_keys_found.append(k.value)
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        if "Dragon" in v.value and len(v.value) < 80:
                            short_dragon_value = True
            # Flag only dicts that look like inline band-letter→short-band-label
                # maps: all four of A,B,C,D present and at least one short
                # Dragon-labelled value.
            if set(band_keys_found) >= {"A", "B", "C", "D"} and short_dragon_value:
                offences.append(
                    f"{path}:{node.lineno} dict literal with band keys {sorted(set(band_keys_found))} "
                    f"and Dragon-name string value (inline band map)"
                )
            self.generic_visit(node)

    Visitor().visit(tree)
    return offences


def check_no_inline_band_labels() -> tuple[bool, str]:
    offences: list[str] = []
    for path in SCRIPTS_DIR.rglob("*.py"):
        if path.name == SELF_NAME:
            continue
        if "__pycache__" in path.parts:
            continue
        if path.name == Path(__file__).name:
            continue
        offences.extend(_scan_py_for_inline_bands(path))
    if not offences:
        return True, f"no inline BAND_LABELS found under {SCRIPTS_DIR}/"
    details = f"{len(offences)} offence(s): " + "; ".join(offences[:20])
    return False, details


# ── Check 7 — unified data internal band consistency ─────────────────────────


def _walk_band_labels(obj: object, path: str = "$") -> list[tuple[str, str]]:
    """Recursively yield (json_path, value) for every 'band_label' key in obj."""
    found: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}"
            if k == "band_label":
                found.append((new_path, v))
            else:
                found.extend(_walk_band_labels(v, new_path))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(_walk_band_labels(item, f"{path}[{i}]"))
    return found


def check_unified_data_bands(unified: dict) -> tuple[bool, str]:
    canonical = set(BAND_LABELS.values())
    all_labels = _walk_band_labels(unified)
    if not all_labels:
        return True, "no band_label fields present in unified data"
    compliant = [(p, v) for p, v in all_labels if v in canonical]
    non_compliant = [(p, v) for p, v in all_labels if v not in canonical]
    details = (
        f"{len(all_labels)} found, {len(compliant)} compliant, "
        f"{len(non_compliant)} non-compliant"
    )
    if non_compliant:
        sample = "; ".join(f"{p}='{v}'" for p, v in non_compliant[:10])
        details += f". First {min(10, len(non_compliant))}: {sample}"
    return len(non_compliant) == 0, details


# ── Check 8 — band-conventions.json self-check ────────────────────────────────

_BAND_CONVENTIONS_REL = (
    "docs/reference-corpus/real-wellbeing/band-conventions.json"
)
_REQUIRED_BAND_FIELDS = {"band_label", "letter", "dragons", "grades", "ages_approx"}
_EXPECTED_BAND_KEYS = {"A", "B", "C", "D", "E", "F"}


def check_band_conventions_self(repo_root: Path) -> tuple[bool, str]:
    conventions_path = repo_root / _BAND_CONVENTIONS_REL
    try:
        with conventions_path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        return False, f"cannot open band-conventions.json: {exc}"
    except json.JSONDecodeError as exc:
        return False, f"band-conventions.json malformed JSON: {exc}"

    issues: list[str] = []

    if "version" not in data or not isinstance(data.get("version"), str):
        issues.append("missing or non-string 'version' field")

    if "source_of_truth" not in data:
        issues.append("missing 'source_of_truth' field")
    else:
        sot_path = repo_root / data["source_of_truth"]
        if not sot_path.exists():
            issues.append(
                f"source_of_truth path does not exist on disk: {data['source_of_truth']}"
            )

    bands = data.get("bands")
    if not isinstance(bands, dict):
        issues.append("'bands' is missing or not an object")
    else:
        actual_keys = set(bands.keys())
        if actual_keys != _EXPECTED_BAND_KEYS:
            extra = sorted(actual_keys - _EXPECTED_BAND_KEYS)
            missing = sorted(_EXPECTED_BAND_KEYS - actual_keys)
            issues.append(
                f"'bands' key mismatch — extra: {extra}, missing: {missing}"
            )
        for letter, entry in bands.items():
            if not isinstance(entry, dict):
                issues.append(f"band '{letter}' is not an object")
                continue
            missing_fields = sorted(_REQUIRED_BAND_FIELDS - set(entry.keys()))
            if missing_fields:
                issues.append(f"band '{letter}' missing fields: {missing_fields}")

    if not issues:
        return True, (
            "band-conventions.json valid — version present, source_of_truth exists, "
            "6 bands (A–F), all required fields present"
        )
    return False, "; ".join(issues)


# ── Runner ────────────────────────────────────────────────────────────────────


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="REAL wellbeing preflight")
    parser.add_argument("--criterion-bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--unified-data", type=Path, default=DEFAULT_UNIFIED)
    parser.add_argument("--expected-lts", type=int, default=DEFAULT_EXPECTED_LTS)
    args = parser.parse_args(argv)

    bank = _load_json(args.criterion_bank)
    unified = _load_json(args.unified_data)
    criteria = bank.get("criteria", [])
    lts = unified.get("learning_targets", [])

    timestamp = datetime.now(timezone.utc).isoformat()
    print("=== PREFLIGHT REPORT ===")
    print(f"Timestamp: {timestamp}")
    print(f"Criterion bank: {args.criterion_bank} ({len(criteria)} entries)")
    print(f"Unified data: {args.unified_data} ({len(lts)} LTs)")
    print()

    c1_ok, c1 = check_band_label_compliance(criteria)
    c2_ok, c2 = check_lt_count(lts, args.expected_lts)
    c3_ok, c3 = check_dag_validity(lts)
    c4_ok, c4 = check_schema_compliance(criteria, lts)
    c5_ok, c5 = check_field_derivation(criteria)
    c6_ok, c6 = check_no_inline_band_labels()
    c7_ok, c7 = check_unified_data_bands(unified)
    c8_ok, c8 = check_band_conventions_self(REPO_ROOT)

    print(f"Check 1 (band_label compliance):       {_fmt_pass_fail(c1_ok)} — {c1}")
    print(f"Check 2 (LT count):                    {_fmt_pass_fail(c2_ok)} — {c2}")
    print(f"Check 3 (DAG validity):                {_fmt_pass_fail(c3_ok)} — {c3}")
    print(f"Check 4 (schema compliance):           {_fmt_pass_fail(c4_ok)} — {c4}")
    print(f"Check 5 (field-derivation):            {_fmt_pass_fail(c5_ok)} — {c5}")
    print(f"Check 6 (no inline BAND_LABELS):       {_fmt_pass_fail(c6_ok)} — {c6}")
    print(f"Check 7 (unified data bands):          {_fmt_pass_fail(c7_ok)} — {c7}")
    print(f"Check 8 (canonical self-check):        {_fmt_pass_fail(c8_ok)} — {c8}")
    print()
    overall_ok = all([c1_ok, c2_ok, c3_ok, c4_ok, c5_ok, c6_ok, c7_ok, c8_ok])
    print(f"OVERALL: {_fmt_pass_fail(overall_ok)}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
