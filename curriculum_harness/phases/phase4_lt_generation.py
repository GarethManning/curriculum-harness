"""Phase 4 — learning targets via MCP learning-target-authoring-guide (per KUD item).

## Regeneration loop (Session 3c)

After the initial LT is built and validated, any flag in ``FAIL_SET``
triggers hard-fail regeneration with a bounded retry budget
(``MAX_REGENERATION_RETRIES`` = 3). Each retry prompt carries the prior
attempt's statement and flags, plus an instruction to address those
flags specifically.

### FAIL_SET — what triggers regeneration

Flags that fire regeneration are genuine validation failures per v4.1:
``SOURCE_FAITHFULNESS_FAIL``, ``EXCEEDS_WORD_LIMIT``, ``COMPOUND_TYPE``,
``EMBEDDED_EXAMPLE``, ``DISPOSITION_RUBRIC_ERROR``,
``MISSING_I_CAN_FORMAT``, ``MISSING_LT_STATEMENT``.

Flags that are informational warnings — ``POSSIBLE_COMPOUND``,
``LT_FORMAT_EXPECTATION_MISMATCH``, ``HE_DISPOSITION_INFERRED`` — are
NOT in FAIL_SET. They ship on the LT as-is.

### Budget-exhausted handling

If the 3rd retry still has any FAIL_SET flag, the LT is NOT shipped
as valid. Instead, the source bullet(s) backing that LT go into
``state["human_review_required"]`` with the full retry history so a
human can decide whether the source content itself is the problem.

### Language-detection bypass

``state["source_language"] == "non-en"`` skips regeneration for
``SOURCE_FAITHFULNESS_FAIL`` specifically (other flags still retry).
The English-only matcher cannot repair a Hungarian / other non-English
source mismatch, and burning the retry budget on a flag the matcher
can't fix produces no signal. Those LTs ship with the flag and a
``SOURCE_LANGUAGE_BYPASS`` annotation in the regeneration-event log.

### Adjacent-mechanism declaration — what the regen loop does NOT check

1. **Semantic differentness of retries.** A near-identical retry
   (same text, same flags) burns the retry budget silently. Mitigated
   by a cosine-similarity check between retry N and retry N-1 — if
   similarity >=0.90, a separate ``REGENERATION_NEAR_IDENTICAL`` flag
   is attached and the LT ships to human review without further
   retries.
2. **New flags introduced by a retry.** A retry that fixes flag X
   but introduces flag Y is detected: if retry N's flags contain any
   flag absent from retry N-1's flags, a ``REGENERATION_INTRODUCED_
   NEW_FLAG`` annotation is added to the retry record. Regeneration
   still continues until budget is exhausted or all flags clear.
3. **Source-content adequacy.** If an LT consistently fails the same
   flag across all retries, the underlying source bullet may be
   ill-formed or the flag definition may be wrong. The loop surfaces
   the case rather than papering over it — the source goes to
   ``human_review_required`` instead of shipping a flagged LT.
4. **FAIL_SET membership.** The set is defined in code; it is NOT
   tuned per-run to silence particular flags. Flag frequency is a
   signal, not a nuisance.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from curriculum_harness._anthropic import (
    AnthropicCallTimeout,
    beta_messages_create,
    get_async_client,
    mcp_servers_param,
    mcp_toolset_single_tool,
    response_debug_dump,
    response_text_content,
)
from curriculum_harness.phases.phase3_kud import is_recall_only_know_content
from curriculum_harness.source_faithfulness import (
    SOURCE_FAITHFULNESS_FAIL_FLAG,
    compute_parent_provenance,
    compute_source_provenance,
)
from curriculum_harness.state import DecomposerState
from curriculum_harness.types import (
    HE_DISPOSITION_INFERRED,
    HumanReviewItem,
    KUD,
    KUDItem,
    LearningTarget,
    SONNET_MODEL,
    extract_json_array,
    extract_json_object,
    resolve_lt_statement_format,
)

TOOL_NAME = "learning-target-authoring-guide"

TYPE_FRAMEWORK_FOR_LT = """Learning target types (wording must match the assigned type number for this KUD item):

Type 1 — Hierarchical knowledge. Assessed via criterion-referenced rubric. Criteria describe what was specifically and correctly demonstrated. Standards are relatively well-defined.

Type 2 — Horizontal or perspectival knowledge. Assessed via criterion-referenced rubric. Criteria describe quality of knowledge and reasoning together on a continuum — these cannot be separated in horizontal subjects. Multiple valid interpretations exist; quality is judged on depth and sophistication.

Type 3 — Dispositional knowledge. Assessed primarily via multi-informant observation protocol. A single-point rubric (competent descriptor only) may be appropriate for student self-assessment contexts. Do not generate five-level rubric language for Type 3 LTs.

