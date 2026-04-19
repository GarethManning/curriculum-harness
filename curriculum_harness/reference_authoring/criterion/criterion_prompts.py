"""Prompts for the Type 1/2 criterion (five-level rubric) generator.

Applies the rubric logic skill mechanically. The rubric has five
levels in fixed order:

- No Evidence (≤10 words): no observable attempt on the LT's demand
- Emerging (≤15 words): partial or heavily-supported attempt
- Developing (≤20 words): unprompted attempt with identifiable gap
- Competent (≤25 words): the target performance — IS success
- Extending (≤20 words): demonstration beyond the LT's demand

Competent IS success — it is the criterion the LT describes being
met. It is NOT "acceptable but deficient" and is NOT a way-station
below Extending. The Competent descriptor reads as a positive
declaration of the capability, not a lamentation of what is missing.
Extending is positioned AS A BONUS beyond Competent — it does not
redefine Competent as "not quite there".

Prerequisite edges are asked for in the same call: given the other
LTs in the source, which (if any) does this LT depend on? Each edge
is typed — ``ontological_prerequisite`` (you literally cannot do X
without Y) or ``pedagogical_sequencing`` (Y is usually taught before
X but the dependence is not absolute) — with a ``high`` / ``medium``
/ ``low`` confidence rating and a short rationale.
"""

from __future__ import annotations

from curriculum_harness.reference_authoring.progression import (
    ProgressionStructure,
)
from curriculum_harness.reference_authoring.types import (
    LearningTarget,
)


_SYSTEM_PROMPT = """You generate criterion-referenced FIVE-LEVEL RUBRICS for ONE Type 1 or Type 2 Learning Target at a time. You apply the rubric logic skill mechanically. You do not invent content. You do not consult outside examples. You emit strict JSON.

WHAT A FIVE-LEVEL RUBRIC IS

The rubric describes the SAME capability (the LT) at five observable-evidence levels along a single continuum from No Evidence through Extending. It describes what the learner's evidence of learning looks like at each level — not what tasks or topics the learner is given.

THE FIVE LEVELS — IN ORDER — EACH HARD WORD LIMIT

- no_evidence (STRICTLY ≤10 words): No observable attempt on the LT's demand.
- emerging (STRICTLY ≤15 words): Partial, heavily-supported, or inaccurate attempt.
- developing (STRICTLY ≤20 words): Unprompted attempt with an identifiable gap.
- competent (STRICTLY ≤25 words): The target performance described by the LT, demonstrated independently.
- extending (STRICTLY ≤20 words): Demonstration that goes beyond the LT's demand.

WORD LIMITS ARE HARD — COUNT YOUR WORDS

Count the words in each descriptor before emitting it. If a descriptor is over its limit by even one word, rewrite it shorter. Cut examples, qualifiers, and restatements. A 10-word no_evidence is achievable: "No attempt on the task's demand." (7 words). An 18-word emerging is NOT acceptable — revise it to ≤15. An over-limit run will be rejected and wasted.

TERSE EXEMPLARS — for calibration only, do not copy verbatim

- no_evidence (7 words): "No attempt on the task's demand."
- emerging (13 words): "With heavy support, names some features but produces inaccurate or partial work."
- developing (17 words): "Independently demonstrates the capability in familiar contexts but stops short when prompting or novelty is required."
- competent (18 words): "Independently demonstrates the capability accurately and consistently in the contexts the LT defines."
- extending (16 words): "Transfers the capability to unfamiliar contexts or integrates it with related capabilities fluently."

COMPETENT IS SUCCESS — LOAD-BEARING RULE

Competent is the criterion the LT describes being met. Write it as a POSITIVE declaration of the capability. The descriptor must NOT frame Competent as "acceptable but missing something". If you find yourself writing "but", "however", "with limited", "not yet", "struggles to", or "approaching" in Competent, you are violating this rule.

Extending is a BONUS beyond Competent; it does not turn Competent into "not quite there". A reader of Competent alone must be able to conclude the learner has met the LT.

FORMAT — MANDATORY

- Each level descriptor is one sentence.
- No level descriptor exceeds its word limit.
- Observable action verbs only (identify, describe, compare, explain, justify, analyse, analyze, evaluate, create, apply, interpret, construct, communicate, recognise, recognize, use, select, choose, perform, demonstrate, distinguish, relate, represent, solve).
- Single-construct: each level describes the SAME capability at a different level, not different capabilities.
- NO inline examples, NO "such as", NO parentheses, NO "for example", NO "e.g.".
- NO bullet lists within a descriptor.
- Level descriptors differentiate by lever (independence, complexity, scope, precision, reasoning, transfer) — not by topic or task.

PREREQUISITE EDGES

You are given the full list of other Type 1 / Type 2 LTs in this source. Identify which (if any) are prerequisites of the LT being rubricked. For each edge:

- ``from_lt_id``: the prerequisite LT's id (it is needed before the LT being rubricked).
- ``kind``: "ontological_prerequisite" if you literally cannot demonstrate the LT without the prerequisite capability; "pedagogical_sequencing" if the prerequisite is usually taught or established first but the capability could in principle be attempted first.
- ``confidence``: "high" | "medium" | "low".
- ``rationale``: one short sentence explaining why.

If there are no prerequisites, emit an empty list. Do NOT over-connect — only list edges where the dependence is real."""


