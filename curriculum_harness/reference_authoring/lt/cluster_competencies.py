"""Competency clustering with 3x self-consistency and deterministic stability.

Groups KUD items into competencies using the source's organising
structure (e.g. Welsh CfW Statements of What Matters, Ontario Big
Ideas, Common Core cluster headings). The LT authoring skill says 2-3
LTs per competency; this is the stage that decides competency
boundaries before LT generation.

STABILITY CHECK — DETERMINISTIC POST-PROCESSING (per 4b-2 v2 revision)

Clusters are flagged ``cluster_unstable`` if ANY of the following is
true across the three runs:

1. The number of clusters differs across runs.
2. More than 20% of KUD items are placed in different clusters across
   runs (member-set drift, computed by aligning clusters across runs
   via Jaccard similarity on member ids).
3. A cluster's ``dominant_knowledge_type`` differs across runs.
4. A cluster exists in one run but not in another (measured by
   best-match alignment; an unmatched cluster fails this check).

≤1/3 parseable runs → overall ``cluster_unreliable``; no cluster set
produced. The stability check is applied mechanically on the three
run outputs — not as a subjective judgement by the classifier.
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from typing import Any

from curriculum_harness.reference_authoring.lt.cluster_prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from curriculum_harness.reference_authoring.types import (
    CompetencyCluster,
    CompetencyClusterSet,
    ReferenceKUD,
    SourceInventory,
)
from curriculum_harness.types import HAIKU_MODEL, extract_json_object
from curriculum_harness._anthropic import (
    AnthropicCallTimeout,
    get_async_client,
    haiku_stream_text,
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = HAIKU_MODEL
DEFAULT_TEMPERATURE = 0.3
DEFAULT_RUNS = 3
DEFAULT_MAX_TOKENS = 8192
# Drop source-blocks from prompt when KUD is large to keep the model
# from spending output budget on boilerplate JSON structure.
LARGE_KUD_THRESHOLD = 80

MEMBERSHIP_DRIFT_THRESHOLD = 0.20  # >20% drift → unstable
JACCARD_ALIGN_THRESHOLD = 0.30  # ≥0.30 Jaccard → clusters considered matched

_VALID_TYPES = {"Type 1", "Type 2", "Type 3"}


def _compact_kud_items(inventory: SourceInventory, kud: ReferenceKUD) -> list[dict[str, Any]]:
    block_line: dict[str, int] = {b.block_id: b.line_start for b in inventory.content_blocks}
    items: list[dict[str, Any]] = []
    for i in kud.items:
        items.append(
            {
                "item_id": i.item_id,
                "kud_column": i.kud_column,
                "knowledge_type": i.knowledge_type,
                "content_statement": i.content_statement,
                "source_block_id": i.source_block_id,
                "source_line_start": block_line.get(i.source_block_id, 0),
            }
        )
    items.sort(key=lambda x: (x["source_line_start"], x["item_id"]))
    return items


def _validate_parsed(
    obj: dict[str, Any] | None,
    *,
    expected_item_ids: set[str],
) -> list[dict[str, Any]] | None:
    """Return a list of validated cluster dicts or None if malformed.

    Enforces: every expected item id appears in exactly one cluster,
    cluster shape is correct, dominant_knowledge_type is valid.
    """
    if not isinstance(obj, dict):
        return None
    raw = obj.get("clusters")
    if not isinstance(raw, list) or not raw:
        return None
    seen_ids: set[str] = set()
    clean: list[dict[str, Any]] = []
    for c in raw:
        if not isinstance(c, dict):
            return None
        name = str(c.get("competency_name", "")).strip()
        definition = str(c.get("competency_definition", "")).strip()
        dkt = str(c.get("dominant_knowledge_type", "")).strip()
        if dkt not in _VALID_TYPES:
            return None
        kud_ids = c.get("kud_item_ids") or []
        if not isinstance(kud_ids, list) or not kud_ids:
            return None
        norm_ids: list[str] = []
        for x in kud_ids:
            s = str(x).strip()
            if not s:
                return None
            if s in seen_ids:
                # Duplicate assignment — drop the extra; do not reject the run.
                logger.info("clustering: duplicate item %s in run (skipped)", s)
                continue
            if s not in expected_item_ids:
                # Hallucinated id → structural failure, reject run.
                return None
            seen_ids.add(s)
            norm_ids.append(s)
        if not name or not definition:
            return None
        clean.append(
            {
                "competency_name": name,
                "competency_definition": definition,
                "dominant_knowledge_type": dkt,
                "kud_item_ids": norm_ids,
                "source_section_label": str(c.get("source_section_label", "")).strip(),
            }
        )
    # Every expected id must be covered.  For large KUDs the model
    # occasionally drops ≤3 items at the tail of the response.  Auto-assign
    # those stragglers to the cluster that already holds sibling items from
    # the same source block; if no sibling exists, assign to the last cluster.
    # Runs with >3 missing items are genuinely malformed and are rejected.
    missing_ids = expected_item_ids - seen_ids
    if missing_ids:
        if len(missing_ids) > 3:
            return None
        block_to_cluster_idx: dict[str, int] = {}
        for idx, c in enumerate(clean):
            for iid in c["kud_item_ids"]:
                block = iid.rsplit("_item_", 1)[0]
                block_to_cluster_idx.setdefault(block, idx)
        for missing_id in sorted(missing_ids):
            block = missing_id.rsplit("_item_", 1)[0]
            target = block_to_cluster_idx.get(block, len(clean) - 1)
            clean[target]["kud_item_ids"].append(missing_id)
            logger.info(
                "auto-assigned missing item %s to cluster %d (%s)",
                missing_id,
                target,
                clean[target]["competency_name"],
            )
    return clean


async def _one_clustering_run(
    *,
    client: Any,
    model: str,
    temperature: float,
    source_slug: str,
    kud_items: list[dict[str, Any]],
    source_blocks: list[dict[str, Any]] | None,
    run_idx: int,
    expected_ids: set[str],
) -> list[dict[str, Any]] | None:
    user_prompt = build_user_prompt(
        source_slug=source_slug,
        kud_items=kud_items,
        source_blocks=source_blocks,
    )
    label = f"refauth_cluster {source_slug} run{run_idx}"
    try:
        text = await haiku_stream_text(
            client,
            model=model,
            max_tokens=DEFAULT_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            user_blocks=[{"type": "text", "text": user_prompt}],
            label=label,
            temperature=temperature,
        )
    except AnthropicCallTimeout:
        logger.warning("clustering timeout: %s", label)
        return None
    except Exception:  # noqa: BLE001
        logger.exception("clustering error: %s", label)
        return None
    parsed = extract_json_object(text)
    validated = _validate_parsed(parsed, expected_item_ids=expected_ids)
    if validated is None:
        logger.warning("clustering parse/validation failed: %s", label)
    return validated


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _align_clusters(
    canonical: list[list[str]], other: list[list[str]]
) -> list[int | None]:
    """For each canonical cluster, return the index of the best-match
    cluster in ``other`` (by Jaccard on member sets), or None if no
    match clears JACCARD_ALIGN_THRESHOLD. Greedy: the best pair is
    fixed first, then the next, and so on.
    """
    canonical_sets = [set(c) for c in canonical]
    other_sets = [set(c) for c in other]
    used: set[int] = set()
    assignments: list[int | None] = [None] * len(canonical_sets)
    candidates: list[tuple[float, int, int]] = []
    for i, ca in enumerate(canonical_sets):
        for j, ob in enumerate(other_sets):
            candidates.append((_jaccard(ca, ob), i, j))
    candidates.sort(reverse=True)
    for score, i, j in candidates:
        if score < JACCARD_ALIGN_THRESHOLD:
            break
        if assignments[i] is not None:
            continue
        if j in used:
            continue
        assignments[i] = j
        used.add(j)
    return assignments


def _membership_drift(
    canonical: list[list[str]], other: list[list[str]]
) -> float:
    """Share of items whose cluster assignment differs between the two runs.

    Build a canonical id → cluster-index map, and an ``other`` id →
    aligned-cluster-index map; count mismatches. Items in ``other``
    that land in an unmatched cluster count as drifted.
    """
    align = _align_clusters(canonical, other)
    canonical_of: dict[str, int] = {}
    for idx, members in enumerate(canonical):
        for m in members:
            canonical_of[m] = idx
    # Build id → aligned-canonical-idx (or None) for ``other``.
    other_aligned_for: dict[str, int | None] = {}
    for j, members in enumerate(other):
        canonical_idx_for_j: int | None = None
        for i, assigned_j in enumerate(align):
            if assigned_j == j:
                canonical_idx_for_j = i
                break
        for m in members:
            other_aligned_for[m] = canonical_idx_for_j
    all_ids = set(canonical_of) | set(other_aligned_for)
    if not all_ids:
        return 0.0
    drift = 0
    for iid in all_ids:
        if canonical_of.get(iid) != other_aligned_for.get(iid):
            drift += 1
    return drift / len(all_ids)


def _check_stability(
    *,
    runs: list[list[dict[str, Any]]],
) -> tuple[list[str], list[int | None]]:
    """Apply the 4b-2 v2 operationalised cluster-stability check.

    Returns (diagnostics, alignment_runs_to_canonical). The canonical
    run is runs[0]; alignment_runs_to_canonical has one entry per run
    other than run 0 (in order), each a list mapping canonical cluster
    index → other-run cluster index (or None).
    """
    diagnostics: list[str] = []
    canonical = [c["kud_item_ids"] for c in runs[0]]
    canonical_dkt = [c["dominant_knowledge_type"] for c in runs[0]]

    # 1. Cluster count differs.
    counts = [len(r) for r in runs]
    if len(set(counts)) > 1:
        diagnostics.append(
            f"cluster_count_differs: counts across runs = {counts}"
        )

    alignments: list[list[int | None]] = []
    for idx, r in enumerate(runs[1:], start=2):
        other = [c["kud_item_ids"] for c in r]
        align = _align_clusters(canonical, other)
        alignments.append(align)
        # 4. Cluster-existence check — any canonical cluster has no match
        unmatched = [i for i, a in enumerate(align) if a is None]
        if unmatched:
            diagnostics.append(
                f"cluster_missing_in_run{idx}: canonical clusters "
                f"{unmatched} have no Jaccard>={JACCARD_ALIGN_THRESHOLD:.2f} match"
            )
        # 2. Membership drift
        drift = _membership_drift(canonical, other)
        if drift > MEMBERSHIP_DRIFT_THRESHOLD:
            diagnostics.append(
                f"membership_drift_run{idx}: {drift:.2%} of items reassigned "
                f"vs run1 (threshold {MEMBERSHIP_DRIFT_THRESHOLD:.0%})"
            )
        # 3. Dominant-type drift on matched clusters
        for can_i, other_j in enumerate(align):
            if other_j is None:
                continue
            if r[other_j]["dominant_knowledge_type"] != canonical_dkt[can_i]:
                diagnostics.append(
                    f"dominant_type_drift_run{idx}: canonical cluster {can_i} "
                    f"({canonical_dkt[can_i]}) → run{idx} cluster {other_j} "
                    f"({r[other_j]['dominant_knowledge_type']})"
                )
    return diagnostics, alignments


def _build_cluster_set(
    *,
    source_slug: str,
    canonical_run: list[dict[str, Any]],
    all_runs: list[list[dict[str, Any]]],
    alignments: list[list[int | None]],
    overall_stability_flag: str,
    overall_diagnostics: list[str],
    kud: ReferenceKUD,
    inventory: SourceInventory,
    model: str,
    temperature: float,
    runs_count: int,
) -> CompetencyClusterSet:
    block_line: dict[str, int] = {b.block_id: b.line_start for b in inventory.content_blocks}
    item_to_block: dict[str, str] = {i.item_id: i.source_block_id for i in kud.items}
    item_to_type: dict[str, str] = {i.item_id: i.knowledge_type for i in kud.items}

    clusters: list[CompetencyCluster] = []
    for canonical_idx, c in enumerate(canonical_run):
        member_ids = c["kud_item_ids"]
        block_ids = sorted({item_to_block[m] for m in member_ids if m in item_to_block})
        block_line_starts = [block_line.get(b, 0) for b in block_ids] or [0]
        kt_break: Counter[str] = Counter(item_to_type[m] for m in member_ids if m in item_to_type)
        # Gather the per-run signature so the cluster's stability story is visible.
        per_run_sigs: list[dict[str, Any]] = []
        per_run_sigs.append(
            {
                "run": 1,
                "competency_name": c["competency_name"],
                "dominant_knowledge_type": c["dominant_knowledge_type"],
                "kud_item_ids": list(member_ids),
            }
        )
        # Map each other-run to its aligned cluster (if any).
        for run_offset, align in enumerate(alignments, start=2):
            other_idx = align[canonical_idx]
            if other_idx is None:
                per_run_sigs.append(
                    {
                        "run": run_offset,
                        "competency_name": None,
                        "dominant_knowledge_type": None,
                        "kud_item_ids": [],
                        "note": "no_matched_cluster",
                    }
                )
            else:
                other = all_runs[run_offset - 1][other_idx]
                per_run_sigs.append(
                    {
                        "run": run_offset,
                        "competency_name": other["competency_name"],
                        "dominant_knowledge_type": other["dominant_knowledge_type"],
                        "kud_item_ids": list(other["kud_item_ids"]),
                    }
                )

        # Per-cluster stability diagnostics: canonical dkt drift or
        # unmatched in any run.
        per_cluster_diag: list[str] = []
        for sig in per_run_sigs[1:]:
            if sig.get("note") == "no_matched_cluster":
                per_cluster_diag.append(
                    f"unmatched_in_run{sig['run']}"
                )
            elif sig["dominant_knowledge_type"] != c["dominant_knowledge_type"]:
                per_cluster_diag.append(
                    f"dominant_type_drift_run{sig['run']}: "
                    f"{c['dominant_knowledge_type']}→{sig['dominant_knowledge_type']}"
                )
        stability_flag = "stable" if not per_cluster_diag else "cluster_unstable"

        clusters.append(
            CompetencyCluster(
                cluster_id=f"cluster_{canonical_idx+1:02d}",
                competency_name=c["competency_name"],
                competency_definition=c["competency_definition"],
                kud_item_ids=list(member_ids),
                source_block_ids=block_ids,
                source_position_start=min(block_line_starts),
                source_position_end=max(block_line_starts),
                dominant_knowledge_type=c["dominant_knowledge_type"],
                knowledge_type_breakdown=dict(kt_break),
                stability_flag=stability_flag,
                per_run_signatures=per_run_sigs,
                stability_diagnostics=per_cluster_diag,
            )
        )

    cluster_set = CompetencyClusterSet(
        source_slug=source_slug,
        clusters=clusters,
        model=model,
        temperature=temperature,
        runs=runs_count,
        unassigned_kud_item_ids=[],  # validator enforces no leftovers
        overall_stability_flag=overall_stability_flag,
        overall_stability_diagnostics=list(overall_diagnostics),
    )
    return cluster_set


async def cluster_competencies(
    inventory: SourceInventory,
    kud: ReferenceKUD,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    runs: int = DEFAULT_RUNS,
) -> CompetencyClusterSet:
    """Cluster a KUD into competencies with 3x self-consistency."""
    client = get_async_client()
    compact = _compact_kud_items(inventory, kud)
    expected_ids = {it["item_id"] for it in compact}
    source_slug = inventory.source_slug
    # Skip source_blocks for large KUDs — the output must enumerate every
    # item ID and the 8192-token budget is needed for that, not structure prose.
    if len(compact) <= LARGE_KUD_THRESHOLD:
        source_blocks: list[dict[str, Any]] | None = [b.to_dict() for b in inventory.content_blocks]
    else:
        source_blocks = None

    coros = [
        _one_clustering_run(
            client=client,
            model=model,
            temperature=temperature,
            source_slug=source_slug,
            kud_items=compact,
            source_blocks=source_blocks,
            run_idx=i + 1,
            expected_ids=expected_ids,
        )
        for i in range(runs)
    ]
    results = await asyncio.gather(*coros)
    valid: list[list[dict[str, Any]]] = [r for r in results if r is not None]

    if len(valid) < 2:
        return CompetencyClusterSet(
            source_slug=source_slug,
            model=model,
            temperature=temperature,
            runs=runs,
            overall_stability_flag="cluster_unreliable",
            overall_stability_diagnostics=[
                f"only {len(valid)}/{runs} clustering runs produced valid output"
            ],
        )

    diagnostics, alignments = _check_stability(runs=valid)
    overall_flag = "stable" if not diagnostics else "cluster_unstable"
    return _build_cluster_set(
        source_slug=source_slug,
        canonical_run=valid[0],
        all_runs=valid,
        alignments=alignments,
        overall_stability_flag=overall_flag,
        overall_diagnostics=diagnostics,
        kud=kud,
        inventory=inventory,
        model=model,
        temperature=temperature,
        runs_count=runs,
    )


def cluster_competencies_sync(
    inventory: SourceInventory,
    kud: ReferenceKUD,
    **kwargs: Any,
) -> CompetencyClusterSet:
    return asyncio.run(cluster_competencies(inventory, kud, **kwargs))