All three types use criterion-referenced assessment. A compound LT that requires both horizontal knowledge (Type 2) and dispositional enactment (Type 3) should be flagged COMPOUND_TYPE, not silently assigned one type.

This framework is designed for schools generally — not for any specific school. The type system should work whether a school uses grade levels, multi-grade bands, key stages, or any other leveling structure."""

LT_ACTION_RULES_ICAN = """Additional generation rules:
Rule 1 — No "demonstrate understanding" language:
- "Demonstrate understanding" and "show understanding" are not observable.
- Replace with observable actions: constructs, orders, analyses, evaluates, explains, applies, identifies, interprets.
- Never use "understanding" as the primary verb or as the object of "demonstrate".

Rule 2 — No rote recall as a component of a substantive LT:
- If a KUD item contains both a recall element (dates, names, definitions) AND a substantive task, write the LT for the substantive task ONLY.
- If a KUD item is purely recall with no substantive task, skip it entirely — do not generate an LT.
- Treat rote recall as scaffolding, not the target itself.
- Example: recall dates + construct sequences → "I can construct chronological sequences that show cause-effect relationships."

Rule 3 — The statement must lead with a specific observable action verb after the required prefix.
- Vague verbs (understand, know, appreciate) are acceptable only for Type 3 with explicit observational framing.
"""

LT_ACTION_RULES_NEUTRAL = """Additional generation rules:
Rule 1 — No "demonstrate understanding" language; use observable actions (analyses, evaluates, explains, applies, identifies, interprets, describes, compares).
Rule 2 — Same recall vs substantive rule as for I-can mode: write the substantive task only; skip pure recall items.
Rule 3 — Lead with strong observable language appropriate to the output format (see hard rules below).
"""

GCSE_AQA_EXAM_BLOCK = """
GCSE / AQA assessment awareness (this document is an exam specification):
- Prefer command words that match typical AQA History assessments: describe, explain, analyse, evaluate, assess, compare — choose the level that fits the KUD (do not use "evaluate" for a purely descriptive KUD).
- Align demand with how papers reward responses: shorter AO1-style recall/description vs extended AO2/AO3 analysis — match the KUD's assessment_route and knowledge depth.
- Use wording that could plausibly appear in level-marked schemes: specific, evidential, discriminating — avoid vague "understand the topic" phrasing.
- Do not invent mark totals or tariff numbers unless the KUD text cites them.
"""

HE_SUPPLEMENT_MAX = 3
HE_RAW_EXCERPT_CHARS = 60_000
HE_COSINE_DEDUP_THRESHOLD = 0.92

RUBRIC_TERMS = (
    "rubric",
    "criteria",
    "proficient",
    "emerging",
    "level 1",
    "level 2",
    "level 3",
    "level 4",
    "achievement chart",
    "scoring guide",
)

VERB_HINTS = (
    " analyze ",
    " explain ",
    " describe ",
    " compare ",
    " evaluate ",
    " demonstrate ",
    " identify ",
    " interpret ",
    " apply ",
    " create ",
    " solve ",
    " use ",
    " understand ",
    " assess ",
    " revise ",
)

ICAN_PREFIX = "I can "

# Regeneration loop — see module docstring for what triggers retry.
MAX_REGENERATION_RETRIES = 3
REGENERATION_NEAR_IDENTICAL_THRESHOLD = 0.90
REGEN_NEAR_IDENTICAL_FLAG = "REGENERATION_NEAR_IDENTICAL"
REGEN_INTRODUCED_NEW_FLAG = "REGENERATION_INTRODUCED_NEW_FLAG"
SOURCE_LANGUAGE_BYPASS_ANNOTATION = "SOURCE_LANGUAGE_BYPASS"

# Flags in FAIL_SET trigger regeneration. Flags outside FAIL_SET are
# informational warnings and ship on the LT as-is.
FAIL_SET: frozenset[str] = frozenset({
    SOURCE_FAITHFULNESS_FAIL_FLAG,
    "EXCEEDS_WORD_LIMIT",
    "COMPOUND_TYPE",
    "EMBEDDED_EXAMPLE",
    "DISPOSITION_RUBRIC_ERROR",
    "MISSING_I_CAN_FORMAT",
    "MISSING_LT_STATEMENT",
})


def _fail_flags(flags: list[str]) -> list[str]:
    """Return the subset of ``flags`` that are in FAIL_SET, preserving order."""
    return [f for f in flags if f in FAIL_SET]


def _should_bypass_for_language(
    fail_flags_on_lt: list[str], source_language: str
) -> bool:
    """Non-English source ⇒ skip retries when the ONLY failing flag is
    SOURCE_FAITHFULNESS_FAIL. Other failing flags still trigger retry.

    Rationale: the matcher is English-only (see
    `eval/source_evidence_matcher.py` adjacent-mechanism #4). Retrying
    an English LT against non-English bullets cannot repair the flag.
    Other flags (word limit, compound type, etc.) are language-agnostic
    and still warrant retry.
    """
    if source_language != "non-en":
        return False
    return set(fail_flags_on_lt) == {SOURCE_FAITHFULNESS_FAIL_FLAG}


def _compose_retry_instruction(
    prior_statement: str,
    prior_flags: list[str],
    attempt_idx: int,
) -> str:
    """Build the retry-specific instruction block for the LLM prompt.

    ``attempt_idx`` is 1-based for the retry count (attempt 1 is the
    first regeneration attempt; attempt 0 is the initial LT).
    """
    bullet_points = []
    for flag in prior_flags:
        bullet_points.append(f"- {flag}")
    return (
        f"REGENERATION ATTEMPT {attempt_idx} of {MAX_REGENERATION_RETRIES}.\n"
        f"Prior attempt: {prior_statement!r}\n"
        f"Prior attempt failed these validation flags:\n"
        + "\n".join(bullet_points)
        + "\nRewrite the learning target to specifically fix every listed "
          "flag while still being faithful to the KUD element. Do NOT "
          "produce the same statement again — it will be rejected."
    )


def _tokenize_for_cosine(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def cosine_similarity_text(a: str, b: str) -> float:
    """Token-frequency cosine similarity in [0, 1]; stdlib only."""
    ta = _tokenize_for_cosine(a)
    tb = _tokenize_for_cosine(b)
    if not ta or not tb:
        return 0.0
    ca = Counter(ta)
    cb = Counter(tb)
    vocab = set(ca) | set(cb)
    dot = sum(ca.get(w, 0) * cb.get(w, 0) for w in vocab)
    na = math.sqrt(sum(c * c for c in ca.values()))
    nb = math.sqrt(sum(c * c for c in cb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _max_cosine_to_corpus(stmt: str, corpus: list[str]) -> float:
    if not stmt.strip():
        return 0.0
    return max((cosine_similarity_text(stmt, c) for c in corpus if c.strip()), default=0.0)


def _hard_rules_for_format(fmt: str) -> str:
    if fmt == "i_can":
        return (
            f'Hard rules: the statement must begin exactly with {ICAN_PREFIX!r} (capital I, lowercase can, one space); '
            "max 25 words; single construct; no parenthetical examples."
        )
    if fmt == "outcome_statement":
        return (
            "Hard rules: write ONE plain student-facing outcome statement — **no** 'I can' prefix. "
            "Start with an observable verb or short noun phrase (e.g. 'Describes…', 'Explains…', 'Analyses…'). "
            "Max 25 words; single construct; no parenthetical examples."
        )
    if fmt == "competency_descriptor":
        return (
            "Hard rules: write ONE third-person competency-style clause (e.g. 'Uses evidence to…', 'Applies…', 'Demonstrates…'). "
            "**No** 'I can' and **no** first-person. Max 25 words; single construct; no parenthetical examples."
        )
    return _hard_rules_for_format("i_can")


def _action_rules_for_format(fmt: str) -> str:
    return LT_ACTION_RULES_ICAN if fmt == "i_can" else LT_ACTION_RULES_NEUTRAL


def _system_direct_for_format(fmt: str) -> str:
    rules = _hard_rules_for_format(fmt)
    ar = _action_rules_for_format(fmt)
    return f"""You write ONE measurable learning target per request.

{TYPE_FRAMEWORK_FOR_LT}
{ar}

{rules}

Output ONLY JSON: {{"statement": str}}
"""


def _primary_type_from_assessment_route(route: str) -> int:
    r = (route or "").lower()
    if "observation" in r:
        return 3
    if any(x in r for x in ("reasoning", "interpret", "analytical", "judgment", "essay")):
        return 2
    return 2


def _fallback_type_from_route(route: str) -> int:
    r = (route or "").lower()
    if "observation" in r:
        return 3
    if any(x in r for x in ("reasoning", "interpret", "analytical", "judgment", "essay")):
        return 2
    return 1


def _lt_type_and_compound(item: KUDItem) -> tuple[int, bool]:
    kt = (item.knowledge_type or "").strip().lower()
    route = item.assessment_route or ""
    body = f"{item.content or ''} {item.notes or ''}".lower()

    h_hier = "hierarchical" in kt
    h_horiz = "horizontal" in kt
    h_disp = "dispositional" in kt or "disposition" in kt

    horiz_and_disp_tags = h_horiz and h_disp
    horiz_tag_disp_in_body = h_horiz and (
        "dispositional" in body or "disposition" in body or "dispositions" in body
    )
    disp_tag_horiz_in_body = h_disp and (
        "horizontal" in body or "perspectival" in body or "perspective" in body
    )

    if "mixed" in kt or horiz_and_disp_tags or horiz_tag_disp_in_body or disp_tag_horiz_in_body:
        return _primary_type_from_assessment_route(route), True

    if h_hier and h_horiz and not h_disp:
        return 1, False
    if h_hier and h_disp and not h_horiz:
        return _fallback_type_from_route(route), False
    if h_horiz and h_hier and not h_disp:
        return 1, False

    if h_hier and not h_horiz and not h_disp:
        return 1, False
    if h_horiz and not h_hier and not h_disp:
        return 2, False
    if h_disp and not h_hier and not h_horiz:
        return 3, False

    return _fallback_type_from_route(route), False


def _validate_lt(lt: LearningTarget, *, compound_type: bool, fmt: str) -> list[str]:
    flags = list(lt.flags)
    stmt = (lt.statement or "").strip()
    words = stmt.split()
    wc = len(words)
    lt.word_count = wc

    if not stmt:
        flags.append("MISSING_LT_STATEMENT")
    elif fmt == "i_can":
        if not stmt.startswith(ICAN_PREFIX):
            flags.append("MISSING_I_CAN_FORMAT")
    elif fmt == "outcome_statement":
        if stmt.lower().startswith("i can "):
            flags.append("LT_FORMAT_EXPECTATION_MISMATCH")
    elif fmt == "competency_descriptor":
        low = stmt.lower()
        if low.startswith("i can ") or low.startswith("i "):
            flags.append("LT_FORMAT_EXPECTATION_MISMATCH")

    if compound_type:
        flags.append("COMPOUND_TYPE")
    if wc > 25:
        flags.append("EXCEEDS_WORD_LIMIT")
    lower = stmt.lower()
    if fmt == "i_can" and " and " in lower:
        parts = re.split(r"\s+and\s+", lower, maxsplit=1)
        if len(parts) == 2:
            v0 = any(v in f" {parts[0]} " for v in VERB_HINTS)
            v1 = any(v in f" {parts[1]} " for v in VERB_HINTS)
            if v0 and v1:
                flags.append("POSSIBLE_COMPOUND")
    if re.search(r"\([^)]+\)", stmt):
        flags.append("EMBEDDED_EXAMPLE")
    if lt.type == 3:
        rub = any(t in lower for t in RUBRIC_TERMS)
        if rub:
            flags.append("DISPOSITION_RUBRIC_ERROR")
    return list(dict.fromkeys(flags))


async def _direct_lt(kud_line: str, assigned_type: int, fmt: str) -> LearningTarget:
    client = get_async_client()
    system = _system_direct_for_format(fmt)
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": system},
                {
                    "type": "text",
                    "text": (
                        f"KUD element:\n{kud_line}\n"
                        f"Assigned learning target type (from knowledge_type taxonomy): {assigned_type}"
                    ),
                },
            ],
        }],
        label="phase4_sonnet_direct_lt",
    )
    text = response_text_content(msg)
    parsed = extract_json_object(text) or {}
    stmt = str(parsed.get("statement", "")).strip()
    lt = LearningTarget(
        statement=stmt,
        type=assigned_type,
        word_count=len(stmt.split()),
        lt_statement_format=fmt,
    )
    return lt


def _format_kud_line(bucket: str, item: KUDItem) -> str:
    return (
        f"[{bucket}] {item.content}\n"
        f"knowledge_type={item.knowledge_type}; assessment_route={item.assessment_route}\n"
        f"notes={item.notes}"
    )


async def _he_dispositional_supplement(
    *,
    raw_curriculum: str,
    subject: str,
    grade: str,
    jurisdiction: str,
    fmt: str,
    existing_statements: list[str],
) -> list[LearningTarget]:
    excerpt = (raw_curriculum or "")[:HE_RAW_EXCERPT_CHARS].strip()
    if len(excerpt) < 400:
        return []

    subj = subject.strip() or "the course"
    gr = grade.strip() or "this level"
    juris = jurisdiction.strip() or "the institution"
    rules = _hard_rules_for_format(fmt)
    system = (
        "You infer implicit graduate-level dispositions from a higher-education syllabus excerpt. "
        "Dispositions include (examples only): critical judgement, independent scholarship, tolerance of ambiguity, "
        "intellectual humility, sustained inquiry. "
        f"Return ONLY a JSON array of at most {HE_SUPPLEMENT_MAX} objects, each "
        '{"statement": "<single disposition phrased as a learning outcome>"}. '
        "Each must be assessable via multi-informant observation (no exam-style source analysis). "
        f"Subject context: {subj} at {gr} ({juris}).\n"
        f"{rules}"
    )
    client = get_async_client()
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": system},
                {"type": "text", "text": f"Syllabus excerpt:\n\n{excerpt}"},
            ],
        }],
        label="phase4_he_disposition_supplement",
    )
    text = response_text_content(msg)
    arr = extract_json_array(text) or []
    out: list[LearningTarget] = []
    corpus = list(existing_statements)
    for item in arr:
        if len(out) >= HE_SUPPLEMENT_MAX:
            break
        if not isinstance(item, dict):
            continue
        stmt = str(item.get("statement", "")).strip()
        if not stmt:
            continue
        if _max_cosine_to_corpus(stmt, corpus) >= HE_COSINE_DEDUP_THRESHOLD:
            continue
        lt = LearningTarget(
            statement=stmt,
            type=3,
            knowledge_type="dispositional",
            assessment_route="observation_protocol",
            kud_source="phase4:he_disposition_inference",
            word_count=len(stmt.split()),
            flags=[HE_DISPOSITION_INFERRED],
            lt_statement_format=fmt,
        )
        lt.flags = _validate_lt(lt, compound_type=False, fmt=fmt)
        if HE_DISPOSITION_INFERRED not in lt.flags:
            lt.flags.insert(0, HE_DISPOSITION_INFERRED)
        out.append(lt)
        corpus.append(stmt)
    return out


def _build_initial_instruction(
    assigned_type: int,
    fmt: str,
    exam_addon: str,
    action_block: str,
    hard: str,
    arch_summary: str,
) -> str:
    return (
        f"Call `{TOOL_NAME}` to author ONE learning target from this KUD element.\n\n"
        f"{TYPE_FRAMEWORK_FOR_LT}\n\n"
        f"{action_block}\n\n"
        f"{hard}\n"
        f"{exam_addon}\n"
        f"This element has **assigned type {assigned_type}** from the KUD `knowledge_type` field — "
        "generate wording consistent with that type only (do not choose a different type from the wording).\n"
        f"Architecture context (summary): {arch_summary[:4000]}\n"
        'Then output ONLY JSON: {"statement": str}'
    )


async def _one_llm_attempt(
    *,
    instruction: str,
    kud_line: str,
    bucket: str,
    assigned_type: int,
    fmt: str,
    mcp_url: str,
    mcp_name: str,
    client: Any,
) -> tuple[str, list[HumanReviewItem], list[str]]:
    """Single LLM call (MCP first, direct Sonnet fallback).

    Returns ``(statement, review_items_to_append, error_lines)``. An
    empty statement with no review items indicates a clean skip
    (e.g. initial call returned an explicit ``skip_rote`` sentinel).
    Empty statement with a review item indicates a catastrophic failure
    the caller should treat as "no LT for this item".
    """
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": instruction},
            {"type": "text", "text": kud_line},
        ],
    }]
    resp: Any = None
    stmt = ""
    reviews: list[HumanReviewItem] = []
    errors_out: list[str] = []
    try:
        resp = await beta_messages_create(
            client,
            model=SONNET_MODEL,
            max_tokens=2048,
            messages=messages,
            label=f"phase4_mcp_lt_{bucket}",
            mcp_servers=mcp_servers_param(mcp_url, mcp_name),
            tools=[mcp_toolset_single_tool(mcp_name, TOOL_NAME)],
        )
        text = response_text_content(resp)
        parsed = extract_json_object(text) or {}
        stmt = str(parsed.get("statement", "")).strip()
    except AnthropicCallTimeout:
        errors_out.append(
            f"phase4: timeout for KUD item {bucket}: {kud_line[:80]} (trying direct Sonnet)"
        )
        try:
            fb = await _direct_lt(kud_line, assigned_type, fmt)
            stmt = fb.statement
        except Exception:
            reviews.append(
                HumanReviewItem(
                    item_type="phase4_timeout",
                    summary=f"{bucket}: {kud_line[:120]}",
                    decision_needed="Re-run or author LT manually.",
                )
            )
            return "", reviews, errors_out
    except Exception as exc:
        raw_dump = response_debug_dump(resp) if resp is not None else str(exc)
        reviews.append(
            HumanReviewItem(
                item_type="phase4_mcp",
                summary=f"{bucket}: {exc}"[:500],
                decision_needed="MCP LT failure; attempting direct Sonnet.",
            )
        )
        reviews.append(
            HumanReviewItem(
                item_type="phase4_mcp_raw",
                summary="raw (truncated)",
                decision_needed=raw_dump[:6000],
            )
        )
        fb = await _direct_lt(kud_line, assigned_type, fmt)
        stmt = fb.statement

    if not stmt:
        fb = await _direct_lt(kud_line, assigned_type, fmt)
        stmt = fb.statement
    return stmt, reviews, errors_out


def _finalise_lt(
    *,
    stmt: str,
    assigned_type: int,
    compound: bool,
    fmt: str,
    item: KUDItem,
    source_label: str,
    kud_parents: list[dict],
    source_bullets: list[dict],
) -> LearningTarget:
    """Build a LearningTarget from ``stmt`` and attach validation flags
    + provenance (surface flags from `_validate_lt`, source-faithfulness
    flag from the `source_bullets` corpus, kud / source provenance).
    Returns the finalised LT.
    """
    lt = LearningTarget(
        statement=stmt,
        type=assigned_type,
        knowledge_type=item.knowledge_type,
        assessment_route=item.assessment_route,
        kud_source=source_label,
        word_count=len(stmt.split()),
        lt_statement_format=fmt,
    )
    lt.flags = _validate_lt(lt, compound_type=compound, fmt=fmt)
    kud_prov, _ = compute_parent_provenance(stmt, kud_parents, top_k=1)
    src_prov, src_passed = compute_source_provenance(stmt, source_bullets)
    lt.kud_provenance = kud_prov
    lt.source_provenance = src_prov
    if not src_passed and source_bullets:
        if SOURCE_FAITHFULNESS_FAIL_FLAG not in lt.flags:
            lt.flags.append(SOURCE_FAITHFULNESS_FAIL_FLAG)
    return lt


async def _generate_with_regen_loop(
    *,
    bucket: str,
    item: KUDItem,
    assigned_type: int,
    compound: bool,
    fmt: str,
    exam_addon: str,
    action_block: str,
    hard: str,
    arch_summary: str,
    mcp_url: str,
    mcp_name: str,
    client: Any,
    kud_parents: list[dict],
    source_bullets: list[dict],
    source_language: str,
) -> tuple[
    LearningTarget | None,
    list[HumanReviewItem],
    list[str],
    dict[str, Any] | None,
    dict[str, Any] | None,
]:
    """Generate ONE LT with bounded regeneration on FAIL_SET flags.

    Returns (lt, reviews, errors, regen_event, human_review_entry).
    See `_regenerate_loop` module docstring for the state machine.
    """
    kud_line = _format_kud_line(bucket, item)
    source_label = f"{bucket}: {item.content[:120]}"
    base_instruction = _build_initial_instruction(
        assigned_type, fmt, exam_addon, action_block, hard, arch_summary
    )

    all_reviews: list[HumanReviewItem] = []
    all_errors: list[str] = []
    attempts: list[dict[str, Any]] = []
    lt: LearningTarget | None = None
    event_annotations: list[str] = []

    for attempt_idx in range(MAX_REGENERATION_RETRIES + 1):
        if attempt_idx == 0:
            instruction = base_instruction
        else:
            prior = attempts[-1]
            instruction = (
                f"{base_instruction}\n\n"
                + _compose_retry_instruction(
                    prior_statement=prior["statement"],
                    prior_flags=prior["fail_flags"],
                    attempt_idx=attempt_idx,
                )
            )

        stmt, reviews, errors_out = await _one_llm_attempt(
            instruction=instruction,
            kud_line=kud_line,
            bucket=bucket,
            assigned_type=assigned_type,
            fmt=fmt,
            mcp_url=mcp_url,
            mcp_name=mcp_name,
            client=client,
        )
        all_reviews.extend(reviews)
        all_errors.extend(errors_out)

        if not stmt:
            # Catastrophic LLM failure; caller treats as "no LT for this item".
            return None, all_reviews, all_errors, None, None

        s_low = stmt.lower().strip()
        if attempt_idx == 0 and (
            "skip_rote" in s_low or s_low in ("skip", "skip_rote_recall_only")
        ):
            return None, all_reviews, all_errors, None, None

        candidate = _finalise_lt(
            stmt=stmt,
            assigned_type=assigned_type,
            compound=compound,
            fmt=fmt,
            item=item,
            source_label=source_label,
            kud_parents=kud_parents,
            source_bullets=source_bullets,
        )
        fail_flags_this_attempt = _fail_flags(candidate.flags)

        attempt_annotations: list[str] = []
        similarity_to_prev: float | None = None
        if attempt_idx > 0:
            similarity_to_prev = cosine_similarity_text(
                attempts[-1]["statement"], stmt
            )
            if similarity_to_prev >= REGENERATION_NEAR_IDENTICAL_THRESHOLD:
                attempt_annotations.append(REGEN_NEAR_IDENTICAL_FLAG)
            prior_flag_set = set(attempts[-1]["fail_flags"])
            new_fail_flags = [
                f for f in fail_flags_this_attempt if f not in prior_flag_set
            ]
            if new_fail_flags:
                attempt_annotations.append(REGEN_INTRODUCED_NEW_FLAG)

        attempts.append({
            "attempt": attempt_idx,
            "statement": stmt,
            "flags": list(candidate.flags),
            "fail_flags": fail_flags_this_attempt,
            "annotations": attempt_annotations,
            "similarity_to_prev": (
                round(similarity_to_prev, 4)
                if similarity_to_prev is not None
                else None
            ),
        })
        lt = candidate

        if not fail_flags_this_attempt:
            break
        if _should_bypass_for_language(
            fail_flags_this_attempt, source_language
        ):
            event_annotations.append(SOURCE_LANGUAGE_BYPASS_ANNOTATION)
            break
        if REGEN_NEAR_IDENTICAL_FLAG in attempt_annotations:
            # Further retries on the same text burn the budget silently.
            break
        if attempt_idx == MAX_REGENERATION_RETRIES:
            break

    final_fail_flags: list[str] = _fail_flags(lt.flags) if lt else []
    outcome: str
    if not final_fail_flags:
        outcome = (
            "success@initial" if len(attempts) == 1
            else f"success@retry_{len(attempts) - 1}"
        )
    elif SOURCE_LANGUAGE_BYPASS_ANNOTATION in event_annotations:
        outcome = "language_bypass_ship_flagged"
    elif (
        attempts
        and REGEN_NEAR_IDENTICAL_FLAG in (attempts[-1].get("annotations") or [])
    ):
        outcome = "near_identical_retry_abort"
    else:
        outcome = "exhausted_retries"

    event: dict[str, Any] | None = None
    if len(attempts) > 1 or final_fail_flags:
        event = {
            "source_label": source_label,
            "bucket": bucket,
            "kud_content": item.content,
            "source_bullet_ids": list(
                getattr(item, "source_bullet_ids", []) or []
            ),
            "attempts": attempts,
            "outcome": outcome,
            "annotations": list(dict.fromkeys(event_annotations)),
        }

    human_review_entry: dict[str, Any] | None = None
    if final_fail_flags and outcome in (
        "exhausted_retries",
        "near_identical_retry_abort",
    ):
        human_review_entry = {
            "source_label": source_label,
            "kud_content": item.content,
            "source_bullet_ids": list(
                getattr(item, "source_bullet_ids", []) or []
            ),
            "final_fail_flags": final_fail_flags,
            "outcome": outcome,
            "attempt_count": len(attempts),
            "attempts": attempts,
        }

    return lt, all_reviews, all_errors, event, human_review_entry


async def phase4_lt_generation(state: DecomposerState) -> dict[str, Any]:
    errs = list(state.get("errors") or [])
    review_dicts = list(state.get("human_review_queue") or [])

    kud = KUD.from_dict(state.get("kud"))
    arch = state.get("architecture_diagnosis") or {}
    profile = dict(state.get("curriculum_profile") or {})
    fmt = resolve_lt_statement_format(profile)
    doc_fam = str(profile.get("document_family", "")).strip().lower()
    source_language = str(state.get("source_language") or "en")

    if not kud.all_items():
        errs.append("phase4: skipped — empty KUD")
        return {
            "current_phase": "phase4:skipped",
            "errors": errs,
            "learning_targets": [],
            "regeneration_events": [],
            "human_review_required": [],
        }

    mcp_url = state.get("mcp_server_url") or ""
    mcp_name = state.get("mcp_server_name") or "claude-education-skills"
    arch_summary = str(arch)[:12000]
    # NOTE: GCSE_AQA_EXAM_BLOCK is still attached on any
    # exam_specification profile. VALIDITY.md foundation moment 3
    # (validate_exam_block_scope) tracks the AQA-specific scoping bug;
    # Session 3c does not change that gate's scope.
    exam_addon = GCSE_AQA_EXAM_BLOCK if doc_fam == "exam_specification" else ""
    hard = _hard_rules_for_format(fmt)
    action_block = _action_rules_for_format(fmt)

    # Session 3d — Phase 4's per-LT faithfulness check must run against
    # coverage-relevant bullets only (specific_expectation +
    # overall_expectation). Illustrative bullets (sample_question,
    # teacher_prompt), front_matter, other, and cross_grade extraction
    # errors are structural noise: an LT that only "matches" a sample
    # question or front-matter line is not demonstrably faithful. This
    # mirrors the gate-level filter applied in `_run_loader.py`.
    # Backwards-compat: bullets without a bullet_type field (pre-Session-
    # 3d runs) are treated as coverage-relevant so legacy behaviour is
    # preserved.
    _raw_bullets = list(state.get("source_bullets") or [])
    _COVERAGE_RELEVANT_BTYPES = {
        "specific_expectation",
        "overall_expectation",
    }
    _has_btype_field = any(("bullet_type" in b) for b in _raw_bullets)
    if _has_btype_field:
        # Determine whether the bullet_type field uses the Session-3d
        # semantic enum or the pre-Session-3d detector name. If any
        # bullet carries a semantic value, treat the whole set as
        # Session-3d shape and filter.
        _semantic_shape = any(
            (b.get("bullet_type") in _COVERAGE_RELEVANT_BTYPES)
            or b.get("bullet_type")
            in {"sample_question", "teacher_prompt", "cross_grade", "front_matter", "other"}
            for b in _raw_bullets
        )
        if _semantic_shape:
            source_bullets = [
                b for b in _raw_bullets
                if b.get("bullet_type") in _COVERAGE_RELEVANT_BTYPES
            ]
        else:
            source_bullets = _raw_bullets
    else:
        source_bullets = _raw_bullets
    if _raw_bullets and not source_bullets:
        # Filter produced an empty set from a non-empty raw list. Fall
        # back to the full list so Phase 4 does not run blind. The log
        # line calls out the condition so the run report surfaces it.
        errs.append(
            "phase4: bullet_type filter collapsed source_bullets to zero "
            f"coverage-relevant bullets from {len(_raw_bullets)} total — "
            "falling back to unfiltered corpus; Phase 1 scoping likely "
            "missed the target grade."
        )
        source_bullets = _raw_bullets
    kud_parents = [
        {"id": f"{bucket}[{idx}]", "content": it.content}
        for idx, (bucket, it) in enumerate(kud.all_items())
    ]

    targets: list[dict[str, Any]] = []
    regeneration_events: list[dict[str, Any]] = []
    human_review_required: list[dict[str, Any]] = []
    client = get_async_client()

    for bucket, item in kud.all_items():
        if bucket == "know" and is_recall_only_know_content(item.content):
            continue
        assigned_type, compound = _lt_type_and_compound(item)

        lt, reviews, errors_out, event, hr_entry = await _generate_with_regen_loop(
            bucket=bucket,
            item=item,
            assigned_type=assigned_type,
            compound=compound,
            fmt=fmt,
            exam_addon=exam_addon,
            action_block=action_block,
            hard=hard,
            arch_summary=arch_summary,
            mcp_url=mcp_url,
            mcp_name=mcp_name,
            client=client,
            kud_parents=kud_parents,
            source_bullets=source_bullets,
            source_language=source_language,
        )
        review_dicts.extend(r.to_dict() for r in reviews)
        errs.extend(errors_out)
        if event is not None:
            regeneration_events.append(event)
        if hr_entry is not None:
            human_review_required.append(hr_entry)
        if lt is None:
            continue
        targets.append(lt.to_dict())

    if doc_fam == "higher_ed_syllabus":
        try:
            existing_st = [str(t.get("statement", "")) for t in targets]
            extras = await _he_dispositional_supplement(
                raw_curriculum=str(state.get("raw_curriculum") or ""),
                subject=str(state.get("subject") or ""),
                grade=str(state.get("grade") or ""),
                jurisdiction=str(state.get("jurisdiction") or ""),
                fmt=fmt,
                existing_statements=existing_st,
            )
            for lt in extras:
                # HE dispositional supplements are synthesised from
                # the raw syllabus (no single source bullet), so they
                # ship as best-effort provenance without regeneration.
                stmt = lt.statement
                kud_prov, _ = compute_parent_provenance(stmt, kud_parents, top_k=1)
                src_prov, _src_passed = compute_source_provenance(
                    stmt, source_bullets
                )
                lt.kud_provenance = kud_prov
                lt.source_provenance = src_prov
                targets.append(lt.to_dict())
        except Exception as exc:
            errs.append(f"phase4: HE disposition supplement failed: {exc}")

    phase4_flagged = sum(
        1
        for t in targets
        if SOURCE_FAITHFULNESS_FAIL_FLAG in (t.get("flags") or [])
    )
    if not source_bullets:
        errs.append(
            "phase4: no source_bullets corpus available — "
            "SOURCE_FAITHFULNESS_FAIL flags suppressed for this run"
        )

    return {
        "current_phase": "phase4:complete",
        "errors": errs,
        "human_review_queue": review_dicts,
        "learning_targets": targets,
        "phase4_faithfulness_flagged_count": phase4_flagged,
        "regeneration_events": regeneration_events,
        "human_review_required": human_review_required,
    }
