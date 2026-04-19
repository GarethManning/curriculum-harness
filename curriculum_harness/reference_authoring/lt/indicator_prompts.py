"""Prompts for the Type 3 observation-indicator generator.

Generates LT-SPECIFIC observable behaviours per band along the
SOURCE'S OWN native progression structure (Welsh CfW Progression
Steps 1-5, US/Ontario single grade, Scottish CfE Levels, etc.) and
LT-SPECIFIC parent/caregiver noticing prompts. Self-reflection
prompts per band are inserted by the pipeline from the
``ProgressionStructure.band_self_reflection_prompts`` map calibrated
to each source's own developmental expectations; the LLM does NOT
generate them.

Type 3 LTs NEVER get rubric criteria. This is the LT authoring skill's
absolute rule. The indicator set describes what the sustained
orientation looks like as observed in natural settings, not as scored
against a competence rubric.
"""

from __future__ import annotations

from curriculum_harness.reference_authoring.progression import (
    ProgressionStructure,
)


_HEAD_MULTI = """You generate Mode 3 observation indicators for ONE Type 3 Learning Target at a time. You apply the LT authoring skill's observation protocol rules mechanically against this source's own native progression structure. You do not invent content. You do not consult outside examples. You emit strict JSON.

ABSOLUTE RULE

Type 3 LTs NEVER get rubric criteria. You do not produce Competent / Approaching / Proficient descriptors. You do not produce success-level rubric text. You produce observable behaviours that third parties can notice in natural settings.

WHAT YOU PRODUCE

For ONE Type 3 LT, you produce two kinds of LT-specific content:

1. Per-band observable behaviours (2-3 per band) for this source's native bands, in developmental order:

{band_list_block}

   Source progression context: {source_type}, {age_range_hint}.

   Band rules:
   - Third-person language: "The student [specific observable behaviour at this band level]". NOT "I can".
   - Observable in natural classroom, playground, or community settings — not only on-task performance.
   - LT-specific. These behaviours refer explicitly to the sustained orientation named by the LT.
   - Developmentally calibrated. Earliest band behaviours are more prompted, concrete, infrequent. Latest band behaviours are sustained, enacted across unfamiliar contexts, self-initiated.

2. Parent / caregiver noticing prompts (exactly 3). Plain language, addressed to a parent or caregiver, asking what they have noticed at home. LT-specific — tailored to the particular sustained orientation."""

_HEAD_SINGLE = """You generate Mode 3 observation indicators for ONE Type 3 Learning Target at a SINGLE GRADE LEVEL for a single-grade source. You apply the LT authoring skill's observation protocol rules mechanically. You do not invent content. You do not consult outside examples. You emit strict JSON.

ABSOLUTE RULE

Type 3 LTs NEVER get rubric criteria. You do not produce Competent / Approaching / Proficient descriptors. You produce observable behaviours that third parties can notice in natural settings.

WHAT YOU PRODUCE

This source has a single grade level: {single_band_label}. There is no progression sequence inside the source. You produce ONE band entry containing 2-3 observable behaviours at {single_band_label}, plus 3 parent/caregiver noticing prompts. Do not invent additional bands.

Source progression context: {source_type}, {age_range_hint}.

Band rules:
- Third-person language: "The student [specific observable behaviour at {single_band_label} level]". NOT "I can".
- Observable in natural classroom, playground, or community settings.
- LT-specific.
- Pitched at this grade's developmental level — neither earliest-band scaffolded nor latest-band sustained-across-unfamiliar-contexts."""

_NOT_PRODUCE = """WHAT YOU DO NOT PRODUCE

- NO rubric descriptors.
- NO self-reflection prompts (the pipeline inserts those, calibrated to this source's own developmental expectations per band).
- NO summative scoring language.
- NO "student demonstrates mastery of ...".

DEVELOPMENTAL CONVERSATION PROTOCOL

Include a brief (1-2 sentence) reference to the developmental conversation protocol: what the synthesising conversation between teacher, student, and optionally parent covers. NOT a full script — a reference pointer."""

