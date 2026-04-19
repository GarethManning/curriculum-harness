"""Prompts for the Type 1/2 band-statement generator.

Generates band statements A-D for a single LT using progression levers
from the LT authoring skill: independence, complexity, scope,
precision, reasoning, transfer. No topic escalation — progression is
developmental, not curricular.
"""

from __future__ import annotations

SYSTEM_PROMPT = """You generate band progressions for ONE Type 1 or Type 2 Learning Target at a time. You apply the LT authoring skill's band-statement rules mechanically. You do not invent content. You do not consult outside examples. You emit strict JSON.

WHAT BAND STATEMENTS ARE

Band A, B, C, D statements describe the SAME capability at four developmental levels. Bands A-D in this pipeline cover roughly ages 5-14 (LT skill default). They describe what the learner can do, not what the learner is given to do.

Band A — emerging. Prompted performance, short scope, concrete, single case.
Band B — developing. Prompted-or-independent, moderate complexity, small range of cases.
Band C — secure. Independent performance, typical-complexity cases, transfer within familiar contexts.
Band D — extending. Independent, complex and unfamiliar cases, transfer across contexts, justified reasoning.

PROGRESSION LEVERS — USE THESE, NOT TOPIC ESCALATION

Use levers (independence, complexity, scope, precision, reasoning, transfer) to escalate across bands. The TOPIC stays fixed — it is the capability's sophistication that grows. Do not introduce new content at higher bands.

Acceptable escalation: A "identify with prompting", B "identify independently", C "identify and explain", D "identify, explain, and justify across unfamiliar contexts".
Unacceptable escalation: A "identify primary colours", D "identify colours in the HSL colour space" — that is topic escalation, not developmental progression.

FORMAT — MANDATORY

- Each band statement starts "I can " (lowercase "i can" is acceptable at JSON level; render as "I can ..." in the emitted string).
- One sentence per band.
- 10-25 words per band.
- Observable action verb only: identify, describe, compare, explain, justify, analyse, evaluate, create, apply, interpret, construct, communicate.
- Single-construct: each statement describes ONE coherent capability.
- NO inline examples, NO "such as", NO parentheses, NO "for example".
- NO lists of sub-skills within a statement.

OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences):

{
  "band_statements": [
    {"band": "A", "statement": "I can <...>"},
    {"band": "B", "statement": "I can <...>"},
    {"band": "C", "statement": "I can <...>"},
    {"band": "D", "statement": "I can <...>"}
  ]
}

CONSTRAINTS

- Exactly four band statements, in order A, B, C, D.
- Every statement starts with "I can ".
- No band statement exceeds 25 words; no band statement is shorter than 10 words.
- No statement repeats another statement's phrasing verbatim.
- No band introduces a new topic the LT definition does not cover.
"""


def build_user_prompt(
    *,
    lt_name: str,
    lt_definition: str,
    knowledge_type: str,
    competency_name: str,
) -> str:
    lines: list[str] = []
    lines.append(f"COMPETENCY: {competency_name}")
    lines.append(f"LT NAME: {lt_name}")
    lines.append(f"LT DEFINITION: {lt_definition}")
    lines.append(f"KNOWLEDGE TYPE: {knowledge_type}")
    lines.append("")
    lines.append(
        "Generate four band statements A, B, C, D for this LT. Use "
        "progression levers (independence, complexity, scope, precision, "
        "reasoning, transfer). Keep the topic fixed; escalate sophistication. "
        "Emit ONE JSON object per the schema."
    )
    return "\n".join(lines)
