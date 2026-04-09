"""Phase 4 — learning targets via MCP learning-target-authoring-guide (per KUD item)."""

from __future__ import annotations

import re
from typing import Any

from kaku_decomposer._anthropic import (
    AnthropicCallTimeout,
    beta_messages_create,
    get_async_client,
    mcp_servers_param,
    mcp_toolset_single_tool,
    response_debug_dump,
    response_text_content,
)
from kaku_decomposer.phases.phase3_kud import is_recall_only_know_content
from kaku_decomposer.state import DecomposerState
from kaku_decomposer.types import (
    HumanReviewItem,
    KUD,
    KUDItem,
    LearningTarget,
    SONNET_MODEL,
    extract_json_object,
)

TOOL_NAME = "learning-target-authoring-guide"

TYPE_FRAMEWORK_FOR_LT = """Learning target types (wording must match the assigned type number for this KUD item):

Type 1 — Hierarchical knowledge. Assessed via criterion-referenced rubric. Criteria describe what was specifically and correctly demonstrated. Standards are relatively well-defined.

Type 2 — Horizontal or perspectival knowledge. Assessed via criterion-referenced rubric. Criteria describe quality of knowledge and reasoning together on a continuum — these cannot be separated in horizontal subjects. Multiple valid interpretations exist; quality is judged on depth and sophistication.

Type 3 — Dispositional knowledge. Assessed primarily via multi-informant observation protocol. A single-point rubric (competent descriptor only) may be appropriate for student self-assessment contexts. Do not generate five-level rubric language for Type 3 LTs.

All three types use criterion-referenced assessment. A compound LT that requires both horizontal knowledge (Type 2) and dispositional enactment (Type 3) should be flagged COMPOUND_TYPE, not silently assigned one type.

This framework is designed for schools generally — not for any specific school. The type system should work whether a school uses grade levels, multi-grade bands, key stages, or any other leveling structure."""

LT_ACTION_RULES = """Additional generation rules:
Rule 1 — No "demonstrate understanding" language:
- "Demonstrate understanding" and "show understanding" are not observable.
- Replace with observable actions: constructs, orders, analyses, evaluates, explains, applies, identifies, interprets.
- Never use "understanding" as the primary verb or as the object of "demonstrate".

Rule 2 — No rote recall as a component of a substantive LT:
- If a KUD item contains both a recall element (dates, names, definitions) AND a substantive task, write the LT for the substantive task ONLY.
- If the KUD item is purely recall with no substantive task, skip it entirely — do not generate an LT.
- If a KUD item mixes rote recall (dates, definitions, names) with a substantive task (sequence, analyse, construct, evaluate), write only the substantive task LT.
- Treat rote recall as scaffolding, not the target itself.
- Example transformation intent: "recall historical dates and construct chronological sequences" -> "I can construct chronological sequences that show cause-effect relationships."

Rule 3 — Action verb must be the primary verb:
- The I-can statement must lead with a specific observable action verb.
- Vague verbs (understand, know, appreciate, recognise, be aware of) are acceptable only for Type 3 dispositional LTs with explicit observational framing.
"""

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


def _primary_type_from_assessment_route(route: str) -> int:
    """When COMPOUND_TYPE (horizontal + dispositional), pick primary type from route emphasis."""
    r = (route or "").lower()
    if "observation" in r:
        return 3
    if any(x in r for x in ("reasoning", "interpret", "analytical", "judgment", "essay")):
        return 2
    return 2


def _fallback_type_from_route(route: str) -> int:
    """When knowledge_type is missing or unrecognized, infer type 1/2/3 from assessment_route only."""
    r = (route or "").lower()
    if "observation" in r:
        return 3
    if any(x in r for x in ("reasoning", "interpret", "analytical", "judgment", "essay")):
        return 2
    return 1


def _lt_type_and_compound(item: KUDItem) -> tuple[int, bool]:
    """
    Map KUD knowledge_type → LT type (1/2/3). COMPOUND_TYPE flag when horizontal + dispositional
    blur; primary type comes from assessment_route emphasis.
    """
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


def _validate_lt(lt: LearningTarget, *, compound_type: bool) -> list[str]:
    flags = list(lt.flags)
    stmt = (lt.statement or "").strip()
    words = stmt.split()
    wc = len(words)
    lt.word_count = wc

    if not stmt.startswith(ICAN_PREFIX):
        flags.append("MISSING_I_CAN_FORMAT")
    if compound_type:
        flags.append("COMPOUND_TYPE")
    if wc > 25:
        flags.append("EXCEEDS_WORD_LIMIT")
    lower = stmt.lower()
    if " and " in lower:
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


