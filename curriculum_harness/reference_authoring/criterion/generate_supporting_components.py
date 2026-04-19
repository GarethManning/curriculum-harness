"""Type 1/2 supporting-components generator.

Per Type 1 / Type 2 LT with an authored rubric, generates three
supporting artefacts:

- CoConstructionPlan — teacher moves for building the rubric WITH
  students (stages, student prompts, anchor-examples guidance).
- StudentRubric — "I can"-style student-facing version of the five
  levels plus self-check prompts.
- FeedbackGuide — per-level teacher moves that advance to the next
  level (no "next level" for extending, so moves_by_level omits it).

Runs 3x at temperature 0.3 with a structural signature (stage count,
student-prompt count, student-rubric level-name order, feedback-move
level coverage, move-count per level). Halts if ≤1 run parses or no
signature reaches 2/3.
"""

from __future__ import annotations

import asyncio
import logging
from collections import Counter
from typing import Any

from curriculum_harness.reference_authoring.criterion.criterion_prompts import (
    build_supporting_system_prompt,
    build_supporting_user_prompt,
)
from curriculum_harness.reference_authoring.types import (
    CoConstructionPlan,
    FeedbackGuide,
    LearningTarget,
    LearningTargetSet,
    RUBRIC_LEVEL_ORDER,
    Rubric,
    RubricCollection,
    RubricLevel,
    StudentRubric,
    SupportingComponents,
    SupportingComponentsCollection,
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
DEFAULT_MAX_TOKENS = 2048
LT_CONCURRENCY = 6

_FEEDBACK_LEVELS = ("no_evidence", "emerging", "developing", "competent")


def _nonempty_str_list(raw: Any, *, min_len: int, max_len: int) -> list[str] | None:
    if not isinstance(raw, list):
        return None
    if not (min_len <= len(raw) <= max_len):
        return None
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            return None
        s = item.strip()
        if not s:
            return None
        out.append(s)
    return out


def _validate_run(obj: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(obj, dict):
        return None

    # --- co-construction plan
    ccp = obj.get("co_construction_plan")
    if not isinstance(ccp, dict):
        return None
    stages = _nonempty_str_list(ccp.get("stages"), min_len=3, max_len=5)
    prompts = _nonempty_str_list(ccp.get("student_prompts"), min_len=3, max_len=5)
    anchor = ccp.get("anchor_examples_guidance")
    if stages is None or prompts is None:
        return None
    if not isinstance(anchor, str) or not anchor.strip():
        return None

    # --- student rubric
    sr = obj.get("student_rubric")
    if not isinstance(sr, dict):
        return None
    levels_raw = sr.get("levels")
    if not isinstance(levels_raw, list) or len(levels_raw) != len(RUBRIC_LEVEL_ORDER):
        return None
    sr_levels: list[dict[str, str]] = []
    for i, expected in enumerate(RUBRIC_LEVEL_ORDER):
        entry = levels_raw[i]
        if not isinstance(entry, dict):
            return None
        name = str(entry.get("name", "")).strip()
        desc = str(entry.get("descriptor", "")).strip()
        if name != expected or not desc:
            return None
        low = desc.lower()
        if expected == "no_evidence":
            if not low.startswith("i have not yet"):
                return None
        else:
            if not low.startswith("i can"):
                return None
        sr_levels.append({"name": expected, "descriptor": desc})
    sc_prompts = _nonempty_str_list(sr.get("self_check_prompts"), min_len=2, max_len=3)
    if sc_prompts is None:
        return None

    # --- feedback guide
    fg = obj.get("feedback_guide")
    if not isinstance(fg, dict):
        return None
    moves_raw = fg.get("moves_by_level")
    if not isinstance(moves_raw, dict):
        return None
    moves: dict[str, list[str]] = {}
    for level in _FEEDBACK_LEVELS:
        level_moves = _nonempty_str_list(moves_raw.get(level), min_len=2, max_len=3)
        if level_moves is None:
            return None
        moves[level] = level_moves

    return {
        "co_construction_plan": {
            "stages": stages,
            "student_prompts": prompts,
            "anchor_examples_guidance": anchor.strip(),
        },
        "student_rubric": {"levels": sr_levels, "self_check_prompts": sc_prompts},
        "feedback_guide": {"moves_by_level": moves},
    }


def _signature(parsed: dict[str, Any]) -> tuple[Any, ...]:
    ccp = parsed["co_construction_plan"]
    fg = parsed["feedback_guide"]["moves_by_level"]
    return (
        ("stages", len(ccp["stages"])),
        ("student_prompts", len(ccp["student_prompts"])),
        ("student_rubric_levels", tuple(e["name"] for e in parsed["student_rubric"]["levels"])),
        ("self_check_prompts", len(parsed["student_rubric"]["self_check_prompts"])),
        tuple(("moves", level, len(fg[level])) for level in _FEEDBACK_LEVELS),
    )


async def _one_run(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    rubric: Rubric,
    system_prompt: str,
    run_idx: int,
) -> dict[str, Any] | None:
    user_prompt = build_supporting_user_prompt(
        lt=lt,
        rubric_levels={lvl.name: lvl.descriptor for lvl in rubric.levels},
    )
    label = f"refauth_supporting {lt.lt_id} run{run_idx}"
    try:
        text = await haiku_stream_text(
            client,
            model=model,
            max_tokens=DEFAULT_MAX_TOKENS,
            system=system_prompt,
            user_blocks=[{"type": "text", "text": user_prompt}],
            label=label,
            temperature=temperature,
        )
    except AnthropicCallTimeout:
        logger.warning("supporting generation timeout: %s", label)
        return None
    except Exception:  # noqa: BLE001
        logger.exception("supporting generation error: %s", label)
        return None
    parsed = extract_json_object(text)
    validated = _validate_run(parsed)
    if validated is None:
        logger.warning("supporting generation parse/validation failed: %s", label)
    return validated


async def _generate_for_rubric(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    rubric: Rubric,
    system_prompt: str,
    runs: int,
) -> tuple[SupportingComponents | None, dict[str, Any] | None]:
    coros = [
        _one_run(
            client=client,
            model=model,
            temperature=temperature,
            lt=lt,
            rubric=rubric,
            system_prompt=system_prompt,
            run_idx=i + 1,
        )
        for i in range(runs)
    ]
    results = await asyncio.gather(*coros)
    valid = [r for r in results if r is not None]
    if len(valid) < 2:
        return None, {
            "lt_id": lt.lt_id,
            "lt_name": lt.lt_name,
            "halt_reason": "supporting_unreliable",
            "diagnostic": f"only {len(valid)}/{runs} runs produced parseable output",
        }

    sig_counts: Counter[Any] = Counter(_signature(r) for r in valid)
    top_sig, top_count = sig_counts.most_common(1)[0]
    if top_count < 2:
        return None, {
            "lt_id": lt.lt_id,
            "lt_name": lt.lt_name,
            "halt_reason": "supporting_unreliable",
            "diagnostic": (
                f"no structural signature reached 2/3 agreement; "
                f"signatures={list(sig_counts)}"
            ),
        }
    majority = next(r for r in valid if _signature(r) == top_sig)
    stability = "stable" if top_count == runs else "supporting_unstable"

    co_plan = CoConstructionPlan(
        lt_id=lt.lt_id,
        stages=list(majority["co_construction_plan"]["stages"]),
        student_prompts=list(majority["co_construction_plan"]["student_prompts"]),
        anchor_examples_guidance=majority["co_construction_plan"][
            "anchor_examples_guidance"
        ],
    )
    stud_rub = StudentRubric(
        lt_id=lt.lt_id,
        levels=[
            RubricLevel(
                name=e["name"],
                descriptor=e["descriptor"],
                word_count=len(e["descriptor"].split()),
            )
            for e in majority["student_rubric"]["levels"]
        ],
        self_check_prompts=list(majority["student_rubric"]["self_check_prompts"]),
    )
    fb_guide = FeedbackGuide(
        lt_id=lt.lt_id,
        moves_by_level={
            level: list(majority["feedback_guide"]["moves_by_level"][level])
            for level in _FEEDBACK_LEVELS
        },
    )

    per_run_sigs: list[dict[str, Any]] = []
    for idx, r in enumerate(valid, start=1):
        sig = _signature(r)
        per_run_sigs.append(
            {
                "run": idx,
                "signature": [
                    list(x) if isinstance(x, tuple) else x for x in sig
                ],
            }
        )

    components = SupportingComponents(
        lt_id=lt.lt_id,
        co_construction_plan=co_plan,
        student_rubric=stud_rub,
        feedback_guide=fb_guide,
        stability_flag=stability,
        per_run_signatures=per_run_sigs,
        stability_diagnostics=(
            [] if stability == "stable" else [f"signature_counts={dict(sig_counts)}"]
        ),
    )
    return components, None


async def generate_supporting_components(
    lt_set: LearningTargetSet,
    rubric_collection: RubricCollection,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    runs: int = DEFAULT_RUNS,
    concurrency: int = LT_CONCURRENCY,
) -> SupportingComponentsCollection:
    """Generate supporting components for every LT that has a rubric.

    Only LTs with an authored rubric (present in ``rubric_collection``)
    receive supporting components. Halted LTs are skipped.
    """
    client = get_async_client()
    sem = asyncio.Semaphore(concurrency)
    system_prompt = build_supporting_system_prompt()

    lt_by_id = {lt.lt_id: lt for lt in lt_set.lts}

    async def _bounded(rubric: Rubric):
        lt = lt_by_id.get(rubric.lt_id)
        if lt is None:
            return None, {
                "lt_id": rubric.lt_id,
                "lt_name": "",
                "halt_reason": "lt_not_found",
                "diagnostic": f"no LT in lt_set matches rubric lt_id={rubric.lt_id}",
            }
        async with sem:
            return await _generate_for_rubric(
                client=client,
                model=model,
                temperature=temperature,
                lt=lt,
                rubric=rubric,
                system_prompt=system_prompt,
                runs=runs,
            )

    tasks = [_bounded(r) for r in rubric_collection.rubrics]
    outputs = await asyncio.gather(*tasks)

    coll = SupportingComponentsCollection(
        source_slug=lt_set.source_slug,
        model=model,
        temperature=temperature,
        runs=runs,
    )
    for (comp, halted) in outputs:
        if comp is not None:
            coll.components.append(comp)
        if halted is not None:
            coll.halted_lts.append(halted)
    return coll


def generate_supporting_components_sync(
    lt_set: LearningTargetSet,
    rubric_collection: RubricCollection,
    **kwargs: Any,
) -> SupportingComponentsCollection:
    return asyncio.run(
        generate_supporting_components(lt_set, rubric_collection, **kwargs)
    )
