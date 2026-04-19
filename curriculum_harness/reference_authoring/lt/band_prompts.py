"""Prompts for the Type 1/2 band-statement generator.

Generates band statements for a single LT against the source's own
native progression structure. The band labels and their developmental
ordering come from the source — Welsh CfW Progression Steps 1-5, US
Common Core single grade, Scottish CfE Levels, etc. Single-band
sources (band_count == 1) produce one statement per LT at the
source's grade level rather than a band progression.

Progression levers from the LT authoring skill remain universal:
independence, complexity, scope, precision, reasoning, transfer. They
are how progression works developmentally, not what any specific
school's bands are called.
"""

from __future__ import annotations

from curriculum_harness.reference_authoring.progression import (
    ProgressionStructure,
)


_MULTI_BAND_HEADER = """You generate developmental band progressions for ONE Type 1 or Type 2 Learning Target at a time. You apply the LT authoring skill's band-statement rules mechanically. You do not invent content. You do not consult outside examples. You emit strict JSON.

WHAT BAND STATEMENTS ARE

The band statements describe the SAME capability at developmental levels along this source's native progression structure. They describe what the learner can do, not what the learner is given to do. The bands for this source, in developmental order, are:

{band_list_block}

Source progression context: {source_type}, {age_range_hint}.

PROGRESSION LEVERS — USE THESE, NOT TOPIC ESCALATION

Use levers (independence, complexity, scope, precision, reasoning, transfer) to escalate across the bands. The TOPIC stays fixed — it is the capability's sophistication that grows. Do not introduce new content at higher bands.

Acceptable escalation: earliest band "identify with prompting", latest band "identify, explain, and justify across unfamiliar contexts" — the same capability, escalating along the levers.
Unacceptable escalation: earliest band "identify primary colours", latest band "identify colours in the HSL colour space" — that is topic escalation, not developmental progression."""

_SINGLE_BAND_HEADER = """You generate ONE Type 1 or Type 2 Learning Target's band statement at a single grade level for a single-grade source. You apply the LT authoring skill's band-statement rules mechanically. You do not invent content. You do not consult outside examples. You emit strict JSON.

WHAT THE BAND STATEMENT IS

This source has a single grade level: {single_band_label}. There is no progression sequence inside the source. You produce ONE band statement describing the developmentally-appropriate target at {single_band_label}, expressed as a single capability the learner can demonstrate. Do not invent additional bands.

Source context: {source_type}, {age_range_hint}.

LEVERS APPLY TO THE SINGLE STATEMENT'S LEVEL

Use the LT authoring skill's progression levers (independence, complexity, scope, precision, reasoning, transfer) to set the statement at the right developmental level for this grade — independent performance with grade-appropriate complexity, scope, and reasoning. Do not pitch it as "emerging" or "extending"; it is a single grade-level capability."""

_FORMAT_RULES = """FORMAT — MANDATORY

- Each band statement starts "I can " (lowercase "i can" is acceptable at JSON level; render as "I can ..." in the emitted string).
- One sentence per band.
- 10-25 words per band.
- Observable action verb only: identify, describe, compare, explain, justify, analyse, evaluate, create, apply, interpret, construct, communicate.
- Single-construct: each statement describes ONE coherent capability.
- NO inline examples, NO "such as", NO parentheses, NO "for example".
- NO lists of sub-skills within a statement."""

_MULTI_BAND_SCHEMA = """OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences). Use the band labels EXACTLY as listed above, in the order shown:

{{
  "band_statements": [
{schema_examples}
  ]
}}

CONSTRAINTS

- Exactly {band_count} band statements, in the order shown above.
- The "band" field of each entry MUST match one of the listed band labels exactly.
- Every statement starts with "I can ".
- No band statement exceeds 25 words; no band statement is shorter than 10 words.
- No statement repeats another statement's phrasing verbatim.
- No band introduces a new topic the LT definition does not cover."""

_SINGLE_BAND_SCHEMA = """OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences):

{{
  "band_statements": [
    {{"band": "{single_band_label}", "statement": "I can <...>"}}
  ]
}}

CONSTRAINTS

- Exactly 1 band statement entry whose "band" field is "{single_band_label}".
- The statement starts with "I can ".
- Statement is 10-25 words.
- No inline examples, no "such as", no parentheses, no "for example"."""


def _band_list_block(progression: ProgressionStructure) -> str:
    lines: list[str] = []
    for label in progression.band_labels:
        lines.append(f"- {label}")
    return "\n".join(lines)


def _schema_examples(progression: ProgressionStructure) -> str:
    parts: list[str] = []
    for label in progression.band_labels:
        parts.append(f'    {{"band": "{label}", "statement": "I can <...>"}}')
    return ",\n".join(parts)


def build_system_prompt(progression: ProgressionStructure) -> str:
    """Build the system prompt for band-statement generation.

    The prompt is parameterised on the source's native progression
    structure: band labels in developmental order, single-band vs
    multi-band framing, and source-type/age context for orientation.
    """

    if progression.is_single_band():
        head = _SINGLE_BAND_HEADER.format(
            single_band_label=progression.band_labels[0],
            source_type=progression.source_type,
            age_range_hint=progression.age_range_hint,
        )
        schema = _SINGLE_BAND_SCHEMA.format(
            single_band_label=progression.band_labels[0],
        )
    else:
        head = _MULTI_BAND_HEADER.format(
            band_list_block=_band_list_block(progression),
            source_type=progression.source_type,
            age_range_hint=progression.age_range_hint,
        )
        schema = _MULTI_BAND_SCHEMA.format(
            band_count=progression.band_count,
            schema_examples=_schema_examples(progression),
        )
    return "\n\n".join([head, _FORMAT_RULES, schema])


def build_user_prompt(
    *,
    lt_name: str,
    lt_definition: str,
    knowledge_type: str,
    competency_name: str,
    progression: ProgressionStructure,
) -> str:
    lines: list[str] = []
    lines.append(f"COMPETENCY: {competency_name}")
    lines.append(f"LT NAME: {lt_name}")
    lines.append(f"LT DEFINITION: {lt_definition}")
    lines.append(f"KNOWLEDGE TYPE: {knowledge_type}")
    lines.append(
        f"SOURCE PROGRESSION: {progression.source_type} "
        f"({progression.band_count} band(s); {progression.age_range_hint})"
    )
    lines.append("")
    if progression.is_single_band():
        lines.append(
            f"Generate ONE band statement at {progression.band_labels[0]} for this LT. "
            "Use progression levers to pitch it at the right developmental level "
            "for this grade. Emit ONE JSON object per the schema."
        )
    else:
        labels_str = ", ".join(progression.band_labels)
        lines.append(
            f"Generate {progression.band_count} band statements covering "
            f"{labels_str} for this LT. Use progression levers (independence, "
            "complexity, scope, precision, reasoning, transfer). Keep the topic "
            "fixed; escalate sophistication. Emit ONE JSON object per the schema."
        )
    return "\n".join(lines)
