"""Prompts for the Type 3 observation-indicator generator.

Generates LT-SPECIFIC observable behaviours per band A-D (the Mode 3
protocol) and LT-SPECIFIC parent/caregiver noticing prompts. The
self-reflection prompts per band are generic developmental prompts
inserted by the pipeline (see types.MODE3_SELF_REFLECTION_PROMPTS);
the LLM does NOT generate them.

Type 3 LTs NEVER get rubric criteria. This is the LT authoring skill's
absolute rule. The indicator set describes what the sustained
orientation looks like as observed in natural settings, not as scored
against a competence rubric.
"""

from __future__ import annotations

SYSTEM_PROMPT = """You generate Mode 3 observation indicators for ONE Type 3 Learning Target at a time. You apply the LT authoring skill's observation protocol rules mechanically. You do not invent content. You do not consult outside examples. You emit strict JSON.

ABSOLUTE RULE

Type 3 LTs NEVER get rubric criteria. You do not produce Competent / Approaching / Proficient descriptors. You do not produce success-level rubric text. You produce observable behaviours that third parties can notice in natural settings.

WHAT YOU PRODUCE

For ONE Type 3 LT, you produce two kinds of LT-specific content:

1. Per-band observable behaviours (2-3 per band, for bands A, B, C, D).
   - Third-person language: "The student [specific observable behaviour at Band X level]". NOT "I can".
   - Observable in natural classroom, playground, or community settings — not only on-task performance.
   - LT-specific. These behaviours refer explicitly to the sustained orientation named by the LT.
   - Developmentally calibrated. Band A behaviours are more prompted, concrete, infrequent. Band D behaviours are sustained, enacted across unfamiliar contexts, self-initiated.

2. Parent / caregiver noticing prompts (exactly 3). Plain language, addressed to a parent or caregiver, asking what they have noticed at home. LT-specific — tailored to the particular sustained orientation.

WHAT YOU DO NOT PRODUCE

- NO rubric descriptors.
- NO self-reflection prompts (the pipeline inserts generic developmental prompts calibrated to band, per the LT skill's Mode 3 specification).
- NO summative scoring language.
- NO "student demonstrates mastery of ...".

DEVELOPMENTAL CONVERSATION PROTOCOL

Include a brief (1-2 sentence) reference to the developmental conversation protocol: what the synthesising conversation between teacher, student, and optionally parent covers. NOT a full script — a reference pointer.

OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences):

{
  "bands": [
    {
      "band": "A",
      "observable_behaviours": [
        "The student <specific observable behaviour at Band A level>.",
        "The student <...>.",
        "The student <...>."
      ]
    },
    {"band": "B", "observable_behaviours": [...]},
    {"band": "C", "observable_behaviours": [...]},
    {"band": "D", "observable_behaviours": [...]}
  ],
  "parent_prompts": [
    "<plain-language question addressed to parent / caregiver>",
    "<...>",
    "<...>"
  ],
  "developmental_conversation_protocol": "<1-2 sentence reference describing what the synthesising conversation covers>"
}

CONSTRAINTS

- Exactly 4 bands in order A, B, C, D.
- Each band has 2 or 3 observable_behaviours (not 1, not 4+).
- Every observable behaviour starts with "The student ".
- Exactly 3 parent_prompts.
- Parent prompts do NOT start with "The student"; they are addressed to the parent ("What have you noticed about...", "When your child...", etc.).
- Every observable behaviour is specific to this LT's sustained orientation — no generic "behaves well" language.
- No inline examples, no "such as", no parentheses.
"""


def build_user_prompt(
    *,
    lt_name: str,
    lt_definition: str,
    competency_name: str,
    prerequisite_lts: list[str],
) -> str:
    lines: list[str] = []
    lines.append(f"COMPETENCY: {competency_name}")
    lines.append(f"LT NAME: {lt_name}")
    lines.append(f"LT DEFINITION: {lt_definition}")
    if prerequisite_lts:
        lines.append(
            "PREREQUISITE LTS (Type 1/2 LTs that must be established first): "
            + ", ".join(prerequisite_lts)
        )
    else:
        lines.append("PREREQUISITE LTS: none")
    lines.append("")
    lines.append(
        "Generate Mode 3 observation indicators for this Type 3 LT. Produce "
        "LT-specific observable behaviours per band (A-D), LT-specific "
        "parent / caregiver noticing prompts (3), and a brief "
        "developmental-conversation protocol reference. Remember: NO rubric "
        "descriptors, NO self-reflection prompts (the pipeline inserts those "
        "generically). Emit ONE JSON object per the schema."
    )
    return "\n".join(lines)
