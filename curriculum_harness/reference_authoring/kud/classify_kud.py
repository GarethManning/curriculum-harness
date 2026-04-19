"""Reference KUD classifier with 3x self-consistency.

Applies the LT authoring skill Step 0 decision tree to each content
block in a ``SourceInventory``. Calls the model 3 times per block at
temperature 0.3 (per Session 4b arc plan v3) and resolves per-block
stability:

- 3/3 agreement on the (kud_column, knowledge_type, assessment_route)
  signature of all items → ``stable``; run-1's items are retained.
- 2/3 agreement → ``classification_unstable``; majority run's items are
  retained and each item carries the flag.
- ≤1/3 agreement → ``classification_unreliable``; block halts with no
  KUD items produced and is captured as a ``HaltedBlock``.

Severe underspecification (≥2 runs flag ``severe``) also halts the
block. Milder flags attach to items produced.
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from typing import Any

from curriculum_harness.reference_authoring.kud.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from curriculum_harness.reference_authoring.types import (
    HaltedBlock,
    KUDItem,
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
DEFAULT_MAX_TOKENS = 2048
BLOCK_CONCURRENCY = 4  # limit how many blocks are classified concurrently


_VALID_COLUMNS = {"know", "understand", "do_skill", "do_disposition"}
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


def _validate_parsed(obj: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return a normalised dict or None if the classification is malformed.

    Lightly normalises the ``items`` list (coerces kud_column/type/route to
    the canonical strings, drops items that cannot be made valid). A result
    where every item is valid or where items=[] with a severe flag is
    considered parse-valid.
    """
    if not isinstance(obj, dict):
        return None
    flag = obj.get("underspecification_flag")
    if flag not in (None, "null", "mild", "moderate", "severe"):
        return None
    if flag == "null":
        flag = None
    raw_items = obj.get("items")
    if not isinstance(raw_items, list):
        return None
    clean_items: list[dict[str, Any]] = []
    for it in raw_items:
        if not isinstance(it, dict):
            return None
        col = str(it.get("kud_column", "")).strip().lower().replace("-", "_")
        col = col.replace("do-skill", "do_skill").replace("do-disposition", "do_disposition")
        if col not in _VALID_COLUMNS:
            return None
        kt_raw = str(it.get("knowledge_type", "")).strip()
        # Accept "type 1", "TYPE 1", "Type1" variants.
        kt_norm = kt_raw.lower().replace("type", "type ").replace("  ", " ").strip()
        if kt_norm.startswith("type "):
            kt_norm = "Type " + kt_norm.split()[-1]
        if kt_norm not in _VALID_TYPES:
            return None
        route = str(it.get("assessment_route", "")).strip().lower().replace("-", "_")
        if route not in _VALID_ROUTES:
            return None
        # Enforce the type→route and type↔column contracts.
        if _TYPE_TO_ROUTE[kt_norm] != route:
            return None
        if kt_norm == "Type 3" and col != "do_disposition":
            return None
        if col == "do_disposition" and kt_norm != "Type 3":
            return None
        content = str(it.get("content_statement", "")).strip()
        if not content:
            return None
        rationale = str(it.get("classification_rationale", "")).strip()
        prereq = it.get("prerequisite_lts") or []
        if not isinstance(prereq, list):
            prereq = []
        prereq = [str(p).strip() for p in prereq if str(p).strip()]
        clean_items.append(
            {
                "kud_column": col,
                "knowledge_type": kt_norm,
                "assessment_route": route,
                "content_statement": content,
                "classification_rationale": rationale,
                "prerequisite_lts": prereq,
            }
        )
    if flag == "severe" and clean_items:
        # Severe-flag runs must produce no items.
        return None
    if flag != "severe" and not clean_items:
        # Non-severe runs must produce at least one item.
        return None
    return {
        "underspecification_flag": flag,
        "underspecification_rationale": str(obj.get("underspecification_rationale", "")).strip(),
        "items": clean_items,
    }


def _signature(parsed: dict[str, Any]) -> tuple[Any, ...]:
    """Stable signature for self-consistency comparison.

    Captures whether the block is severe-underspecified and, if not, the
    sorted multiset of (kud_column, knowledge_type) tuples. Assessment
    route is derivable from knowledge_type so it is excluded to avoid
    double-counting.
    """
    if parsed["underspecification_flag"] == "severe":
        return ("severe",)
    multiset = tuple(
        sorted((it["kud_column"], it["knowledge_type"]) for it in parsed["items"])
    )
    return ("items", multiset)


async def _single_classification(
    *,
    client: Any,
    model: str,
    temperature: float,
    block_id: str,
    heading_path: list[str],
    block_type: str,
    raw_text: str,
    run_idx: int,
    source_context: str = "",
) -> dict[str, Any] | None:
    user_prompt = build_user_prompt(
        block_id=block_id,
        heading_path=heading_path,
        block_type=block_type,
        raw_text=raw_text,
        source_context=source_context,
    )
    label = f"refauth_kud {block_id} run{run_idx}"
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
        logger.warning("classification timeout: %s", label)
        return None
    except Exception:  # noqa: BLE001 — defensive; model errors should not halt the pipeline
        logger.exception("classification error: %s", label)
        return None
    parsed_obj = extract_json_object(text)
    validated = _validate_parsed(parsed_obj)
    if validated is None:
        logger.warning("classification parse/validation failed: %s", label)
        return None
    validated["_raw_response"] = text
    return validated