SYSTEM_DIRECT = f"""You write ONE measurable student-facing learning target per request.

{TYPE_FRAMEWORK_FOR_LT}
{LT_ACTION_RULES}

Hard rules:
- The first characters of the statement must be exactly: {ICAN_PREFIX!r} (capital I, lowercase can, one space).
- Max 25 words; single construct; no parenthetical examples.

Output ONLY JSON: {{"statement": str}}
"""


async def _direct_lt(kud_line: str, assigned_type: int) -> LearningTarget:
    client = get_async_client()
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM_DIRECT},
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
    )
    return lt


def _format_kud_line(bucket: str, item: KUDItem) -> str:
    return (
        f"[{bucket}] {item.content}\n"
        f"knowledge_type={item.knowledge_type}; assessment_route={item.assessment_route}\n"
        f"notes={item.notes}"
    )


async def phase4_lt_generation(state: DecomposerState) -> dict[str, Any]:
    errs = list(state.get("errors") or [])
    review_dicts = list(state.get("human_review_queue") or [])

    kud = KUD.from_dict(state.get("kud"))
    arch = state.get("architecture_diagnosis") or {}
    if not kud.all_items():
        errs.append("phase4: skipped — empty KUD")
        return {
            "current_phase": "phase4:skipped",
            "errors": errs,
            "learning_targets": [],
        }

    mcp_url = state.get("mcp_server_url") or ""
    mcp_name = state.get("mcp_server_name") or "claude-education-skills"
    arch_summary = str(arch)[:12000]

    targets: list[dict[str, Any]] = []
    client = get_async_client()

    for bucket, item in kud.all_items():
        if bucket == "know" and is_recall_only_know_content(item.content):
            continue
        assigned_type, compound = _lt_type_and_compound(item)
        kud_line = _format_kud_line(bucket, item)
        instruction = (
            f"Call `{TOOL_NAME}` to author ONE learning target from this KUD element.\n\n"
            f"{TYPE_FRAMEWORK_FOR_LT}\n\n"
            f"{LT_ACTION_RULES}\n\n"
            'Hard rules: the statement must begin exactly with "I can " (capital I, lowercase can, one space); '
            "max 25 words; single construct; no parenthetical examples.\n"
            f"This element has **assigned type {assigned_type}** from the KUD `knowledge_type` field — "
            "generate wording consistent with that type only (do not choose a different type from the wording).\n"
            f"Architecture context (summary): {arch_summary[:4000]}\n"
            'Then output ONLY JSON: {"statement": str}'
        )
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": instruction},
                {"type": "text", "text": kud_line},
            ],
        }]
        resp: Any = None
        stmt = ""
        source = f"{bucket}: {item.content[:120]}"

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
            errs.append(f"phase4: timeout for KUD item {source[:80]} (trying direct Sonnet)")
            try:
                fb = await _direct_lt(kud_line, assigned_type)
                stmt = fb.statement
            except Exception:
                review_dicts.append(
                    HumanReviewItem(
                        item_type="phase4_timeout",
                        summary=source,
                        decision_needed="Re-run or author LT manually.",
                    ).to_dict(),
                )
                continue
        except Exception as exc:
            raw_dump = response_debug_dump(resp) if resp is not None else str(exc)
            review_dicts.append(
                HumanReviewItem(
                    item_type="phase4_mcp",
                    summary=f"{source}: {exc}"[:500],
                    decision_needed="MCP LT failure; attempting direct Sonnet.",
                ).to_dict(),
            )
            review_dicts.append(
                HumanReviewItem(
                    item_type="phase4_mcp_raw",
                    summary="raw (truncated)",
                    decision_needed=raw_dump[:6000],
                ).to_dict(),
            )
            fb = await _direct_lt(kud_line, assigned_type)
            stmt = fb.statement

        if not stmt:
            fb = await _direct_lt(kud_line, assigned_type)
            stmt = fb.statement

        s_low = stmt.lower().strip()
        if "skip_rote" in s_low or s_low in ("skip", "skip_rote_recall_only"):
            continue

        lt = LearningTarget(
            statement=stmt,
            type=assigned_type,
            knowledge_type=item.knowledge_type,
            assessment_route=item.assessment_route,
            kud_source=source,
            word_count=len(stmt.split()),
        )
        lt.flags = _validate_lt(lt, compound_type=compound)
        targets.append(lt.to_dict())

    return {
        "current_phase": "phase4:complete",
        "errors": errs,
        "human_review_queue": review_dicts,
        "learning_targets": targets,
    }
