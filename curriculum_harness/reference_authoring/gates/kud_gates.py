"""KUD quality gates for the reference-authoring pipeline.

Gates (per session 4b-1 prompt and arc plan v3, revised in 4b-2):

1. source_coverage — every non-heading inventory block not halted for
   severe underspecification maps to ≥1 KUD item.
2. traceability — every KUD item's source_block_id refers to a real
   inventory block.
3. artefact_count_ratio — KUD item count / non-heading inventory block
   count lands in a domain-aware target band:
     - hierarchical: [0.8, 1.5] (vision v4.1 default)
     - horizontal:   [0.8, 1.5] (vision v4.1 default)
     - dispositional: [0.8, 2.2] (4b-2 PROVISIONAL revision)
4. type3_distribution — for dispositional-domain sources, ≥20% of KUD
   items are Type 3. Informational only.
5. no_compound_unsplit — every KUD item's (kud_column, knowledge_type)
   pair is consistent (single type per item).

Halting gates (source_coverage, traceability, artefact_count_ratio,
no_compound_unsplit) surface specific diagnostics and halt output.
type3_distribution emits an informational flag.

Dispositional-ceiling provisionality (4b-2).
The dispositional ceiling was raised from 1.5 to 2.2 on the basis of
one real-corpus extraction (Welsh CfW Health and Well-being, session
4b-1) which landed at 1.65. Panel review confirmed the compound-split
output was correct: prose dispositional sources legitimately bundle
multiple capabilities per bullet, and the LT authoring skill requires
splitting by knowledge type regardless of source-bullet count. 2.2
provides headroom above Welsh CfW without being unbounded. This
ceiling is PROVISIONAL: the next dispositional source run through the
pipeline (e.g. Scottish CfE Health and Wellbeing) may land at a ratio
that challenges it. The ceiling is reviewed and potentially re-revised
against each new dispositional source until a stable pattern emerges
across the domain.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from curriculum_harness.reference_authoring.types import (
    GateResult,
    QualityReport,
    ReferenceKUD,
    SourceInventory,
)

SOURCE_DOMAINS = ("hierarchical", "horizontal", "dispositional")

# Domain-aware ratio bands. Hierarchical and horizontal inherit vision v4.1
# defaults; dispositional is the PROVISIONAL 4b-2 revision documented above.
RATIO_BANDS: dict[str, tuple[float, float]] = {
    "hierarchical": (0.8, 1.5),
    "horizontal": (0.8, 1.5),
    "dispositional": (0.8, 2.2),
}
# Legacy aliases — kept so callers that still reference the old constants
# continue to resolve. New code should use RATIO_BANDS[domain].
RATIO_MIN = 0.8
RATIO_MAX = 1.5
TYPE3_MIN_PCT = 0.20

_TYPE_TO_ROUTE = {
    "Type 1": "rubric_with_clear_criteria",
    "Type 2": "reasoning_quality_rubric",
    "Type 3": "multi_informant_observation",
}


def _non_heading_block_ids(inventory: SourceInventory) -> list[str]:
    return [b.block_id for b in inventory.content_blocks if b.block_type != "heading"]


def _severely_halted_ids(kud: ReferenceKUD) -> set[str]:
    return {h.block_id for h in kud.halted_blocks if h.halt_reason == "severe_underspecification"}


def _unreliable_halted_ids(kud: ReferenceKUD) -> set[str]:
    return {h.block_id for h in kud.halted_blocks if h.halt_reason == "classification_unreliable"}


def _gate_source_coverage(
    inventory: SourceInventory, kud: ReferenceKUD
) -> GateResult:
    non_heading = set(_non_heading_block_ids(inventory))
    severely = _severely_halted_ids(kud)
    unreliable = _unreliable_halted_ids(kud)
    # Blocks that MUST have produced items.
    required = non_heading - severely - unreliable
    covered = {i.source_block_id for i in kud.items}
    missing = sorted(required - covered)
    passed = len(missing) == 0
    return GateResult(
        name="source_coverage",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "all non-severe, non-unreliable inventory blocks produced ≥1 KUD item"
            if passed
            else f"{len(missing)} inventory blocks produced no KUD items despite passing self-consistency: {missing}"
        ),
        details={
            "required_blocks": sorted(required),
            "covered_blocks": sorted(covered & required),
            "missing_blocks": missing,
            "severely_halted_blocks": sorted(severely),
            "unreliable_halted_blocks": sorted(unreliable),
        },
    )


def _gate_traceability(
    inventory: SourceInventory, kud: ReferenceKUD
) -> GateResult:
    valid_block_ids = {b.block_id for b in inventory.content_blocks}
    untraceable = [i for i in kud.items if i.source_block_id not in valid_block_ids]
    passed = len(untraceable) == 0
    return GateResult(
        name="traceability",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "every KUD item has a valid source_block_id"
            if passed
            else f"{len(untraceable)} KUD items have source_block_id values not present in the inventory"
        ),
        details={
            "total_items": len(kud.items),
            "untraceable_count": len(untraceable),
            "untraceable_items": [
                {
                    "item_id": i.item_id,
                    "declared_source_block_id": i.source_block_id,
                }
                for i in untraceable
            ],
        },
    )


def _gate_artefact_count_ratio(
    inventory: SourceInventory,
    kud: ReferenceKUD,
    *,
    source_domain: str,
) -> GateResult:
    if source_domain not in RATIO_BANDS:
        raise ValueError(
            f"source_domain must be one of {SOURCE_DOMAINS}, got {source_domain!r}"
        )
    r_min, r_max = RATIO_BANDS[source_domain]
    non_heading = _non_heading_block_ids(inventory)
    severely = _severely_halted_ids(kud)
    expected_blocks = [b for b in non_heading if b not in severely]
    denom = len(expected_blocks)
    numer = len(kud.items)
    ratio = (numer / denom) if denom else 0.0
    passed = denom > 0 and r_min <= ratio <= r_max
    provisional_note = (
        " (dispositional ceiling is PROVISIONAL per 4b-2; next dispositional "
        "source may re-trigger review)"
        if source_domain == "dispositional"
        else ""
    )
    base = (
        f"KUD items / expected-yield blocks = {numer}/{denom} = {ratio:.3f} "
        f"(denominator excludes {len(severely)} severely-underspecified blocks)"
    )
    return GateResult(
        name="artefact_count_ratio",
        passed=passed,
        halting=not passed,
        diagnostic=(
            f"{base} within {source_domain}-domain target [{r_min}, {r_max}]{provisional_note}"
            if passed
            else f"{base} outside {source_domain}-domain target band [{r_min}, {r_max}]{provisional_note}"
        ),
        details={
            "kud_item_count": numer,
            "non_heading_block_count": len(non_heading),
            "severely_halted_block_count": len(severely),
            "expected_yield_block_count": denom,
            "ratio": round(ratio, 4),
            "source_domain": source_domain,
            "target_min": r_min,
            "target_max": r_max,
            "dispositional_provisional": source_domain == "dispositional",
        },
    )


def _gate_type3_distribution(
    kud: ReferenceKUD,
    *,
    source_is_dispositional: bool,
) -> GateResult:
    total = len(kud.items)
    type3 = sum(1 for i in kud.items if i.knowledge_type == "Type 3")
    pct = (type3 / total) if total else 0.0
    if not source_is_dispositional:
        # Not applicable; emit a pass with a note.
        return GateResult(
            name="type3_distribution",
            passed=True,
            halting=False,
            diagnostic=(
                "type3_distribution gate skipped — source is not marked as "
                "dispositional-domain"
            ),
            details={"type3_count": type3, "total_items": total, "pct": round(pct, 4)},
        )
    meets_min = pct >= TYPE3_MIN_PCT
    return GateResult(
        name="type3_distribution",
        passed=meets_min,
        halting=False,
        diagnostic=(
            f"Type 3 items = {type3}/{total} = {pct:.1%} (≥{TYPE3_MIN_PCT:.0%} expected for dispositional domain)"
            if meets_min
            else f"dispositional_content_underrepresented: Type 3 items = {type3}/{total} = {pct:.1%} "
            f"< expected ≥{TYPE3_MIN_PCT:.0%} for dispositional domain (informational only)"
        ),
        details={
            "type3_count": type3,
            "total_items": total,
            "pct": round(pct, 4),
            "expected_min_pct": TYPE3_MIN_PCT,
            "flag": "dispositional_content_underrepresented" if not meets_min else None,
        },
    )


def _gate_no_compound_unsplit(kud: ReferenceKUD) -> GateResult:
    offenders: list[dict[str, str]] = []
    for i in kud.items:
        # Enforce type↔column and type→route consistency.
        route_ok = _TYPE_TO_ROUTE.get(i.knowledge_type) == i.assessment_route
        col_ok = (
            (i.knowledge_type == "Type 3" and i.kud_column == "do_disposition")
            or (i.knowledge_type != "Type 3" and i.kud_column != "do_disposition")
        )
        if not (route_ok and col_ok):
            offenders.append(
                {
                    "item_id": i.item_id,
                    "kud_column": i.kud_column,
                    "knowledge_type": i.knowledge_type,
                    "assessment_route": i.assessment_route,
                }
            )
    passed = len(offenders) == 0
    return GateResult(
        name="no_compound_unsplit",
        passed=passed,
        halting=not passed,
        diagnostic=(
            "every KUD item carries a single knowledge type with consistent column and route"
            if passed
            else f"{len(offenders)} KUD items have inconsistent (kud_column, knowledge_type, assessment_route) triples"
        ),
        details={"offenders": offenders},
    )


def _stability_summary(kud: ReferenceKUD) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for i in kud.items:
        counts[i.stability_flag] += 1
    return dict(counts)


def _underspec_summary(kud: ReferenceKUD) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for i in kud.items:
        key = i.underspecification_flag or "null"
        counts[key] += 1
    return dict(counts)


def _knowledge_type_summary(kud: ReferenceKUD) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for i in kud.items:
        counts[i.knowledge_type] += 1
    return dict(counts)


def _kud_column_summary(kud: ReferenceKUD) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for i in kud.items:
        counts[i.kud_column] += 1
    return dict(counts)


def run_kud_gates(
    inventory: SourceInventory,
    kud: ReferenceKUD,
    *,
    source_is_dispositional: bool,
    source_domain: str | None = None,
) -> QualityReport:
    """Run the full KUD gate suite and return a QualityReport.

    ``source_domain`` selects the artefact-count-ratio band: one of
    ``"hierarchical"``, ``"horizontal"``, ``"dispositional"``. If not
    provided, it is inferred from ``source_is_dispositional`` — True →
    ``"dispositional"``, False → ``"hierarchical"`` (the safe default).
    Callers with a horizontal source must pass ``source_domain`` explicitly.
    """
    if source_domain is None:
        source_domain = "dispositional" if source_is_dispositional else "hierarchical"
    if source_domain not in RATIO_BANDS:
        raise ValueError(
            f"source_domain must be one of {SOURCE_DOMAINS}, got {source_domain!r}"
        )
    gates: list[GateResult] = [
        _gate_source_coverage(inventory, kud),
        _gate_traceability(inventory, kud),
        _gate_artefact_count_ratio(inventory, kud, source_domain=source_domain),
        _gate_type3_distribution(kud, source_is_dispositional=source_is_dispositional),
        _gate_no_compound_unsplit(kud),
    ]
    halted_by: str | None = None
    for g in gates:
        if g.halting and not g.passed:
            halted_by = g.name
            break
    summary = {
        "source_domain": source_domain,
        "inventory_blocks_total": len(inventory.content_blocks),
        "inventory_non_heading_blocks": len(_non_heading_block_ids(inventory)),
        "kud_items_total": len(kud.items),
        "halted_blocks_total": len(kud.halted_blocks),
        "halted_severe": len(_severely_halted_ids(kud)),
        "halted_unreliable": len(_unreliable_halted_ids(kud)),
        "knowledge_type_distribution": _knowledge_type_summary(kud),
        "kud_column_distribution": _kud_column_summary(kud),
        "stability_distribution": _stability_summary(kud),
        "underspecification_distribution": _underspec_summary(kud),
    }
    return QualityReport(
        source_slug=inventory.source_slug,
        gate_results=gates,
        halted_by=halted_by,
        summary=summary,
    )


def quality_report_to_markdown(report: QualityReport) -> str:
    """Render a QualityReport as a human-readable markdown document."""
    lines: list[str] = []
    lines.append(f"# KUD quality report — {report.source_slug}")
    lines.append("")
    status = "HALTED" if report.halted_by else "PASSED"
    lines.append(f"**Overall:** {status}")
    if report.halted_by:
        lines.append(f"**Halted by gate:** `{report.halted_by}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for k, v in report.summary.items():
        if isinstance(v, dict):
            pretty = ", ".join(f"{kk}={vv}" for kk, vv in sorted(v.items()))
            lines.append(f"- **{k}:** {pretty or '(empty)'}")
        else:
            lines.append(f"- **{k}:** {v}")
    lines.append("")
    lines.append("## Gate results")
    lines.append("")
    for g in report.gate_results:
        verdict = "PASS" if g.passed else ("FAIL (halts)" if g.halting else "FLAG")
        lines.append(f"### `{g.name}` — {verdict}")
        lines.append("")
        lines.append(g.diagnostic)
        lines.append("")
    return "\n".join(lines) + "\n"