async def _classify_single_block(
    *,
    client: Any,
    model: str,
    temperature: float,
    block: Any,
    runs: int,
    block_idx: int,
    total_blocks: int,
    source_context: str = "",
) -> tuple[str, list[KUDItem], HaltedBlock | None, list[dict[str, Any]]]:
    """Returns (stability_flag, items, halted_block_or_none, per_run_records)."""
    print(
        f"[refauth_kud] block {block_idx+1}/{total_blocks} {block.block_id} "
        f"(lines {block.line_start}-{block.line_end})",
        flush=True,
    )
    coros = [
        _single_classification(
            client=client,
            model=model,
            temperature=temperature,
            block_id=block.block_id,
            heading_path=block.heading_path,
            block_type=block.block_type,
            raw_text=block.raw_text,
            run_idx=i + 1,
            source_context=source_context,
        )
        for i in range(runs)
    ]
    results = await asyncio.gather(*coros)

    per_run_records: list[dict[str, Any]] = []
    valid_parses: list[dict[str, Any]] = []
    for i, r in enumerate(results):
        if r is None:
            per_run_records.append(
                {
                    "run": i + 1,
                    "ok": False,
                    "diagnostic": "call_or_parse_failed",
                }
            )
            continue
        per_run_records.append(
            {
                "run": i + 1,
                "ok": True,
                "underspecification_flag": r["underspecification_flag"],
                "items_signature": [
                    {
                        "kud_column": it["kud_column"],
                        "knowledge_type": it["knowledge_type"],
                    }
                    for it in r["items"]
                ],
            }
        )
        valid_parses.append(r)

    # Require ≥2 valid parses to resolve stability; otherwise halt.
    if len(valid_parses) < 2:
        halted = HaltedBlock(
            block_id=block.block_id,
            source_block_raw_text=block.raw_text,
            halt_reason="classification_unreliable",
            per_run_classifications=per_run_records,
            diagnostic=(
                f"only {len(valid_parses)}/{runs} runs produced parseable output; "
                "cannot resolve self-consistency"
            ),
        )
        return ("classification_unreliable", [], halted, per_run_records)

    # Count signatures.
    sig_counts: Counter[Any] = Counter()
    for p in valid_parses:
        sig_counts[_signature(p)] += 1
    top_sig, top_count = sig_counts.most_common(1)[0]

    if top_count >= 2 and top_sig == ("severe",):
        severe_parse = next(p for p in valid_parses if _signature(p) == top_sig)
        halted = HaltedBlock(
            block_id=block.block_id,
            source_block_raw_text=block.raw_text,
            halt_reason="severe_underspecification",
            per_run_classifications=per_run_records,
            diagnostic=severe_parse.get("underspecification_rationale", "")
            or "severe underspecification confirmed by majority of runs",
        )
        return ("severe_underspecification", [], halted, per_run_records)

    if top_count < 2:
        halted = HaltedBlock(
            block_id=block.block_id,
            source_block_raw_text=block.raw_text,
            halt_reason="classification_unreliable",
            per_run_classifications=per_run_records,
            diagnostic=(
                "no signature achieved 2/3 agreement across runs; "
                f"observed signatures: {list(sig_counts)}"
            ),
        )
        return ("classification_unreliable", [], halted, per_run_records)

    # Pick the first valid parse matching the majority signature.
    majority_parse = next(p for p in valid_parses if _signature(p) == top_sig)
    stability = "stable" if top_count == runs else "classification_unstable"
    items: list[KUDItem] = []
    for i, it in enumerate(majority_parse["items"], start=1):
        item_id = f"{block.block_id}_item_{i:02d}"
        items.append(
            KUDItem(
                item_id=item_id,
                kud_column=it["kud_column"],
                knowledge_type=it["knowledge_type"],
                assessment_route=it["assessment_route"],
                content_statement=it["content_statement"],
                source_block_id=block.block_id,
                classification_rationale=it["classification_rationale"],
                underspecification_flag=majority_parse["underspecification_flag"],
                prerequisite_lts=list(it["prerequisite_lts"]),
                stability_flag=stability,
                per_run_classifications=per_run_records,
            )
        )
    return (stability, items, None, per_run_records)


async def classify_inventory(
    inventory: SourceInventory,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    runs: int = DEFAULT_RUNS,
    concurrency: int = BLOCK_CONCURRENCY,
    source_context: str = "",
) -> ReferenceKUD:
    """Classify every content block in the inventory into a ReferenceKUD."""
    client = get_async_client()
    sem = asyncio.Semaphore(concurrency)

    async def _bounded(block_idx: int, block: Any):
        async with sem:
            return await _classify_single_block(
                client=client,
                model=model,
                temperature=temperature,
                block=block,
                runs=runs,
                block_idx=block_idx,
                total_blocks=len(inventory.content_blocks),
                source_context=source_context,
            )

    classifiable = [
        (idx, b)
        for idx, b in enumerate(inventory.content_blocks)
        if b.block_type != "heading"
    ]
    tasks = [_bounded(idx, b) for idx, b in classifiable]
    outputs = await asyncio.gather(*tasks)

    kud = ReferenceKUD(
        source_slug=inventory.source_slug,
        snapshot_path=inventory.snapshot_path,
        classification_model=model,
        classification_temperature=temperature,
        self_consistency_runs=runs,
    )
    for (_stability, items, halted, _records) in outputs:
        kud.items.extend(items)
        if halted is not None:
            kud.halted_blocks.append(halted)
    return kud


def classify_inventory_sync(
    inventory: SourceInventory,
    **kwargs: Any,
) -> ReferenceKUD:
    """Synchronous entry point for pipeline CLI."""
    return asyncio.run(classify_inventory(inventory, **kwargs))