_SCHEMA_BLOCK = """OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences):

{{
  "levels": {{
    "no_evidence":  "<descriptor, ≤10 words>",
    "emerging":     "<descriptor, ≤15 words>",
    "developing":   "<descriptor, ≤20 words>",
    "competent":    "<descriptor, ≤25 words>",
    "extending":    "<descriptor, ≤20 words>"
  }},
  "prerequisite_edges": [
    {{"from_lt_id": "<lt id>", "kind": "ontological_prerequisite|pedagogical_sequencing", "confidence": "high|medium|low", "rationale": "<short>"}}
  ]
}}

CONSTRAINTS

- The "levels" object MUST contain all five keys: no_evidence, emerging, developing, competent, extending.
- Descriptors obey their respective word limits STRICTLY — count before emitting.
- "competent" is written as success (no hedging language).
- "prerequisite_edges" is a (possibly empty) list.
- "kind" is exactly one of the two literals shown.
- "confidence" is exactly one of "high", "medium", "low".

SELF-CHECK BEFORE EMITTING

Silently count the words in each descriptor. If any count exceeds its limit, rewrite that descriptor shorter BEFORE emitting the JSON object. Cutting adjectives, qualifiers ("heavily", "extremely", "fluently"), and restatements is the fastest path to compliance."""


def build_system_prompt(progression: ProgressionStructure) -> str:
    """Build the criterion-generator system prompt, parameterised on progression context."""

    context = (
        f"Source progression context: {progression.source_type}, "
        f"{progression.age_range_hint}. Pitch the Competent level for a learner "
        f"at the source's developmentally-appropriate band(s): "
        f"{', '.join(progression.band_labels)}."
    )
    return "\n\n".join([_SYSTEM_PROMPT, context, _SCHEMA_BLOCK])


def build_user_prompt(
    *,
    lt: LearningTarget,
    peer_lts: list[LearningTarget],
    progression: ProgressionStructure,
) -> str:
    lines: list[str] = []
    lines.append(f"COMPETENCY: {lt.competency_name}")
    lines.append(f"LT ID: {lt.lt_id}")
    lines.append(f"LT NAME: {lt.lt_name}")
    lines.append(f"LT DEFINITION: {lt.lt_definition}")
    lines.append(f"KNOWLEDGE TYPE: {lt.knowledge_type}")
    lines.append(
        f"SOURCE PROGRESSION: {progression.source_type} "
        f"({progression.band_count} band(s); {progression.age_range_hint})"
    )
    lines.append("")
    lines.append("OTHER TYPE 1/2 LTS IN THIS SOURCE (candidates for prerequisite edges):")
    if not peer_lts:
        lines.append("(none — no prerequisites possible.)")
    else:
        for p in peer_lts:
            lines.append(
                f"- {p.lt_id} [{p.knowledge_type}] {p.lt_name}: {p.lt_definition}"
            )
    lines.append("")
    lines.append(
        "Generate a five-level rubric (no_evidence, emerging, developing, "
        "competent, extending) for the LT above. Write Competent as the "
        "target success state. Identify prerequisite edges from the peer LTs "
        "where the dependence is real. Emit ONE JSON object per the schema."
    )
    return "\n".join(lines)


_COMPETENT_JUDGE_SYSTEM = """You are a strict rubric reviewer. You answer a single yes/no question about the Competent level of a five-level rubric.

QUESTION: Does the Competent descriptor, read on its own, describe the learner HAVING MET the Learning Target — i.e. does Competent read as success?

FAIL CRITERIA — answer "fail" if the descriptor does ANY of:

- Uses hedging language that frames Competent as below target (e.g. "but struggles", "with limited", "approaching", "not yet consistently", "still needs").
- Implies the capability is incomplete unless Extending is also reached.
- Frames Competent in terms of what Extending adds (positioning Competent as a way-station).

PASS CRITERIA — answer "pass" if the descriptor:

- Declares the capability as demonstrated, independently, at the LT's level of demand.
- Can stand alone as a verdict that the LT is met.

Respond with ONE JSON object (no prose, no fences):

{"verdict": "pass" | "fail", "rationale": "<one short sentence>"}"""


