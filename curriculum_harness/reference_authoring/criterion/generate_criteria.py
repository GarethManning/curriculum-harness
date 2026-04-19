"""Type 1/2 criterion (five-level rubric) generator with 3x self-consistency.

For each Type 1 / Type 2 LT, generates a five-level rubric
(No Evidence / Emerging / Developing / Competent / Extending) with
asymmetric word limits per the rubric logic skill, plus typed
prerequisite edges (ontological vs pedagogical + confidence) against
the other Type 1/2 LTs in the same source.

Type 3 LTs NEVER get rubrics — this is an absolute rule. If a Type 3
LT is passed in, the generator raises a ValueError naming the rule.

SELF-CONSISTENCY

Each LT's rubric is generated 3x at temperature 0.3. The stability
signature for a run is the tuple:

    (level_name, word_count_class, dominant_verb_bucket)  for each level,
    plus a "competent_scope_class" derived from the Competent descriptor.

- 3/3 signature match → ``stable``.
- 2/3 majority → ``rubric_unstable`` (majority retained).
- ≤1/3 parseable → halted, flagged ``rubric_unreliable``.

QUALITY GATES (full gate module: ``criterion_gates.py``)

The generator applies the hard structural gates inline at validation
time (five level names present, descriptors non-empty, word limits,
schema correctness). The richer semantic gates — Competent-as-success
(regex + LLM-as-judge), level progression, single-construct
continuity, no-inline-examples, propositional-LT thin-flag — live in
``criterion_gates.run_criterion_gates`` and are applied by the
pipeline after generation.

The Competent-as-success LLM-as-judge is invoked once per rubric
after self-consistency picks the majority run; its verdict is stored
on the Rubric as ``competent_framing_flag`` (pass/fail) with the
judge's rationale.
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections import Counter
from typing import Any

from curriculum_harness.reference_authoring.criterion.criterion_prompts import (
    build_judge_prompt,
    build_system_prompt,
    build_user_prompt,
)
from curriculum_harness.reference_authoring.progression import (
    ProgressionStructure,
)
from curriculum_harness.reference_authoring.types import (
    LearningTarget,
    LearningTargetSet,
    PREREQUISITE_EDGE_CONFIDENCE,
    PREREQUISITE_EDGE_KINDS,
    PrerequisiteEdge,
    RUBRIC_LEVEL_ORDER,
    RUBRIC_LEVEL_WORD_LIMITS,
    Rubric,
    RubricCollection,
    RubricLevel,
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

_TYPE_1_2 = ("Type 1", "Type 2")

_VERB_BUCKETS: dict[str, str] = {
    # recognition / recall
    "identify": "recognise",
    "recognise": "recognise",
    "recognize": "recognise",
    "recall": "recognise",
    "name": "recognise",
    # description / explanation
    "describe": "describe",
    "explain": "describe",
    "communicate": "describe",
    "represent": "describe",
    # comparison / analysis
    "compare": "analyse",
    "contrast": "analyse",
    "analyse": "analyse",
    "analyze": "analyse",
    "distinguish": "analyse",
    "relate": "analyse",
    "interpret": "analyse",
    # evaluation / justification
    "evaluate": "evaluate",
    "justify": "evaluate",
    "critique": "evaluate",
    # procedure / application
    "apply": "apply",
    "use": "apply",
    "solve": "apply",
    "calculate": "apply",
    "compute": "apply",
    "construct": "apply",
    "perform": "apply",
    "demonstrate": "apply",
    "create": "apply",
    "select": "apply",
    "choose": "apply",
}

_OBSERVABLE_VERBS = set(_VERB_BUCKETS.keys())


def _word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z']+", text))


def _word_count_class(n: int, limit: int) -> str:
    # Signature-level bins only. The hard word-limit gate enforces the cap;
    # this function supplies the signature class used by self-consistency.
    # Within-limit variation is noise, not structural disagreement.
    if n == 0:
        return "empty"
    if n > limit:
        return "over_limit"
    return "within_limit"


_INFLECTION_SUFFIXES = ("ies", "ing", "ed", "es", "s", "d")


def _lemmatise(word: str) -> set[str]:
    """Return a small set of candidate lemmas for ``word``.

    Kept in sync with ``criterion_gates._lemmatise`` — the two modules
    MUST agree on what counts as a verb match, or self-consistency will
    see false disagreements where the generator returns ``none`` but
    the gates correctly recognise the inflected form.
    """
    w = word.lower()
    candidates = {w}
    for suf in _INFLECTION_SUFFIXES:
        if len(w) > len(suf) + 2 and w.endswith(suf):
            stem = w[: -len(suf)]
            candidates.add(stem)
            if suf == "ies":
                candidates.add(stem + "y")
            if suf in ("ed", "ing"):
                candidates.add(stem + "e")
    return candidates


def _dominant_verb_bucket(text: str) -> str:
    buckets: Counter[str] = Counter()
    for m in re.finditer(r"[A-Za-z']+", text):
        candidates = _lemmatise(m.group(0))
        for cand in candidates:
            bucket = _VERB_BUCKETS.get(cand)
            if bucket is not None:
                buckets[bucket] += 1
                break
    if not buckets:
        return "none"
    return buckets.most_common(1)[0][0]


def _competent_scope_class(text: str) -> str:
    """Binary bucket: does Competent cite any scope marker at all?

    The specific marker (independence vs transfer vs range vs accuracy)
    shifts across runs as vocabulary noise, not as structural
    disagreement. Only whether a scope marker is present at all is
    stable enough to signature on.
    """
    lower = text.lower()
    scope_cues = (
        " independently", " without prompting", " unprompted",
        " new context", " unfamiliar", " novel", " transfer",
        " across", " in varied", " in different", " range of",
        " accurate", " correctly", " precisely", " with precision",
    )
    return "scoped" if any(k in lower for k in scope_cues) else "unscoped"


def _validate_run(
    obj: dict[str, Any] | None,
    *,
    peer_lt_ids: set[str],
) -> dict[str, Any] | None:
    if not isinstance(obj, dict):
        return None
    levels = obj.get("levels")
    if not isinstance(levels, dict):
        return None
    clean_levels: dict[str, str] = {}
    for name in RUBRIC_LEVEL_ORDER:
        desc = levels.get(name)
        if not isinstance(desc, str):
            return None
        s = desc.strip()
        if not s:
            return None
        wc = _word_count(s)
        limit = RUBRIC_LEVEL_WORD_LIMITS[name]
        if wc == 0 or wc > limit:
            return None
        clean_levels[name] = s

    edges_raw = obj.get("prerequisite_edges", [])
    if not isinstance(edges_raw, list):
        return None
    clean_edges: list[dict[str, str]] = []
    for e in edges_raw:
        if not isinstance(e, dict):
            return None
        from_id = str(e.get("from_lt_id", "")).strip()
        kind = str(e.get("kind", "")).strip()
        conf = str(e.get("confidence", "")).strip().lower()
        rationale = str(e.get("rationale", "")).strip()
        if from_id not in peer_lt_ids:
            return None
        if kind not in PREREQUISITE_EDGE_KINDS:
            return None
        if conf not in PREREQUISITE_EDGE_CONFIDENCE:
            return None
        clean_edges.append(
            {
                "from_lt_id": from_id,
                "kind": kind,
                "confidence": conf,
                "rationale": rationale,
            }
        )
    return {"levels": clean_levels, "prerequisite_edges": clean_edges}


def _signature(parsed: dict[str, Any]) -> tuple[Any, ...]:
    """Structural signature for self-consistency matching.

    Captures, per level, (name, word-count-class, verb-bucket), plus a
    competent-scope class. Does not fingerprint exact wording — two
    runs with minor rewording still match if structure is preserved.
    """
    parts: list[tuple[str, str, str]] = []
    for name in RUBRIC_LEVEL_ORDER:
        desc = parsed["levels"][name]
        parts.append(
            (
                name,
                _word_count_class(_word_count(desc), RUBRIC_LEVEL_WORD_LIMITS[name]),
                _dominant_verb_bucket(desc),
            )
        )
    competent_scope = _competent_scope_class(parsed["levels"]["competent"])
    return tuple(parts) + (("competent_scope", competent_scope),)


async def _one_run(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    peer_lts: list[LearningTarget],
    progression: ProgressionStructure,
    system_prompt: str,
    run_idx: int,
) -> dict[str, Any] | None:
    user_prompt = build_user_prompt(lt=lt, peer_lts=peer_lts, progression=progression)
    label = f"refauth_criterion {lt.lt_id} run{run_idx}"
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
        logger.warning("criterion generation timeout: %s", label)
        return None
    except Exception:  # noqa: BLE001
        logger.exception("criterion generation error: %s", label)
        return None
    parsed = extract_json_object(text)
    validated = _validate_run(parsed, peer_lt_ids={p.lt_id for p in peer_lts})
    if validated is None:
        logger.warning("criterion generation parse/validation failed: %s", label)
    return validated


async def _judge_competent(
    *,
    client: Any,
    model: str,
    lt: LearningTarget,
    competent_descriptor: str,
) -> tuple[str, str]:
    """Return (verdict, rationale). verdict is "pass" or "fail"; "error" on failure."""
    system, user = build_judge_prompt(
        lt_name=lt.lt_name,
        lt_definition=lt.lt_definition,
        competent_descriptor=competent_descriptor,
    )
    label = f"refauth_criterion_judge {lt.lt_id}"
    try:
        text = await haiku_stream_text(
            client,
            model=model,
            max_tokens=400,
            system=system,
            user_blocks=[{"type": "text", "text": user}],
            label=label,
            temperature=0.0,
        )
    except AnthropicCallTimeout:
        logger.warning("competent judge timeout: %s", label)
        return "error", "judge timeout"
    except Exception:  # noqa: BLE001
        logger.exception("competent judge error: %s", label)
        return "error", "judge error"
    parsed = extract_json_object(text)
    if not isinstance(parsed, dict):
        return "error", "judge output not parseable as JSON object"
    verdict = str(parsed.get("verdict", "")).strip().lower()
    rationale = str(parsed.get("rationale", "")).strip()
    if verdict not in ("pass", "fail"):
        return "error", f"judge verdict not pass/fail: {verdict!r}"
    return verdict, rationale


async def _generate_for_lt(
    *,
    client: Any,
    model: str,
    temperature: float,
    lt: LearningTarget,
    peer_lts: list[LearningTarget],
    progression: ProgressionStructure,
    system_prompt: str,
    runs: int,
) -> tuple[Rubric | None, dict[str, Any] | None]:
    if lt.knowledge_type not in _TYPE_1_2:
        raise ValueError(
            f"generate_criteria is Type 1/2 only; got {lt.knowledge_type!r} for "
            f"lt_id={lt.lt_id}. Type 3 LTs NEVER get rubrics — route them to the "
            f"observation-indicator generator instead (absolute rule)."
        )

    coros = [
        _one_run(
            client=client,
            model=model,
            temperature=temperature,
            lt=lt,
            peer_lts=peer_lts,
            progression=progression,
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
            "halt_reason": "rubric_unreliable",
            "diagnostic": f"only {len(valid)}/{runs} runs produced parseable output",
        }

    sig_counts: Counter[Any] = Counter(_signature(r) for r in valid)
    top_sig, top_count = sig_counts.most_common(1)[0]
    if top_count < 2:
        return None, {
            "lt_id": lt.lt_id,
            "lt_name": lt.lt_name,
            "halt_reason": "rubric_unreliable",
            "diagnostic": (
                f"no structural signature reached 2/3 agreement; "
                f"signatures={list(sig_counts)}"
            ),
        }
    majority_run = next(r for r in valid if _signature(r) == top_sig)
    stability = "stable" if top_count == runs else "rubric_unstable"

    per_run_sigs: list[dict[str, Any]] = []
    for idx, r in enumerate(valid, start=1):
        sig = _signature(r)
        per_run_sigs.append(
            {
                "run": idx,
                "signature": [list(x) if isinstance(x, tuple) else x for x in sig],
                "competent_word_count": _word_count(r["levels"]["competent"]),
            }
        )

    levels = [
        RubricLevel(
            name=name,
            descriptor=majority_run["levels"][name],
            word_count=_word_count(majority_run["levels"][name]),
        )
        for name in RUBRIC_LEVEL_ORDER
    ]
    edges = [
        PrerequisiteEdge(
            from_lt_id=e["from_lt_id"],
            kind=e["kind"],
            confidence=e["confidence"],
            rationale=e["rationale"],
        )
        for e in majority_run["prerequisite_edges"]
    ]

    # Competent-as-success judge (one-shot, zero-temperature).
    verdict, rationale = await _judge_competent(
        client=client,
        model=model,
        lt=lt,
        competent_descriptor=majority_run["levels"]["competent"],
    )

    rubric = Rubric(
        lt_id=lt.lt_id,
        knowledge_type=lt.knowledge_type,
        levels=levels,
        prerequisite_edges=edges,
        stability_flag=stability,
        per_run_signatures=per_run_sigs,
        stability_diagnostics=(
            [] if stability == "stable" else [f"signature_counts={dict(sig_counts)}"]
        ),
        quality_gate_passed=True,
        quality_gate_failures=[],
        competent_framing_flag=verdict,
        competent_framing_judge_rationale=rationale,
        propositional_lt_rubric_thin_flag=False,
    )
    return rubric, None


async def generate_criteria(
    lt_set: LearningTargetSet,
    progression: ProgressionStructure,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    runs: int = DEFAULT_RUNS,
    concurrency: int = LT_CONCURRENCY,
) -> RubricCollection:
    """Generate five-level rubrics for every Type 1/2 LT in ``lt_set``.

    Type 3 LTs are silently skipped (they do not get rubrics).
    """
    client = get_async_client()
    sem = asyncio.Semaphore(concurrency)
    system_prompt = build_system_prompt(progression)

    type12 = [lt for lt in lt_set.lts if lt.knowledge_type in _TYPE_1_2]
    # Peer LTs for prerequisite-edge inference: the other Type 1/2 LTs.
    peer_map: dict[str, list[LearningTarget]] = {
        lt.lt_id: [p for p in type12 if p.lt_id != lt.lt_id] for lt in type12
    }

    async def _bounded(lt: LearningTarget):
        async with sem:
            return await _generate_for_lt(
                client=client,
                model=model,
                temperature=temperature,
                lt=lt,
                peer_lts=peer_map[lt.lt_id],
                progression=progression,
                system_prompt=system_prompt,
                runs=runs,
            )

    tasks = [_bounded(lt) for lt in type12]
    outputs = await asyncio.gather(*tasks)

    coll = RubricCollection(
        source_slug=lt_set.source_slug,
        model=model,
        temperature=temperature,
        runs=runs,
    )
    for (rubric, halted) in outputs:
        if rubric is not None:
            coll.rubrics.append(rubric)
        if halted is not None:
            coll.halted_lts.append(halted)
    return coll


def generate_criteria_sync(
    lt_set: LearningTargetSet,
    progression: ProgressionStructure,
    **kwargs: Any,
) -> RubricCollection:
    return asyncio.run(generate_criteria(lt_set, progression, **kwargs))
