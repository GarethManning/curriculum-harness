"""LT generator: 2-3 LTs per competency with 3x self-consistency.

Per the LT authoring skill: 2-3 LTs per competency, single-construct
rule, knowledge-type split when a competency mixes Type 2/1 with Type
3. This stage produces LT structure only — band statements for Type
1/2 and observation indicator sets for Type 3 are generated downstream
(generate_band_statements.py, generate_observation_indicators.py).

SELF-CONSISTENCY

Each competency's LT set is generated 3x at temperature 0.3. Stability
is judged on:

- 3/3: identical LT count AND identical knowledge-type multiset across
  runs → ``stable``. Run-1's LT set is retained.
- 2/3: majority signature (LT count + KT multiset) retained, flagged
  ``lt_set_unstable``.
- ≤1/3 valid parses or no 2/3 agreement → halted, flagged
  ``lt_set_unreliable``; no LTs produced for this competency.
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from typing import Any

from curriculum_harness.reference_authoring.lt.lt_prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from curriculum_harness.reference_authoring.types import (
    CompetencyCluster,
    CompetencyClusterSet,
    LearningTarget,
    LearningTargetSet,
    ReferenceKUD,
)
from curriculum_harness.types import SONNET_MODEL, extract_json_object
from curriculum_harness._anthropic import (
    AnthropicCallTimeout,
    get_async_client,
    haiku_stream_text,
)

logger = logging.getLogger(__name__)

DEFAULT_MODEL = SONNET_MODEL
DEFAULT_TEMPERATURE = 0.3
DEFAULT_RUNS = 3
DEFAULT_MAX_TOKENS = 3072
CLUSTER_CONCURRENCY = 4

_VALID_TYPES = {"Type 1", "Type 2", "Type 3"}
_VALID_ROUTES = {
    "rubric_with_clear_criteria",
    "reasoning_quality_rubric",
    "multi_informant_observation",
}
_TYPE_TO_ROUTE = {
    "Type 1": "rubric_with_clear_criteria",
    "Type 2": "reasoning_quality_rubric",
    "Type 3": "multi_informant_observation",
}


def _items_for_cluster(
    cluster: CompetencyCluster, kud: ReferenceKUD
) -> list[dict[str, Any]]:
    by_id = {i.item_id: i for i in kud.items}
    out: list[dict[str, Any]] = []
    for iid in cluster.kud_item_ids:
        it = by_id.get(iid)
        if it is None:
            continue
        out.append(
            {
                "item_id": it.item_id,
                "kud_column": it.kud_column,
                "knowledge_type": it.knowledge_type,
                "assessment_route": it.assessment_route,
                "content_statement": it.content_statement,
                "source_block_id": it.source_block_id,
                "prerequisite_lts": list(it.prerequisite_lts),
            }
        )
    return out


def _validate_parsed(
    obj: dict[str, Any] | None,
    *,
    competency_kt_mix: set[str],
    expected_item_ids: set[str],
) -> list[dict[str, Any]] | None:
    """Return validated LT list or None if the run is malformed."""
    if not isinstance(obj, dict):
        return None
    raw = obj.get("lts")
    if not isinstance(raw, list):
        return None
    if len(raw) < 2 or len(raw) > 3:
        return None
    seen_names: set[str] = set()
    clean: list[dict[str, Any]] = []
    for lt in raw:
        if not isinstance(lt, dict):
            return None
        name = str(lt.get("lt_name", "")).strip()
        if not name or name in seen_names:
            return None
        seen_names.add(name)
        definition = str(lt.get("lt_definition", "")).strip()
        if not definition:
            return None
        kt_raw = str(lt.get("knowledge_type", "")).strip()
        kt_norm = kt_raw.lower().replace("type", "type ").replace("  ", " ").strip()
        if kt_norm.startswith("type "):
            kt_norm = "Type " + kt_norm.split()[-1]
        if kt_norm not in _VALID_TYPES:
            return None
        route = str(lt.get("assessment_route", "")).strip().lower().replace("-", "_")
        if route not in _VALID_ROUTES:
            return None
        if _TYPE_TO_ROUTE[kt_norm] != route:
            return None
        # Definition-format check: Type 3 must start with "The student"; Type 1/2 with "I can".
        lowered = definition.lower()
        if kt_norm == "Type 3":
            if not lowered.startswith("the student"):
                return None
        else:
            if not lowered.startswith("i can"):
                return None
        kud_ids = lt.get("kud_item_ids") or []
        if not isinstance(kud_ids, list) or not kud_ids:
            return None
        norm_ids: list[str] = []
        for x in kud_ids:
            s = str(x).strip()
            if s not in expected_item_ids:
                return None
            norm_ids.append(s)
        prereq_names = lt.get("prerequisite_lt_names") or []
        if not isinstance(prereq_names, list):
            return None
        prereq_names = [str(x).strip() for x in prereq_names if str(x).strip()]
        clean.append(
            {
                "lt_name": name,
                "lt_definition": definition,
                "knowledge_type": kt_norm,
                "assessment_route": route,
                "kud_item_ids": norm_ids,
                "prerequisite_lt_names": prereq_names,
            }
        )
    # Knowledge-type split: if competency has both Type 3 AND (Type 1 or Type 2), LT set must too.
    competency_has_t3 = "Type 3" in competency_kt_mix
    competency_has_t12 = bool({"Type 1", "Type 2"} & competency_kt_mix)
    lt_types = {lt["knowledge_type"] for lt in clean}
    if competency_has_t3 and competency_has_t12:
        if "Type 3" not in lt_types or not ({"Type 1", "Type 2"} & lt_types):
            return None
    # Every expected item must be covered by at least one LT.
    covered: set[str] = set()
    for lt in clean:
        covered.update(lt["kud_item_ids"])
    if covered != expected_item_ids:
        return None
    return clean


def _signature(run: list[dict[str, Any]]) -> tuple[Any, ...]:
    return (
        len(run),
        tuple(sorted(lt["knowledge_type"] for lt in run)),
    )


async def _one_generation_run(
    *,
    client: Any,
    model: str,
    temperature: float,
    cluster: CompetencyCluster,
    items: list[dict[str, Any]],
    competency_kt_mix: set[str],
    expected_ids: set[str],
    run_idx: int,
) -> list[dict[str, Any]] | None:
    user_prompt = build_user_prompt(
        competency_name=cluster.competency_name,
        competency_definition=cluster.competency_definition,
        dominant_knowledge_type=cluster.dominant_knowledge_type,
        kud_items=items,
    )
    label = f"refauth_lt {cluster.cluster_id} run{run_idx}"
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
        logger.warning("lt generation timeout: %s", label)
        return None
    except Exception:  # noqa: BLE001
        logger.exception("lt generation error: %s", label)
        return None
    parsed = extract_json_object(text)
    validated = _validate_parsed(
        parsed,
        competency_kt_mix=competency_kt_mix,
        expected_item_ids=expected_ids,
    )
    if validated is None:
        logger.warning("lt generation parse/validation failed: %s", label)
    return validated


async def _generate_for_cluster(
    *,
    client: Any,
    model: str,
    temperature: float,
    cluster: CompetencyCluster,
    kud: ReferenceKUD,
    runs: int,
) -> tuple[list[LearningTarget], dict[str, Any] | None]:
    items = _items_for_cluster(cluster, kud)
    if not items:
        return [], {
            "cluster_id": cluster.cluster_id,
            "halt_reason": "no_items",
            "diagnostic": "cluster contains no resolvable KUD items",
        }
    competency_kt_mix = {it["knowledge_type"] for it in items}
    expected_ids = {it["item_id"] for it in items}

    coros = [
        _one_generation_run(
            client=client,
            model=model,
            temperature=temperature,
            cluster=cluster,
            items=items,
            competency_kt_mix=competency_kt_mix,
            expected_ids=expected_ids,
            run_idx=i + 1,
        )
        for i in range(runs)
    ]
    results = await asyncio.gather(*coros)
    valid: list[list[dict[str, Any]]] = [r for r in results if r is not None]

    if len(valid) < 2:
        return [], {
            "cluster_id": cluster.cluster_id,
            "competency_name": cluster.competency_name,
            "halt_reason": "lt_set_unreliable",
            "diagnostic": f"only {len(valid)}/{runs} runs produced parseable output",
            "valid_runs": len(valid),
        }

    sig_counts: Counter[Any] = Counter()
    for r in valid:
        sig_counts[_signature(r)] += 1
    top_sig, top_count = sig_counts.most_common(1)[0]
    if top_count < 2:
        return [], {
            "cluster_id": cluster.cluster_id,
            "competency_name": cluster.competency_name,
            "halt_reason": "lt_set_unreliable",
            "diagnostic": (
                f"no signature reached 2/3 agreement; signatures={list(sig_counts)}"
            ),
            "signatures": [str(s) for s in sig_counts],
        }

    majority_run = next(r for r in valid if _signature(r) == top_sig)
    stability = "stable" if top_count == runs else "lt_set_unstable"

    per_run_sigs: list[dict[str, Any]] = []
    for idx, r in enumerate(valid, start=1):
        per_run_sigs.append(
            {
                "run": idx,
                "lt_count": len(r),
                "kt_multiset": sorted(lt["knowledge_type"] for lt in r),
                "lt_names": [lt["lt_name"] for lt in r],
            }
        )

    lts: list[LearningTarget] = []
    for i, lt in enumerate(majority_run, start=1):
        lt_id = f"{cluster.cluster_id}_lt_{i:02d}"
        lts.append(
            LearningTarget(
                lt_id=lt_id,
                cluster_id=cluster.cluster_id,
                competency_name=cluster.competency_name,
                lt_name=lt["lt_name"],
                lt_definition=lt["lt_definition"],
                knowledge_type=lt["knowledge_type"],
                assessment_route=lt["assessment_route"],
                kud_item_ids=list(lt["kud_item_ids"]),
                prerequisite_lts=list(lt["prerequisite_lt_names"]),
                stability_flag=stability,
                per_run_signatures=per_run_sigs,
                stability_diagnostics=(
                    [] if stability == "stable" else [f"lt_set_signature={top_sig}", f"counts={dict(sig_counts)}"]
                ),
            )
        )
    return lts, None


async def generate_lts(
    kud: ReferenceKUD,
    cluster_set: CompetencyClusterSet,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    runs: int = DEFAULT_RUNS,
    concurrency: int = CLUSTER_CONCURRENCY,
) -> LearningTargetSet:
    client = get_async_client()
    sem = asyncio.Semaphore(concurrency)

    async def _bounded(cluster: CompetencyCluster):
        async with sem:
            return await _generate_for_cluster(
                client=client,
                model=model,
                temperature=temperature,
                cluster=cluster,
                kud=kud,
                runs=runs,
            )

    tasks = [_bounded(c) for c in cluster_set.clusters]
    outputs = await asyncio.gather(*tasks)

    lt_set = LearningTargetSet(
        source_slug=cluster_set.source_slug,
        model=model,
        temperature=temperature,
        runs=runs,
    )
    for (lts, halted) in outputs:
        lt_set.lts.extend(lts)
        if halted is not None:
            lt_set.halted_clusters.append(halted)
    return lt_set


def generate_lts_sync(
    kud: ReferenceKUD,
    cluster_set: CompetencyClusterSet,
    **kwargs: Any,
) -> LearningTargetSet:
    return asyncio.run(generate_lts(kud, cluster_set, **kwargs))