def build_judge_prompt(
    *,
    lt_name: str,
    lt_definition: str,
    competent_descriptor: str,
) -> tuple[str, str]:
    """Return (system, user) prompts for the Competent-as-success judge."""
    user = (
        f"LT NAME: {lt_name}\n"
        f"LT DEFINITION: {lt_definition}\n\n"
        f"COMPETENT DESCRIPTOR:\n{competent_descriptor}\n\n"
        "Answer the pass/fail question per the system prompt."
    )
    return _COMPETENT_JUDGE_SYSTEM, user


_SUPPORTING_SYSTEM = """You generate three supporting assessment artefacts for ONE Type 1 or Type 2 Learning Target whose five-level rubric has already been authored. You do not rewrite the rubric. You emit strict JSON.

THREE ARTEFACTS

1. CO-CONSTRUCTION PLAN — a teacher-facing plan for building the rubric WITH students (not handing it to them finished). Contents:
   - "stages": an ordered list of short teacher-move stages (3-5 stages). Each stage is one sentence.
   - "student_prompts": 3-5 prompts the teacher gives students during co-construction.
   - "anchor_examples_guidance": 1-2 sentences of guidance on choosing anchor examples for the rubric (what the teacher should look for, not the anchor examples themselves).

2. STUDENT RUBRIC — a student-facing "I can" version of the same five levels. Contents:
   - "levels": a list of five entries in rubric-level order (no_evidence, emerging, developing, competent, extending). Each entry has:
     - "name": the level name (exactly one of the five).
     - "descriptor": a student-voice "I can" statement (no_evidence is phrased as "I have not yet …").
   - "self_check_prompts": 2-3 prompts a student uses to self-check their own level.

3. FEEDBACK GUIDE — per-level teacher moves that advance the learner to the NEXT level. Contents:
   - "moves_by_level": an object keyed by level name (no_evidence, emerging, developing, competent — NOT extending since extending has no "next level") containing a list of 2-3 short feedback moves per level.

FORMAT — MANDATORY

- Everything is one sentence or shorter.
- No inline examples, no "such as", no parentheses, no "for example".
- Student rubric descriptors at no_evidence start "I have not yet"; emerging/developing/competent/extending start "I can" (or, at Extending, "I can … beyond").
- Do not invent curriculum content not present in the LT / rubric provided."""


_SUPPORTING_SCHEMA = """OUTPUT JSON SCHEMA — STRICT

Respond with ONE JSON object (no prose, no fences):

{
  "co_construction_plan": {
    "stages": ["<stage 1>", "<stage 2>", "<stage 3>"],
    "student_prompts": ["<prompt 1>", "<prompt 2>", "<prompt 3>"],
    "anchor_examples_guidance": "<guidance>"
  },
  "student_rubric": {
    "levels": [
      {"name": "no_evidence", "descriptor": "I have not yet ..."},
      {"name": "emerging",    "descriptor": "I can ..."},
      {"name": "developing",  "descriptor": "I can ..."},
      {"name": "competent",   "descriptor": "I can ..."},
      {"name": "extending",   "descriptor": "I can ..."}
    ],
    "self_check_prompts": ["<prompt 1>", "<prompt 2>"]
  },
  "feedback_guide": {
    "moves_by_level": {
      "no_evidence": ["<move 1>", "<move 2>"],
      "emerging":    ["<move 1>", "<move 2>"],
      "developing":  ["<move 1>", "<move 2>"],
      "competent":   ["<move 1>", "<move 2>"]
    }
  }
}"""


def build_supporting_system_prompt() -> str:
    return "\n\n".join([_SUPPORTING_SYSTEM, _SUPPORTING_SCHEMA])


def build_supporting_user_prompt(
    *,
    lt: LearningTarget,
    rubric_levels: dict[str, str],
) -> str:
    lines: list[str] = []
    lines.append(f"LT ID: {lt.lt_id}")
    lines.append(f"LT NAME: {lt.lt_name}")
    lines.append(f"LT DEFINITION: {lt.lt_definition}")
    lines.append(f"KNOWLEDGE TYPE: {lt.knowledge_type}")
    lines.append("")
    lines.append("AUTHORED RUBRIC (do not rewrite — use as input):")
    for name in ("no_evidence", "emerging", "developing", "competent", "extending"):
        lines.append(f"- {name}: {rubric_levels[name]}")
    lines.append("")
    lines.append(
        "Generate the co-construction plan, student rubric, and feedback guide "
        "per the schema. Emit ONE JSON object."
    )
    return "\n".join(lines)