_SCHEMA_MULTI = """OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences). Use the band labels EXACTLY as listed above, in the order shown:

{{
  "bands": [
{schema_examples}
  ],
  "parent_prompts": [
    "<plain-language question addressed to parent / caregiver>",
    "<...>",
    "<...>"
  ],
  "developmental_conversation_protocol": "<1-2 sentence reference describing what the synthesising conversation covers>"
}}

CONSTRAINTS

- Exactly {band_count} band entries in the order shown above.
- The "band" field of each entry MUST match one of the listed band labels exactly.
- Each band has 2 or 3 observable_behaviours (not 1, not 4+).
- Every observable behaviour starts with "The student ".
- Exactly 3 parent_prompts.
- Parent prompts do NOT start with "The student"; they are addressed to the parent ("What have you noticed about...", "When your child...", etc.).
- Every observable behaviour is specific to this LT's sustained orientation — no generic "behaves well" language.
- No inline examples, no "such as", no parentheses."""

_SCHEMA_SINGLE = """OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences):

{{
  "bands": [
    {{"band": "{single_band_label}", "observable_behaviours": ["The student <...>", "The student <...>"]}}
  ],
  "parent_prompts": [
    "<plain-language question addressed to parent / caregiver>",
    "<...>",
    "<...>"
  ],
  "developmental_conversation_protocol": "<1-2 sentence reference>"
}}

CONSTRAINTS

- Exactly 1 band entry whose "band" field is "{single_band_label}".
- 2 or 3 observable_behaviours (not 1, not 4+).
- Every observable behaviour starts with "The student ".
- Exactly 3 parent_prompts; parent prompts do NOT start with "The student".
- No inline examples, no "such as", no parentheses."""


def _band_list_block(progression: ProgressionStructure) -> str:
    return "\n".join(f"   - {label}" for label in progression.band_labels)


def _schema_examples(progression: ProgressionStructure) -> str:
    parts: list[str] = []
    for label in progression.band_labels:
        parts.append(
            "    {{\"band\": \"" + label + "\", \"observable_behaviours\": "
            "[\"The student <...>\", \"The student <...>\"]}}"
        )
    return ",\n".join(parts)


def build_system_prompt(progression: ProgressionStructure) -> str:
    if progression.is_single_band():
        head = _HEAD_SINGLE.format(
            single_band_label=progression.band_labels[0],
            source_type=progression.source_type,
            age_range_hint=progression.age_range_hint,
        )
        schema = _SCHEMA_SINGLE.format(
            single_band_label=progression.band_labels[0],
        )
    else:
        head = _HEAD_MULTI.format(
            band_list_block=_band_list_block(progression),
            source_type=progression.source_type,
            age_range_hint=progression.age_range_hint,
        )
        schema = _SCHEMA_MULTI.format(
            band_count=progression.band_count,
            schema_examples=_schema_examples(progression),
        )
    return "\n\n".join([head, _NOT_PRODUCE, schema])


def build_user_prompt(
    *,
    lt_name: str,
    lt_definition: str,
    competency_name: str,
    prerequisite_lts: list[str],
    progression: ProgressionStructure,
) -> str:
    lines: list[str] = []
    lines.append(f"COMPETENCY: {competency_name}")
    lines.append(f"LT NAME: {lt_name}")
    lines.append(f"LT DEFINITION: {lt_definition}")
    lines.append(
        f"SOURCE PROGRESSION: {progression.source_type} "
        f"({progression.band_count} band(s); {progression.age_range_hint})"
    )
    if prerequisite_lts:
        lines.append(
            "PREREQUISITE LTS (Type 1/2 LTs that must be established first): "
            + ", ".join(prerequisite_lts)
        )
    else:
        lines.append("PREREQUISITE LTS: none")
    lines.append("")
    if progression.is_single_band():
        lines.append(
            f"Generate Mode 3 observation indicators for this Type 3 LT at "
            f"{progression.band_labels[0]}. Produce a single band entry, "
            "LT-specific parent / caregiver noticing prompts (3), and a "
            "brief developmental-conversation protocol reference. "
            "Remember: NO rubric descriptors, NO self-reflection prompts "
            "(the pipeline inserts those). Emit ONE JSON object per the schema."
        )
    else:
        labels_str = ", ".join(progression.band_labels)
        lines.append(
            f"Generate Mode 3 observation indicators for this Type 3 LT covering "
            f"{labels_str}. Produce LT-specific observable behaviours per band "
            "(2-3 each), LT-specific parent / caregiver noticing prompts (3), "
            "and a brief developmental-conversation protocol reference. "
            "Remember: NO rubric descriptors, NO self-reflection prompts "
            "(the pipeline inserts those calibrated to the source's own "
            "expectations per band). Emit ONE JSON object per the schema."
        )
    return "\n".join(lines)
