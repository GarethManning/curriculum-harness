"""Phase 2 — architecture diagnosis (Sonnet + MCP curriculum-knowledge-architecture-designer)."""

from __future__ import annotations

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
    ArchitectureDiagnosis,
    HumanReviewItem,
    SONNET_MODEL,
    extract_json_object,
)

TOOL_NAME = "curriculum-knowledge-architecture-designer"

SYSTEM_DIRECT = """You are a curriculum architecture analyst. Without external tools, read the curriculum \
and output ONLY valid JSON matching this shape:
{
  "architecture_type": "hierarchical" | "horizontal" | "mixed",
  "proportions": {"hierarchical": float, "horizontal": float, "dispositional": float},
  "hierarchical_elements": [string],
  "horizontal_elements": [string],
  "dispositional_elements": [string],
  "structural_flaw": string,
  "auto_assessable_pct": float
}
Use evidence from the document. No markdown outside the JSON object."""


async def _direct_sonnet_diagnosis(raw_curriculum: str) -> ArchitectureDiagnosis:
    client = get_async_client()
    excerpt = raw_curriculum[:100000]
    msg = await beta_messages_create(
        client,
        model=SONNET_MODEL,
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM_DIRECT},
                {"type": "text", "text": f"Curriculum text:\n\n{excerpt}"},
            ],
        }],
        label="phase2_sonnet_direct_architecture",
    )
    text = response_text_content(msg)
    parsed = extract_json_object(text)
    if parsed:
        return ArchitectureDiagnosis.from_dict(parsed)
    return ArchitectureDiagnosis(structural_flaw="unparseable_model_output")


async def phase2_architecture(state: DecomposerState) -> dict[str, Any]:
    errs = list(state.get("errors") or [])
    review_dicts = list(state.get("human_review_queue") or [])

    raw = state.get("raw_curriculum") or ""
    if not raw.strip():
        errs.append("phase2: skipped — empty raw_curriculum")
        return {
            "current_phase": "phase2:skipped",
            "errors": errs,
            "human_review_queue": review_dicts,
            "architecture_diagnosis": ArchitectureDiagnosis(
                structural_flaw="missing_input",
            ).to_dict(),
        }

    mcp_url = state.get("mcp_server_url") or ""
    mcp_name = state.get("mcp_server_name") or "claude-education-skills"
    excerpt = raw[:100000]

    user_instruction = (
        "Use the MCP tool "
        f"`{TOOL_NAME}` to diagnose the curriculum architecture. "
        "Then summarize the diagnosis as JSON in your reply (same schema as tool output / "
        "the fields: architecture_type, proportions, hierarchical_elements, horizontal_elements, "
        "dispositional_elements, structural_flaw, auto_assessable_pct). "
        "Prefer numeric proportions that sum to ~1.0. "
        "Return descriptive, subject-specific element names for hierarchical_elements, "
        "horizontal_elements, and dispositional_elements. Do NOT use generic labels like "
        "'prerequisite_chains', 'conceptual_hubs', or 'competencies'. "
        "Use names that describe the actual content strand, e.g. 'Geographic and Chronological Skills', "
        "'Historical Thinking and Inquiry', 'Historical Empathy and Citizenship'. "
        "Names should be 3-6 words, title case, meaningful to a teacher reading the output."
    )

    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": user_instruction},
            {"type": "text", "text": f"Full curriculum text:\n\n{excerpt}"},
        ],
    }]

    used_mcp = False
    diagnosis = ArchitectureDiagnosis()
    resp: Any = None

    try:
        client = get_async_client()
        resp = await beta_messages_create(
            client,
            model=SONNET_MODEL,
            max_tokens=8192,
            messages=messages,
            label="phase2_mcp_architecture",
            mcp_servers=mcp_servers_param(mcp_url, mcp_name),
            tools=[mcp_toolset_single_tool(mcp_name, TOOL_NAME)],
        )
        used_mcp = True
        text = response_text_content(resp)
        parsed = extract_json_object(text)
        if parsed:
            diagnosis = ArchitectureDiagnosis.from_dict(parsed)
        else:
            raise ValueError("no_json_in_mcp_response")
    except AnthropicCallTimeout:
        errs.append("phase2: API timeout after 240s")
        diagnosis = ArchitectureDiagnosis(structural_flaw="timeout_phase2")
        return {
            "current_phase": "phase2:timeout",
            "errors": errs,
            "human_review_queue": review_dicts,
            "architecture_diagnosis": diagnosis.to_dict(),
        }
    except Exception as exc:
        raw_dump = ""
        try:
            raw_dump = response_debug_dump(resp) if resp is not None else str(exc)
        except Exception:
            raw_dump = str(exc)
        err_line = f"phase2: MCP/tools failed: {exc}"
        errs.append(err_line)
        review_dicts.append(
            HumanReviewItem(
                item_type="phase2_mcp",
                summary=err_line[:500],
                decision_needed="Confirm raw MCP response and whether to trust fallback JSON.",
            ).to_dict(),
        )
        if raw_dump:
            review_dicts.append(
                HumanReviewItem(
                    item_type="phase2_mcp_raw",
                    summary="MCP response / error detail (truncated)",
                    decision_needed=raw_dump[:8000],
                ).to_dict(),
            )
        diagnosis = await _direct_sonnet_diagnosis(raw)

    return {
        "current_phase": "phase2:complete" if used_mcp else "phase2:fallback",
        "errors": errs,
        "human_review_queue": review_dicts,
        "architecture_diagnosis": diagnosis.to_dict(),
    }
