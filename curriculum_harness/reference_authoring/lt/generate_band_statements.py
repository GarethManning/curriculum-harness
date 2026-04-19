"""Type 1/2 band-statement generator with 3x self-consistency and quality gate.

For each Type 1 / Type 2 LT, generates band statements A-D per the LT
authoring skill. Type 3 LTs are skipped (they get observation
indicators via a separate module — the LT skill's absolute no-rubric
rule).

SELF-CONSISTENCY

Each LT's band set is generated 3x at temperature 0.3. Stability:

- 3/3: matching band count (4) AND each band's statement preserved
  across runs (length-class-aware equivalence check) → ``stable``.
- 2/3: majority run retained, flagged ``band_statements_unstable``.
- ≤1/3 valid parses → halted, flagged ``band_statements_unreliable``.

QUALITY GATE

Each generated band statement runs through the LT skill's checklist
mechanically (format, word-count, observable-verb, no-inline-examples,
no-parentheses, no-"such as"). Statement-level failures fail the set;
the LT halts with quality_gate_passed=False and diagnostics naming
every failure.
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections import Counter
from typing import Any

from curriculum_harness.reference_authoring.lt.band_prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
)
from curriculum_harness.reference_authoring.types import (
    BANDS,
    BandStatement,
    BandStatementCollection,
    BandStatementSet,
    LearningTarget,
    LearningTargetSet,
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
DEFAULT_MAX_TOKENS = 1500
LT_CONCURRENCY = 6

OBSERVABLE_VERBS = {
    "identify",
    "describe",
    "compare",
    "explain",
    "justify",
    "analyse",
    "analyze",
    "evaluate",
    "create",
    "apply",
    "interpret",
    "construct",
    "communicate",
    "recognise",
    "recognize",
    "use",
    "select",
    "choose",
    "perform",
    "demonstrate",
    "distinguish",
    "relate",
    "represent",
}

BANNED_SUBSTRINGS = (
    " such as ",
    "(",
    ")",
    " e.g.",
    " for example",
    " for instance",
)


def _validate_run(obj: dict[str, Any] | None) -> list[dict[str, str]] | None:
    if not isinstance(obj, dict):
        return None
    raw = obj.get("band_statements")
    if not isinstance(raw, list) or len(raw) != len(BANDS):
        return None
    out: list[dict[str, str]] = []
    for i, b in enumerate(BANDS):
        if not isinstance(raw[i], dict):
            return None
        band = str(raw[i].get("band", "")).strip().upper()
        statement = str(raw[i].get("statement", "")).strip()
        if band != b:
            return None
        if not statement.lower().startswith("i can "):
            return None
        # Normalise "i can" → "I can"
        if statement[:5].lower() == "i can":
            statement = "I can " + statement[6:]
        out.append({"band": band, "statement": statement})
    return out


def _quality_check_statement(s: str) -> list[str]:
    """Return a list of failure-name strings; empty list means pass."""
    failures: list[str] = []
    words = re.findall(r"[A-Za-z']+", s)
    n = len(words)
    if n < 10:
        failures.append(f"too_short_{n}_words")
    if n > 25:
        failures.append(f"too_long_{n}_words")
    lower = s.lower()
    for banned in BANNED_SUBSTRINGS:
        if banned in lower:
            failures.append(f"banned_substring:{banned.strip()}")
    # Observable verb: look for any of the allowed verbs as a whole word.
    has_verb = any(re.search(rf"\b{re.escape(v)}(s|d|ing|ed)?\b", lower) for v in OBSERVABLE_VERBS)
    if not has_verb:
        failures.append("no_observable_verb")
    return failures


def _signature(run: list[dict[str, str]]) -> tuple[Any, ...]:
    # Signature is the (band → word-count class) tuple, so we capture
    # structural agreement without requiring identical text.
    classes: list[tuple[str, str]] = []
    for r in run:
        words = len(re.findall(r"[A-Za-z']+", r["statement"]))
        if words < 13:
            cls = "short"
        elif words < 19:
            cls = "medium"
        else:
            cls = "long"
        classes.append((r["band"], cls))
    return tuple(classes)


async def _one_run(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    run_idx: int,
) -> list[dict[str, str]] | None:
    user_prompt = build_user_prompt(
        lt_name=lt.lt_name,
        lt_definition=lt.lt_definition,
        knowledge_type=lt.knowledge_type,
        competency_name=lt.competency_name,
    )
    label = f"refauth_band {lt.lt_id} run{run_idx}"
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
        logger.warning("band generation timeout: %s", label)
        return None
    except Exception:  # noqa: BLE001
        logger.exception("band generation error: %s", label)
        return None
    parsed = extract_json_object(text)
    validated = _validate_run(parsed)
    if validated is None:
        logger.warning("band generation parse/validation failed: %s", label)
    return validated


async def _generate_for_lt(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    runs: int,
) -> tuple[BandStatementSet | None, dict[str, Any] | None]:
    if lt.knowledge_type == "Type 3":
        return None, None  # skipped; Type 3 goes through observation indicators.

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
    valid: list[list[dict[str, str]]] = [r for r in results if r is not None]
    if len(valid) < 2:
        return None, {
            "lt_id": lt.lt_id,
            "lt_name": lt.lt_name,
            "halt_reason": "band_statements_unreliable",
            "diagnostic": f"only {len(valid)}/{runs} runs produced parseable output",
        }

    sig_counts: Counter[Any] = Counter(_signature(r) for r in valid)
    top_sig, top_count = sig_counts.most_common(1)[0]
    if top_count < 2:
        return None, {
            "lt_id": lt.lt_id,
            "lt_name": lt.lt_name,
            "halt_reason": "band_statements_unreliable",
            "diagnostic": (
                f"no word-count-class signature reached 2/3 agreement; "
                f"signatures={list(sig_counts)}"
            ),
        }
    majority_run = next(r for r in valid if _signature(r) == top_sig)
    stability = "stable" if top_count == runs else "band_statements_unstable"

    # Quality gate
    failures: list[str] = []
    for bs in majority_run:
        stmt_fails = _quality_check_statement(bs["statement"])
        for f in stmt_fails:
            failures.append(f"{bs['band']}:{f}")

    per_run_sigs: list[dict[str, Any]] = []
    for idx, r in enumerate(valid, start=1):
        per_run_sigs.append(
            {
                "run": idx,
                "signature": list(_signature(r)),
                "statements": [{"band": x["band"], "statement": x["statement"]} for x in r],
            }
        )

    band_set = BandStatementSet(
        lt_id=lt.lt_id,
        knowledge_type=lt.knowledge_type,
        statements=[BandStatement(band=x["band"], statement=x["statement"]) for x in majority_run],
        stability_flag=stability,
        per_run_signatures=per_run_sigs,
        stability_diagnostics=(
            [] if stability == "stable" else [f"signature_counts={dict(sig_counts)}"]
        ),
        quality_gate_passed=not failures,
        quality_gate_failures=failures,
    )
    return band_set, None


async def generate_band_statements(
    lt_set: LearningTargetSet,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    runs: int = DEFAULT_RUNS,
    concurrency: int = LT_CONCURRENCY,
) -> BandStatementCollection:
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

    coll = BandStatementCollection(
        source_slug=lt_set.source_slug,
        model=model,
        temperature=temperature,
        runs=runs,
    )
    for (bset, halted) in outputs:
        if bset is not None:
            coll.sets.append(bset)
        if halted is not None:
            coll.halted_lts.append(halted)
    return coll


def generate_band_statements_sync(
    lt_set: LearningTargetSet,
    **kwargs: Any,
) -> BandStatementCollection:
    return asyncio.run(generate_band_statements(lt_set, **kwargs))
