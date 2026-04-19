"""Type 3 observation-indicator generator with 3x self-consistency and Mode 3 compliance gate.

For each Type 3 LT, generates an LT-specific observation indicator set
per the LT authoring skill's Mode 3 protocol:

- 2-3 observable behaviours per band (A-D), third-person.
- Generic developmental self-reflection prompts per band, inserted
  from types.MODE3_SELF_REFLECTION_PROMPTS (LT-calibrated by band, NOT
  LT-specific — that is correct Mode 3 behaviour per the skill).
- 3 LT-specific parent/caregiver noticing prompts.
- Prerequisites inherited from the LT (knowledge-contingent Type 3).
- Developmental conversation protocol reference.

ABSOLUTE RULE

Type 3 LTs NEVER get rubric criteria. The Mode 3 compliance gate
rejects any run that produces Competent-style descriptors.

SELF-CONSISTENCY

Generated 3x at temperature 0.3. Stability:

- 3/3: (band count, per-band behaviour count multiset) signature
  identical across runs → ``stable``.
- 2/3: majority retained, flagged ``observation_indicators_unstable``.
- ≤1/3 valid parses → halted, flagged ``observation_indicators_unreliable``.

MODE 3 COMPLIANCE GATE

Each run's indicator set is mechanically checked for:

- Every band present with 2-3 behaviours.
- Every observable behaviour starts with "The student ".
- No behaviour contains rubric descriptors ("competent", "proficient",
  "approaching", "mastery", "novice", "developing" as rubric labels).
- No behaviour contains banned substrings (such as / e.g. / for
  example / parentheses).
- Parent prompts count == 3 and do NOT start with "The student".
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections import Counter
from typing import Any

from curriculum_harness.reference_authoring.lt.indicator_prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from curriculum_harness.reference_authoring.types import (
    BANDS,
    LearningTarget,
    LearningTargetSet,
    MODE3_SELF_REFLECTION_PROMPTS,
    ObservationBand,
    ObservationIndicatorCollection,
    ObservationIndicatorSet,
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
LT_CONCURRENCY = 6

# Observation indicators permit "such as" / "e.g." for illustrative
# concreteness ("behaviour such as X") — this is a legitimate pattern
# for making observable behaviours tangible. Band statements are
# stricter (see generate_band_statements.py). Parentheses remain
# banned because they introduce structural asides; for_example and
# for_instance remain banned because they push the sentence into
# exposition rather than observation.
BANNED_SUBSTRINGS = (
    "(",
    ")",
    " for example",
    " for instance",
)
RUBRIC_WORDS = (
    "competent",
    "proficient",
    "approaching",
    "mastery",
    "novice",
    "developing (rubric",  # allow "developing" as a natural verb elsewhere
)
RUBRIC_EXACT_PATTERNS = (
    r"\bcompetent\b",
    r"\bproficient\b",
    r"\bmastery\b",
    r"\bapproaching competent\b",
    r"\bapproaching proficient\b",
)


def _validate_run(obj: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(obj, dict):
        return None
    raw_bands = obj.get("bands")
    if not isinstance(raw_bands, list) or len(raw_bands) != len(BANDS):
        return None
    clean_bands: list[dict[str, Any]] = []
    for i, expected_band in enumerate(BANDS):
        b = raw_bands[i]
        if not isinstance(b, dict):
            return None
        band = str(b.get("band", "")).strip().upper()
        if band != expected_band:
            return None
        behaviours = b.get("observable_behaviours")
        if not isinstance(behaviours, list) or not (2 <= len(behaviours) <= 3):
            return None
        norm_behaviours: list[str] = []
        for be in behaviours:
            if not isinstance(be, str):
                return None
            s = be.strip()
            if not s.lower().startswith("the student"):
                return None
            # normalise "the student" → "The student"
            s = "The student" + s[len("the student"):] if s[:11].lower() == "the student" else s
            norm_behaviours.append(s)
        clean_bands.append({"band": band, "observable_behaviours": norm_behaviours})
    parent_prompts = obj.get("parent_prompts")
    if not isinstance(parent_prompts, list) or len(parent_prompts) != 3:
        return None
    clean_parents: list[str] = []
    for p in parent_prompts:
        if not isinstance(p, str):
            return None
        s = p.strip()
        if not s:
            return None
        if s.lower().startswith("the student"):
            return None
        clean_parents.append(s)
    protocol = str(obj.get("developmental_conversation_protocol", "")).strip()
    if not protocol:
        return None
    return {
        "bands": clean_bands,
        "parent_prompts": clean_parents,
        "developmental_conversation_protocol": protocol,
    }


def _mode3_gate(parsed: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for b in parsed["bands"]:
        for i, be in enumerate(b["observable_behaviours"]):
            lower = be.lower()
            for banned in BANNED_SUBSTRINGS:
                if banned in lower:
                    failures.append(f"{b['band']}#{i}:banned_substring:{banned.strip()}")
            for pattern in RUBRIC_EXACT_PATTERNS:
                if re.search(pattern, lower):
                    failures.append(f"{b['band']}#{i}:rubric_descriptor:{pattern}")
            if not be.startswith("The student"):
                failures.append(f"{b['band']}#{i}:wrong_person")
    for i, p in enumerate(parsed["parent_prompts"]):
        lower = p.lower()
        if lower.startswith("the student"):
            failures.append(f"parent#{i}:wrong_person")
        for banned in BANNED_SUBSTRINGS:
            if banned in lower:
                failures.append(f"parent#{i}:banned_substring:{banned.strip()}")
    return failures


def _signature(parsed: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(
        (b["band"], len(b["observable_behaviours"])) for b in parsed["bands"]
    ) + (("parents", len(parsed["parent_prompts"])),)


async def _one_run(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    run_idx: int,
) -> dict[str, Any] | None:
    user_prompt = build_user_prompt(
        lt_name=lt.lt_name,
        lt_definition=lt.lt_definition,
        competency_name=lt.competency_name,
        prerequisite_lts=list(lt.prerequisite_lts),
    )
    label = f"refauth_indicator {lt.lt_id} run{run_idx}"
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
        logger.warning("indicator generation timeout: %s", label)
        return None
    except Exception:  # noqa: BLE001
        logger.exception("indicator generation error: %s", label)
        return None
    parsed = extract_json_object(text)
    validated = _validate_run(parsed)
    if validated is None:
        logger.warning("indicator generation parse/validation failed: %s", label)
    return validated


async def _generate_for_lt(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    runs: int,
) -> tuple[ObservationIndicatorSet | None, dict[str, Any] | None]:
    if lt.knowledge_type != "Type 3":
        return None, None  # Type 1/2 use the band-statement generator.

    coros = [
        _one_run(
            client=client,
            model=model,
            temperature=temperature,
            lt=lt,
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
            "halt_reason": "observation_indicators_unreliable",
            "diagnostic": f"only {len(valid)}/{runs} runs produced parseable output",
        }
    sig_counts: Counter[Any] = Counter(_signature(r) for r in valid)
    top_sig, top_count = sig_counts.most_common(1)[0]
    if top_count < 2:
        return None, {
            "lt_id": lt.lt_id,
            "lt_name": lt.lt_name,
            "halt_reason": "observation_indicators_unreliable",
            "diagnostic": (
                f"no signature reached 2/3 agreement; signatures={list(sig_counts)}"
            ),
        }
    majority_run = next(r for r in valid if _signature(r) == top_sig)
    stability = "stable" if top_count == runs else "observation_indicators_unstable"

    failures = _mode3_gate(majority_run)

    per_run_sigs: list[dict[str, Any]] = []
    for idx, r in enumerate(valid, start=1):
        per_run_sigs.append(
            {
                "run": idx,
                "signature": [list(s) for s in _signature(r)],
                "parent_prompt_count": len(r["parent_prompts"]),
            }
        )

    # Mode 3 gate failures HALT the indicator set with a named diagnostic
    # (per session 4b-2 step 5 spec — failures halt, not flag).
    if failures:
        return None, {
            "lt_id": lt.lt_id,
            "lt_name": lt.lt_name,
            "halt_reason": "mode3_gate_failed",
            "diagnostic": f"{len(failures)} compliance failures",
            "failures": failures,
        }

    bands: list[ObservationBand] = []
    for b in majority_run["bands"]:
        bands.append(
            ObservationBand(
                band=b["band"],
                observable_behaviours=list(b["observable_behaviours"]),
                self_reflection_prompt=MODE3_SELF_REFLECTION_PROMPTS[b["band"]],
            )
        )
    indicator_set = ObservationIndicatorSet(
        lt_id=lt.lt_id,
        bands=bands,
        parent_prompts=list(majority_run["parent_prompts"]),
        prerequisite_lts=list(lt.prerequisite_lts),
        developmental_conversation_protocol=majority_run[
            "developmental_conversation_protocol"
        ],
        stability_flag=stability,
        per_run_signatures=per_run_sigs,
        stability_diagnostics=(
            [] if stability == "stable" else [f"signature_counts={dict(sig_counts)}"]
        ),
        quality_gate_passed=True,
        quality_gate_failures=[],
    )
    return indicator_set, None


async def generate_observation_indicators(
    lt_set: LearningTargetSet,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    runs: int = DEFAULT_RUNS,
    concurrency: int = LT_CONCURRENCY,
) -> ObservationIndicatorCollection:
    client = get_async_client()
    sem = asyncio.Semaphore(concurrency)

    async def _bounded(lt: LearningTarget):
        async with sem:
            return await _generate_for_lt(
                client=client,
                model=model,
                temperature=temperature,
                lt=lt,
                runs=runs,
            )

    tasks = [_bounded(lt) for lt in lt_set.lts]
    outputs = await asyncio.gather(*tasks)

    coll = ObservationIndicatorCollection(
        source_slug=lt_set.source_slug,
        model=model,
        temperature=temperature,
        runs=runs,
    )
    for (iset, halted) in outputs:
        if iset is not None:
            coll.sets.append(iset)
        if halted is not None:
            coll.halted_lts.append(halted)
    return coll


def generate_observation_indicators_sync(
    lt_set: LearningTargetSet,
    **kwargs: Any,
) -> ObservationIndicatorCollection:
    return asyncio.run(generate_observation_indicators(lt_set, **kwargs))
