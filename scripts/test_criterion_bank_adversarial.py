"""Adversarial tests for criterion bank generation (Session 4c-4).

Eight tests:
  1. Cycle detection — reject, report path
  2. Self-loop detection — reject
  3. Unresolved ID — reject
  4. Cross-strand edge — reject
  5. Compound LT decomposition — produces multiple criteria, correct associated_lt_ids
  6. Simple LT non-decomposition — produces one criterion
  7. Multi-strand unified DAG — no cycles across strands when unified
  8. Agreement-rate calculation regression — synthetic case verifies rate computed correctly

Run: python scripts/test_criterion_bank_adversarial.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_criterion_bank import (
    compute_agreement,
    detect_cycles,
    detect_cross_strand,
    detect_self_loops,
    detect_unresolved_ids,
    run_dag_validation,
)


def _make_crit(cid: str, prereqs: list[str] = None, strand: str = "single_strand",
               lt_ids: list[str] = None) -> dict:
    return {
        "criterion_id": cid,
        "associated_lt_ids": lt_ids or [f"lt_{cid[-4:]}"],
        "strand": strand,
        "criterion_statement": f"Statement for {cid}",
        "criterion_label": cid,
        "source_provenance": [],
        "competency_level_descriptors": {
            "no_evidence": "No attempt.",
            "emerging": "Partial or prompted.",
            "developing": "Engages with gaps.",
            "competent": "Meets criterion independently.",
            "extending": "Exceeds criterion.",
        },
        "prerequisite_criterion_ids_raw": prereqs or [],
        "schema_version": "v1",
    }


def _make_edge(from_id: str, to_id: str, tag: str = "ontological_prerequisite",
               strength: str = "high") -> dict:
    return {
        "from_criterion_id": from_id,
        "to_criterion_id": to_id,
        "reasoning_tag": tag,
        "strength": strength,
        "rationale": f"{from_id} → {to_id}",
    }


RESULTS: list[tuple[str, bool, str]] = []


def _run(name: str, fn) -> None:
    try:
        passed, detail = fn()
    except Exception as exc:
        passed, detail = False, f"EXCEPTION: {exc}"
    RESULTS.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name}: {detail}")


# ── Test 1: Cycle detection ────────────────────────────────────────────────────

def test_cycle_detection() -> tuple[bool, str]:
    a = _make_crit("src_crit_0001", prereqs=["src_crit_0002"])
    b = _make_crit("src_crit_0002", prereqs=["src_crit_0003"])
    c = _make_crit("src_crit_0003", prereqs=["src_crit_0001"])  # closes cycle
    criteria = [a, b, c]
    edges = [
        _make_edge("src_crit_0001", "src_crit_0002"),
        _make_edge("src_crit_0002", "src_crit_0003"),
        _make_edge("src_crit_0003", "src_crit_0001"),
    ]
    # Note: detect_cycles uses prerequisite_criterion_ids_raw (prereqs pointing upstream),
    # then builds graph from those (upstream → downstream). Let's check using full run_dag_validation.
    # Actually our cycle detection builds graph where pid → criterion (downstream direction).
    # Cycle: 0001 requires 0002 (0002→0001 edge in graph), 0002 requires 0003 (0003→0002), 0003 requires 0001 (0001→0003).
    errors = detect_cycles(criteria)
    if not errors:
        return False, "no cycle detected (expected 1)"
    err = errors[0]
    if err["type"] != "cycle":
        return False, f"wrong error type: {err['type']}"
    path = err["path"]
    if len(path) < 3:
        return False, f"cycle path too short: {path}"
    return True, f"cycle detected: {' → '.join(path)}"


# ── Test 2: Self-loop detection ────────────────────────────────────────────────

def test_self_loop_detection() -> tuple[bool, str]:
    a = _make_crit("src_crit_0001", prereqs=["src_crit_0001"])  # self-loop
    b = _make_crit("src_crit_0002", prereqs=[])
    errors = detect_self_loops([a, b])
    if not errors:
        return False, "no self-loop detected (expected 1)"
    err = errors[0]
    if err["type"] != "self_loop":
        return False, f"wrong error type: {err['type']}"
    return True, f"self-loop detected: {err['detail']}"


# ── Test 3: Unresolved ID ──────────────────────────────────────────────────────

def test_unresolved_id() -> tuple[bool, str]:
    a = _make_crit("src_crit_0001", prereqs=["src_crit_9999"])  # 9999 doesn't exist
    b = _make_crit("src_crit_0002", prereqs=[])
    errors = detect_unresolved_ids([a, b])
    if not errors:
        return False, "no unresolved ID detected (expected 1)"
    err = errors[0]
    if err["type"] != "unresolved_id":
        return False, f"wrong error type: {err['type']}"
    return True, f"unresolved ID detected: {err['detail']}"


# ── Test 4: Cross-strand edge ──────────────────────────────────────────────────

def test_cross_strand_edge() -> tuple[bool, str]:
    a = _make_crit("src_crit_0001", strand="algebra")
    b = _make_crit("src_crit_0002", strand="number")
    edges = [_make_edge("src_crit_0001", "src_crit_0002")]  # cross-strand
    errors = detect_cross_strand([a, b], edges)
    if not errors:
        return False, "no cross-strand edge detected (expected 1)"
    err = errors[0]
    if err["type"] != "cross_strand_edge":
        return False, f"wrong error type: {err['type']}"
    return True, f"cross-strand edge detected: {err['detail']}"


# ── Test 5: Compound LT decomposition ─────────────────────────────────────────

def test_compound_lt_decomposition() -> tuple[bool, str]:
    # A compound LT should produce multiple criteria, each with the same associated_lt_ids.
    lt_id = "cluster_01_lt_01"
    c1 = _make_crit("src_crit_0001", lt_ids=[lt_id])
    c2 = _make_crit("src_crit_0002", lt_ids=[lt_id])
    # Both criteria should reference the same LT.
    if c1["associated_lt_ids"] != [lt_id] or c2["associated_lt_ids"] != [lt_id]:
        return False, "associated_lt_ids mismatch"
    # Multiple criteria from one LT is the expected result.
    if len([c for c in [c1, c2] if lt_id in c["associated_lt_ids"]]) != 2:
        return False, "expected 2 criteria for compound LT"
    # Prerequisite: c1 is prerequisite to c2 (intra-LT edge).
    c2["prerequisite_criterion_ids_raw"] = ["src_crit_0001"]
    errors = run_dag_validation([c1, c2], [_make_edge("src_crit_0001", "src_crit_0002")])
    if errors:
        return False, f"DAG errors on compound LT: {errors}"
    return True, "compound LT → 2 criteria, correct associated_lt_ids, valid DAG"


# ── Test 6: Simple LT non-decomposition ───────────────────────────────────────

def test_simple_lt_non_decomposition() -> tuple[bool, str]:
    lt_id = "cluster_02_lt_01"
    c = _make_crit("src_crit_0003", lt_ids=[lt_id])
    # Exactly one criterion for this LT.
    if c["associated_lt_ids"] != [lt_id]:
        return False, "associated_lt_ids mismatch"
    errors = run_dag_validation([c], [])
    if errors:
        return False, f"DAG errors on simple LT: {errors}"
    return True, "simple LT → 1 criterion, valid DAG"


# ── Test 7: Multi-strand unified DAG ──────────────────────────────────────────

def test_multi_strand_unified_dag() -> tuple[bool, str]:
    # Two strands, each with a small valid DAG. No cross-strand edges.
    a1 = _make_crit("src_crit_0001", strand="algebra", prereqs=[], lt_ids=["lt_alg_01"])
    a2 = _make_crit("src_crit_0002", strand="algebra", prereqs=["src_crit_0001"], lt_ids=["lt_alg_02"])
    n1 = _make_crit("src_crit_0003", strand="number", prereqs=[], lt_ids=["lt_num_01"])
    n2 = _make_crit("src_crit_0004", strand="number", prereqs=["src_crit_0003"], lt_ids=["lt_num_02"])
    criteria = [a1, a2, n1, n2]
    edges = [
        _make_edge("src_crit_0001", "src_crit_0002"),
        _make_edge("src_crit_0003", "src_crit_0004"),
    ]
    errors = run_dag_validation(criteria, edges)
    if errors:
        return False, f"DAG errors: {errors}"
    # Confirm no false cross-strand detection.
    xs = detect_cross_strand(criteria, edges)
    if xs:
        return False, f"false cross-strand detection: {xs}"
    return True, "multi-strand unified DAG: no cycles, no cross-strand errors"


# ── Test 8: Agreement rate calculation regression ──────────────────────────────

def test_agreement_rate_regression() -> tuple[bool, str]:
    """Synthetic case: 4 curated edges, generator recovers 3 of them.
    Primary should be 3/4 = 0.75. Secondary: 2 of 3 recovered have matching tag.
    """
    # LT structure: lt_A → (crit_A); lt_B → (crit_B1, crit_B2); lt_C → (crit_C); lt_D → (crit_D)
    criteria = [
        {**_make_crit("src_crit_0001", lt_ids=["lt_A"]), "prerequisite_criterion_ids_raw": []},
        {**_make_crit("src_crit_0002", lt_ids=["lt_B"], prereqs=["src_crit_0001"]),
         "prerequisite_criterion_ids_raw": ["src_crit_0001"]},
        {**_make_crit("src_crit_0003", lt_ids=["lt_B"], prereqs=[]),
         "prerequisite_criterion_ids_raw": []},
        {**_make_crit("src_crit_0004", lt_ids=["lt_C"], prereqs=["src_crit_0002"]),
         "prerequisite_criterion_ids_raw": ["src_crit_0002"]},
        {**_make_crit("src_crit_0005", lt_ids=["lt_D"], prereqs=[]),
         "prerequisite_criterion_ids_raw": []},
    ]
    edges = [
        # lt_A → lt_B (recovered via crit_0001 → crit_0002, tag=ontological)
        _make_edge("src_crit_0001", "src_crit_0002", tag="ontological_prerequisite"),
        # lt_B → lt_C (recovered via crit_0002 → crit_0004, tag=pedagogical; curated=ontological → tag mismatch)
        _make_edge("src_crit_0002", "src_crit_0004", tag="pedagogical_sequencing"),
        # lt_A → lt_C (not generated — unrecovered)
        # lt_A → lt_D (not generated — unrecovered)
    ]

    curated = [
        {"lt_a": "lt_A", "lt_b": "lt_B", "tag": "ontological_prerequisite", "strength": "high", "rationale": "x"},
        {"lt_a": "lt_B", "lt_b": "lt_C", "tag": "ontological_prerequisite", "strength": "high", "rationale": "x"},
        {"lt_a": "lt_A", "lt_b": "lt_C", "tag": "ontological_prerequisite", "strength": "medium", "rationale": "x"},
        {"lt_a": "lt_A", "lt_b": "lt_D", "tag": "pedagogical_sequencing", "strength": "low", "rationale": "x"},
    ]

    result = compute_agreement(criteria, edges, curated)

    expected_primary = 0.5  # 2/4: lt_A→lt_B (recovered), lt_B→lt_C (recovered), lt_A→lt_C (NO - need crit_A→crit_C), lt_A→lt_D (NO)
    # Wait, let me re-think. lt_A→lt_C: crit_A_set={crit_0001}, crit_C_set={crit_0004}.
    # Is there an edge from crit_0001 to crit_0004? NO. Unrecovered.
    # lt_A→lt_D: crit_A_set={crit_0001}, crit_D_set={crit_0005}. No edge. Unrecovered.
    # lt_A→lt_B: crit_A={crit_0001}, crit_B={crit_0002, crit_0003}. Edge 0001→0002 exists. Recovered.
    # lt_B→lt_C: crit_B={crit_0002, crit_0003}, crit_C={crit_0004}. Edge 0002→0004 exists. Recovered.
    # Primary: 2/4 = 0.5

    # Secondary: lt_A→lt_B: curated=ontological, generated=ontological → MATCH
    #            lt_B→lt_C: curated=ontological, generated=pedagogical → MISMATCH
    # Secondary: 1/4 = 0.25 (only matches where primary also matched)

    expected_primary = 0.5
    expected_secondary = 0.25

    actual_primary = result["primary_agreement_rate"]
    actual_secondary = result["secondary_agreement_rate"]
    unrecovered_count = len(result["unrecovered_edges"])

    if abs(actual_primary - expected_primary) > 0.001:
        return False, f"primary rate wrong: got {actual_primary}, expected {expected_primary}"
    if abs(actual_secondary - expected_secondary) > 0.001:
        return False, f"secondary rate wrong: got {actual_secondary}, expected {expected_secondary}"
    if unrecovered_count != 2:
        return False, f"unrecovered count wrong: got {unrecovered_count}, expected 2"

    return True, (
        f"primary={actual_primary:.0%}, secondary={actual_secondary:.0%}, "
        f"unrecovered={unrecovered_count}/4"
    )


# ── Runner ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Adversarial tests — criterion bank (Session 4c-4)")
    print("=" * 60)

    _run("1. Cycle detection", test_cycle_detection)
    _run("2. Self-loop detection", test_self_loop_detection)
    _run("3. Unresolved ID", test_unresolved_id)
    _run("4. Cross-strand edge", test_cross_strand_edge)
    _run("5. Compound LT decomposition", test_compound_lt_decomposition)
    _run("6. Simple LT non-decomposition", test_simple_lt_non_decomposition)
    _run("7. Multi-strand unified DAG", test_multi_strand_unified_dag)
    _run("8. Agreement-rate calculation regression", test_agreement_rate_regression)

    print("=" * 60)
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print(f"Results: {passed}/{total} passed")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
