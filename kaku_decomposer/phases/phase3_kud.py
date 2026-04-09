"""Phase 3 — KUD mapping (Sonnet + MCP kud-knowledge-type-mapper)."""

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
from kaku_decomposer.state import DecomposerState
from kaku_decomposer.types import (
    HumanReviewItem,
    KUD,
    KUDItem,
    SONNET_MODEL,
    extract_json_object,
)

TOOL_NAME = "kud-knowledge-type-mapper"

_RECALL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdates?\s+of\b", re.IGNORECASE),
    re.compile(r"\bkey\s+dates?\b", re.IGNORECASE),
    re.compile(r"\bkey\s+events?\b", re.IGNORECASE),
    re.compile(r"\bnames?\s+of\b", re.IGNORECASE),
    re.compile(r"\bdefinition(?:s)?\s+of\b", re.IGNORECASE),
    re.compile(r"\bkey\s+events?\s+and\s+dates?\b", re.IGNORECASE),
    re.compile(r"\bhistorical\s+dates?\b", re.IGNORECASE),
    re.compile(r"\bfactual\s+recall\b", re.IGNORECASE),
    re.compile(r"\bvocabulary\b", re.IGNORECASE),
)

_SUBSTANTIVE = re.compile(
    r"\b(analy[sz]e|evaluate|interpret|compare|apply|construct|inquiry|framework|"
    r"perspective|significance|continuity|change|cause|consequence|synthes|argu|judg)\b",
    re.IGNORECASE,
)


def is_recall_only_know_content(content: str) -> bool:
    """True if know[] item is recall-only listing (dates, names, definitions) without substantive task."""
    t = (content or "").strip()
    if not t:
        return False
    if _SUBSTANTIVE.search(t):
        return False
    return any(p.search(t) for p in _RECALL_PATTERNS)


def _filter_recall_only_know(kud: KUD) -> tuple[KUD, int]:
    kept: list[KUDItem] = []
    removed = 0
    for item in kud.know:
        if is_recall_only_know_content(item.content):
            removed += 1
        else:
            kept.append(item)
    kud.know = kept
    return kud, removed


SYSTEM_DIRECT = """You map curriculum expectations into KUD lists. Output ONLY valid JSON:
{
  "know": [{"content": str, "knowledge_type": "hierarchical"|"horizontal"|"dispositional",
            "assessment_route": "rubric_criterion"|"rubric_reasoning"|"observation_protocol", "notes": str}],
  "understand": [same shape],
  "do_skills": [same shape],
  "do_dispositions": [same shape]
}
Tags must align with the architecture diagnosis provided. No markdown."""


async def _direct_sonnet_kud(
    raw_curriculum: str,
    arch_summary: str,
) -> KUD:
    client = get_async_client()
    body = f"Architecture diagnosis (JSON):\n{arch_summary}\n\nCurriculum:\n{raw_curriculum[:95000]}"
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=16384,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM_DIRECT},
                {"type": "text", "text": body},
            ],
        }],
        label="phase3_sonnet_direct_kud",
    )
    text = response_text_content(msg)
    parsed = extract_json_object(text)
    if parsed:
        return KUD.from_dict(parsed)
    return KUD()


async def phase3_kud(state: DecomposerState) -> dict[str, Any]:
    errs = list(state.get("errors") or [])
    review_dicts = list(state.get("human_review_queue") or [])

    raw = state.get("raw_curriculum") or ""
    arch = state.get("architecture_diagnosis") or {}
    if not raw.strip():
        errs.append("phase3: skipped — empty raw_curriculum")
        return {
            "current_phase": "phase3:skipped",
            "errors": errs,
            "kud": KUD().to_dict(),
            "recall_filtered_count": 0,
        }

    mcp_url = state.get("mcp_server_url") or ""
    mcp_name = state.get("mcp_server_name") or "claude-education-skills"
    arch_text = str(arch)[:20000]

    instruction = (
        f"Invoke `{TOOL_NAME}` using the curriculum text and this architecture diagnosis:\n"
        f"{arch_text}\n\n"
        "After tool results, reply with ONLY a JSON object for know, understand, do_skills, "
        "do_dispositions arrays (items with content, knowledge_type, assessment_route, notes)."
    )

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": instruction},
            {"type": "text", "text": f"Curriculum text:\n\n{raw[:100000]}"},
        ],
    }]

    kud = KUD()
    used_mcp = False
    resp: Any = None

    try:
        client = get_async_client()
        resp = await beta_messages_create(
            client,
            model=SONNET_MODEL,
            max_tokens=16384,
            messages=messages,
            label="phase3_mcp_kud",
            mcp_servers=mcp_servers_param(mcp_url, mcp_name),
            tools=[mcp_toolset_single_tool(mcp_name, TOOL_NAME)],
        )
        used_mcp = True
        text = response_text_content(resp)
        parsed = extract_json_object(text)
        if parsed:
            kud = KUD.from_dict(parsed)
        else:
            raise ValueError("no_json_in_mcp_response")
    except AnthropicCallTimeout:
        errs.append("phase3: API timeout after 240s")
        return {
            "current_phase": "phase3:timeout",
            "errors": errs,
            "human_review_queue": review_dicts,
            "kud": KUD().to_dict(),
            "recall_filtered_count": 0,
        }
    except Exception as exc:
        raw_dump = response_debug_dump(resp) if resp is not None else str(exc)
        err_line = f"phase3: MCP/tools failed: {exc}"
        errs.append(err_line)
        review_dicts.append(
            HumanReviewItem(
                item_type="phase3_mcp",
                summary=err_line[:500],
                decision_needed="Review MCP failure; fallback JSON follows in pipeline output.",
            ).to_dict(),
        )
        review_dicts.append(
            HumanReviewItem(
                item_type="phase3_mcp_raw",
                summary="MCP response / error (truncated)",
                decision_needed=raw_dump[:8000],
            ).to_dict(),
        )
        kud = await _direct_sonnet_kud(raw, arch_text)

    kud, recall_filtered_count = _filter_recall_only_know(kud)

    return {
        "current_phase": "phase3:complete" if used_mcp else "phase3:fallback",
        "errors": errs,
        "human_review_queue": review_dicts,
        "kud": kud.to_dict(),
        "recall_filtered_count": recall_filtered_count,
    }
