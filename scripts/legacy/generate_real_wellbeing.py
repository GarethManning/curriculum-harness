"""REAL School Budapest — Wellbeing Framework Reference Corpus Generator
Session REAL-1, 2026-04-20

Produces all reference corpus artefacts for the REAL School Budapest wellbeing
framework at docs/reference-corpus/real-wellbeing-2026-04/:

  architecture-diagnosis.json
  kud-by-competency-by-band.json
  lt-by-band.json
  criterion-bank.json
  quality-report.json
  readable-output/ (markdown versions)

Source: docs/run-snapshots/real-wellbeing-2026-04/source.md

Usage:
    python scripts/generate_real_wellbeing.py [--phase PHASE]

Where PHASE is one of:
    all           (default) — run all phases
    diagnosis     — architecture diagnosis only
    kud           — KUD classification
    lt-gate       — LT and band-statement gate checks
    criteria      — criterion bank generation
    quality       — quality report + readable outputs
"""

# ARCHIVED 2026-04-24 — see scripts/legacy/README.md
# This script is NOT runnable from this location. The import of band_constants will fail.
# Restoration requires path surgery and schema migration; do not restore without the work
# described in scripts/legacy/README.md.

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from curriculum_harness._anthropic import LEDGER, get_async_client
from curriculum_harness.types import SONNET_MODEL, extract_json_object

sys.path.insert(0, str(Path(__file__).resolve().parent))
from band_constants import BAND_LABELS, BAND_META  # noqa: E402

# ── Paths ──────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = REPO_ROOT / "docs" / "reference-corpus" / "real-wellbeing-2026-04"
SNAPSHOT_DIR = REPO_ROOT / "docs" / "run-snapshots" / "real-wellbeing-2026-04"
READABLE_DIR = CORPUS_DIR / "readable-output"

SOURCE_SLUG = "real-wellbeing-2026-04"
SOURCE_NAME = "REAL School Budapest — Wellbeing Framework"
SCHEMA_VERSION = "v1"

BANDS = sorted(BAND_META.keys())

# ── Source data ────────────────────────────────────────────────────────────────

COMPETENCIES = [
    {
        "competency_id": "comp_1",
        "name": "Emotional Intelligence",
        "definition": "The ability to understand, express, and manage one's emotions while empathetically responding to others.",
    },
    {
        "competency_id": "comp_2",
        "name": "Attention & Reflective Practices",
        "definition": "The ability to develop present attention and reflection for clarity and wise action.",
    },
    {
        "competency_id": "comp_3",
        "name": "Physical Wellbeing & Self-Care",
        "definition": "The ability to understand and apply health-enhancing practices and routines that build resilience.",
    },
    {
        "competency_id": "comp_4",
        "name": "Consent, Safety & Healthy Relationships",
        "definition": "The ability to understand bodies, boundaries, consent, puberty, and safe, respectful choices; accessing trustworthy health information.",
    },
    {
        "competency_id": "comp_5",
        "name": "Community, Purpose & Belonging",
        "definition": "The ability to foster healthy relationships and inclusive, purpose-driven communities.",
    },
    {
        "competency_id": "comp_6",
        "name": "Wellbeing Science & Literacy",
        "definition": "The ability to understand how the brain and body produce the experiences of stress, emotion, habit, and attention — and to evaluate health information using this knowledge.",
    },
    {
        "competency_id": "comp_7",
        "name": "Metacognitive Self-Direction",
        "definition": "The ability to notice, analyse, and intentionally adjust one's own thinking and learning patterns.",
    },
]

LEARNING_TARGETS: list[dict] = [
    # ── Competency 1 ──────────────────────────────────────────────────────────
    {
        "lt_id": "lt_1_1",
        "competency_id": "comp_1",
        "lt_name": "Self-Awareness & Regulation",
        "lt_definition": "I can notice and manage my emotions, thoughts, and behaviours.",
        "knowledge_type": "Type 3",
        "assessment_route": "multi_informant_observation",
        "is_observation_indicators": True,
        "prerequisite_lts": ["lt_6_1"],
        "band_statements": {
            "A": "I can notice what my body is telling me, name a feeling, and use one calming strategy to return to learning.",
            "B": "I can identify a common personal trigger and choose a practised strategy to manage my response.",
            "C": "I can apply a chosen strategy in a challenging situation and reflect on how well it worked.",
            "D": "I can apply my strategies under stress across different settings, explain what worked and what didn't, and state one change for next time.",
        },
    },
    {
        "lt_id": "lt_1_2",
        "competency_id": "comp_1",
        "lt_name": "Social Awareness & Empathy",
        "lt_definition": "I can understand others' feelings and respond with care.",
        "knowledge_type": "Type 3",
        "assessment_route": "multi_informant_observation",
        "is_observation_indicators": True,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can name a feeling another person might be having and offer a kind word or a specific helpful action.",
            "B": "I can describe a situation from another person's perspective and ask if they would like help before acting.",
            "C": "I can notice what others say and do in a group, check in when I'm unsure, and adjust my actions to match their stated needs or boundaries.",
            "D": "I can repair a relationship after conflict by listening, owning my part, and agreeing on a next step that works for both people.",
        },
    },
    # ── Competency 2 ──────────────────────────────────────────────────────────
    {
        "lt_id": "lt_2_1",
        "competency_id": "comp_2",
        "lt_name": "Focused Attention & Strategy",
        "lt_definition": "I can direct and sustain my attention purposefully and return it when it wanders.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can use my senses to attend to one task for a short time and describe how I brought my attention back when it wandered.",
            "B": "I can use a practised attention strategy during a task and describe what made it easier or harder to focus.",
            "C": "I can evaluate how an attention strategy affected my focus during a specific task and explain why it did or didn't help.",
            "D": "I can sustain attention during a challenging task, identify what is pulling it away, and use a deliberate strategy to return.",
        },
    },
    {
        "lt_id": "lt_2_2",
        "competency_id": "comp_2",
        "lt_name": "Reflective Decision-Making",
        "lt_definition": "I can reflect on my experiences and make choices that fit my values.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can retell a short experience and state one thing I learned from it.",
            "B": "I can stop and state at least one helpful and one harmful possible outcome before making a choice.",
            "C": "I can compare multiple options, state my choice, and give a reason based on my values.",
            "D": "I can explain the trade-offs in a decision and justify my choice by considering how it affects different people.",
        },
    },
    # ── Competency 3 ──────────────────────────────────────────────────────────
    {
        "lt_id": "lt_3_1",
        "competency_id": "comp_3",
        "lt_name": "Health Literacy & Habits",
        "lt_definition": "I can understand and use healthy routines.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": ["lt_6_1"],
        "band_statements": {
            "A": "I can name my body's basic needs and practise simple personal hygiene routines with reminders.",
            "B": "I can explain how sleep, food, and movement affect how I feel, and set a goal for one healthy habit.",
            "C": "I can track one habit for a week, identify a barrier, and explain why I want to keep or change it.",
            "D": "I can compare two sources of health information, create a balanced weekly habits plan, and adjust it based on logged results.",
        },
    },
    {
        "lt_id": "lt_3_2",
        "competency_id": "comp_3",
        "lt_name": "Self-Care & Resilience",
        "lt_definition": "I can maintain my wellbeing and seek and give support.",
        "knowledge_type": "Type 3",
        "assessment_route": "multi_informant_observation",
        "is_observation_indicators": True,
        "prerequisite_lts": ["lt_6_1"],
        "band_statements": {
            "A": "I can name a trusted adult I can ask for help and practise a simple self-care routine.",
            "B": "I can identify my body's early warning signs and choose a helpful self-care response.",
            "C": "I can make a self-care plan that works at home and school and list trusted people or services for support.",
            "D": "I can maintain my key self-care routines during stressful times and describe one way I support a peer to do the same.",
        },
    },
    # ── Competency 4 ──────────────────────────────────────────────────────────
    {
        "lt_id": "lt_4_1",
        "competency_id": "comp_4",
        "lt_name": "Bodies, Boundaries & Consent",
        "lt_definition": "I can respect bodies and boundaries, seek and give consent, and get help when safety is unclear.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can name private body parts correctly and say who my trusted adults are that help keep me safe.",
            "B": "I can set and respect boundaries, ask for clear consent, and seek help if I feel pressured.",
            "C": "I can apply consent skills in non-sexual and online contexts and state my boundaries clearly to peers.",
            "D": "I can recognise power or peer-pressure risks, state my refusal and exit plan, and describe how I would support a peer to access help.",
        },
    },
    {
        "lt_id": "lt_4_2",
        "competency_id": "comp_4",
        "lt_name": "Puberty, Health & Safe Choices",
        "lt_definition": "I can understand puberty and sexual health basics and make safe, respectful choices.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": ["lt_4_1"],
        "band_statements": {
            "A": None,  # N/A — not applicable at this developmental stage
            "B": "I can explain the basic changes of puberty, use personal hygiene routines, and find reliable health information from trusted sources.",
            "C": "I can manage my personal hygiene related to puberty, identify trusted sources of health information, and explain the basics of human reproduction.",
            "D": "I can assess risks related to STIs, pregnancy, and substance use, explain protection methods, and identify steps to access confidential health advice.",
        },
    },
    # ── Competency 5 ──────────────────────────────────────────────────────────
    {
        "lt_id": "lt_5_1",
        "competency_id": "comp_5",
        "lt_name": "Interpersonal Skills & Communication",
        "lt_definition": "I can build healthy relationships with clear, respectful communication.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can take turns in conversation, use kind words, and use an I-statement.",
            "B": "I can use I-statements to state my needs, ask about boundaries, and propose two options for a fair solution.",
            "C": "I can listen in a disagreement without interrupting, choose words that stay respectful, and use a simple repair routine.",
            "D": "I can state my boundaries clearly, paraphrase before I respond, and choose words that fit the situation including in conflict.",
        },
    },
    {
        "lt_id": "lt_5_2",
        "competency_id": "comp_5",
        "lt_name": "Community Engagement & Purpose",
        "lt_definition": "I can contribute to community wellbeing with purpose.",
        "knowledge_type": "Type 3",
        "assessment_route": "multi_informant_observation",
        "is_observation_indicators": True,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can do a classroom job and explain how it helps our class.",
            "B": "I can identify when someone is left out and invite them to join an activity.",
            "C": "I can identify a need in our school, propose a simple project, and complete it with a team.",
            "D": "I can work with a diverse group to address a need, show the impact of our project, and explain why the work matters to me.",
        },
    },
    # ── Competency 6 ──────────────────────────────────────────────────────────
    {
        "lt_id": "lt_6_1",
        "competency_id": "comp_6",
        "lt_name": "Brain, Body & Wellbeing Science",
        "lt_definition": "I can explain how the brain, body, and nervous system produce the experiences of stress, emotion, habit, and attention.",
        "knowledge_type": "Type 1",
        "assessment_route": "rubric_with_clear_criteria",
        "is_observation_indicators": False,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can name body signals that tell me something about how I feel, and describe what sleep and food do for my body and brain.",
            "B": "I can explain what happens in my body during a fight, flight, or freeze response, and describe the three parts of the habit loop.",
            "C": "I can explain how the amygdala and prefrontal cortex interact during a stressful moment, explain what neuroplasticity means, and describe how the habit loop explains behaviour change at the level of mechanism.",
            "D": "I can use accurate neuroscience vocabulary to explain how stress, emotion, attention, and habit interact as a system, and describe the role of the HPA axis in the stress response.",
        },
    },
    {
        "lt_id": "lt_6_2",
        "competency_id": "comp_6",
        "lt_name": "Health Information Literacy",
        "lt_definition": "I can evaluate health information by examining the quality of its evidence and the reliability of its source.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": ["lt_6_1"],
        "band_statements": {
            "A": "I can identify whether a health claim comes from a trusted adult or source and explain my reasoning.",
            "B": "I can compare two health information sources and describe which one I trust more and why.",
            "C": "I can analyse a health claim by examining the type of evidence it uses and identifying whether the source has a reason to be biased.",
            "D": "I can evaluate a contested health claim by comparing the quality of evidence on each side, identifying the strongest and weakest arguments, and justifying my conclusion.",
        },
    },
    # ── Competency 7 ──────────────────────────────────────────────────────────
    {
        "lt_id": "lt_7_1",
        "competency_id": "comp_7",
        "lt_name": "Pattern Analysis & Adjustment",
        "lt_definition": "I can analyse a pattern in my own thinking or behaviour, explain what drives it, and describe a specific adjustment I have made or will make.",
        "knowledge_type": "Type 2",
        "assessment_route": "reasoning_quality_rubric",
        "is_observation_indicators": False,
        "prerequisite_lts": [],
        "band_statements": {
            "A": "I can describe one thing I noticed about how I reacted to a situation and say what I might do differently next time.",
            "B": "I can identify a pattern in how I tend to respond in a type of situation and give a reason for why that might happen.",
            "C": "I can analyse a pattern across more than one situation, explain what drives it, and describe a specific adjustment I have made or will make.",
            "D": "I can evaluate a pattern in my thinking or responses across different contexts, justify what sustains it, and describe the effect of a specific adjustment I have made.",
        },
    },
    {
        "lt_id": "lt_7_2",
        "competency_id": "comp_7",
        "lt_name": "Self-Direction in Practice",
        "lt_definition": "The student enacts metacognitive self-direction as a sustained orientation — noticing patterns and adjusting their approach habitually across contexts.",
        "knowledge_type": "Type 3",
        "assessment_route": "multi_informant_observation",
        "is_observation_indicators": True,
        "prerequisite_lts": ["lt_7_1"],
        "band_statements": {
            "A": (
                "Stops and tries a different approach when the first attempt does not work, without being told to. "
                "After a setback, names what happened rather than dismissing it. "
                "Accepts a suggestion to try differently without extended resistance."
            ),
            "B": (
                "Refers back to a strategy they have previously found helpful, without being prompted. "
                "After a task, volunteers one specific observation about how they worked. "
                "When something goes wrong, asks a question about why rather than placing blame."
            ),
            "C": (
                "Identifies a pattern in how they tend to respond across more than one situation and names it "
                "spontaneously in conversation. Adjusts their approach mid-task in response to noticing something "
                "is not working. In reflective writing, connects a current response to a pattern they have identified previously."
            ),
            "D": (
                "Articulates a specific adjustment they have made to their thinking or behaviour and describes its "
                "effect across more than one domain. In novel or challenging situations, applies a self-awareness "
                "strategy without an adult prompt. Makes connections between wellbeing learning and behaviour in "
                "other contexts, unprompted."
            ),
        },
    },
]

# Build lookup maps
LT_BY_ID = {lt["lt_id"]: lt for lt in LEARNING_TARGETS}
COMP_BY_ID = {c["competency_id"]: c for c in COMPETENCIES}

# ── Phase 1: Architecture Diagnosis ──────────────────────────────────────────


def make_architecture_diagnosis() -> dict:
    return {
        "source_slug": SOURCE_SLUG,
        "source_name": SOURCE_NAME,
        "source_type": "internal_school_framework",
        "domain_type": "horizontal_dispositional",
        "domain_type_notes": (
            "Primary domain is horizontal (T2) with significant dispositional (T3) component. "
            "Competency 6 (LTs 6.1, 6.2) is the sole hierarchical (T1/T2) element and functions "
            "as foundational science knowledge prerequisite to C1 and C3."
        ),
        "hierarchical_elements": ["comp_6 (lt_6_1 is T1 — Hierarchical)"],
        "scale": "curriculum",
        "contestation_level": "low",
        "developmental_scope": "explicit_progression",
        "developmental_scope_confidence": "high",
        "developmental_scope_notes": (
            "Source provides explicit per-band (A/B/C/D) statements for all 14 LTs. "
            "Bands are named learning groups with defined age/grade ranges."
        ),
        "jurisdiction": "REAL School Budapest",
        "language": "English",
        "band_reference": {
            letter: {
                "groups": [f"{d} Dragons" for d in meta["dragons"]],
                "grades": meta["grades"],
                "ages_approx": meta["ages_approx"],
                "band_label": meta["band_label"],
            }
            for letter, meta in BAND_META.items()
        },
        "competency_count": 7,
        "lt_count": 14,
        "lt_type_breakdown": {"Type 1": 1, "Type 2": 8, "Type 3": 5},
        "lt_type_1": ["lt_6_1"],
        "lt_type_2": [
            "lt_2_1", "lt_2_2", "lt_3_1", "lt_4_1", "lt_4_2",
            "lt_5_1", "lt_6_2", "lt_7_1",
        ],
        "lt_type_3": ["lt_1_1", "lt_1_2", "lt_3_2", "lt_5_2", "lt_7_2"],
        "prerequisite_structure": {
            "competency_level": [
                "Competency 6 prerequisite to Competencies 1 and 3 (source-stated)",
            ],
            "lt_level": [
                "lt_6_1 prerequisite to lt_1_1 (source-stated: C6 knowledge-contingency)",
                "lt_6_1 prerequisite to lt_3_1 (source-stated: C6 knowledge-contingency)",
                "lt_6_1 prerequisite to lt_3_2 (inferred from comp-level prerequisite)",
                "lt_6_2 prerequisite relationship to lt_6_1 (source-stated: lt_6_1 is prerequisite of lt_6_2)",
                "lt_7_1 prerequisite to lt_7_2 (source-stated)",
            ],
        },
        "flags": [],
        "generated_at": "2026-04-20",
        "session": "REAL-1",
    }


# ── Phase 2: KUD Classification ───────────────────────────────────────────────

KUD_SYSTEM = """You are a curriculum analyst. For a given Learning Target (LT) and its
per-band statements, classify each element into KUD categories:

K = Know (declarative/factual knowledge — can be tested with "what is X?")
U = Understand (conceptual understanding — can be tested with "why/how does X work?")
Do-Skill = Procedural or applied skill (T1/T2 — demonstrable action, reasoning quality)
Do-Disposition = Habitual orientation or dispositional behavior (T3 — pattern observed over time)

Rules:
1. Classify each meaningful clause of each band statement.
2. For T1 LTs: expect primarily K and U items.
3. For T2 LTs: expect primarily Do-Skill; may include K/U prerequisites.
4. For T3 LTs: expect primarily Do-Disposition; may include Do-Skill.
5. Mark each item as [source-derived] — directly from a band statement text.
6. If a band statement implies a knowledge prerequisite not explicitly stated,
   generate it as a SEPARATE item tagged [AI-inferred-from-LT].
7. Be conservative with inference — only infer if the knowledge is clearly required
   to perform the skill described.

Output ONLY valid JSON:
{
  "kud_items": [
    {
      "item_id": "kud_{lt_id}_{band}_{n:02d}",
      "lt_id": "...",
      "band": "A/B/C/D",
      "category": "K|U|Do-Skill|Do-Disposition",
      "statement": "one clear statement of what the learner knows/understands/can do",
      "provenance": "source-derived|AI-inferred-from-LT",
      "source_text_excerpt": "the clause from the band statement this derives from (or null for inferred)"
    }
  ]
}
Produce no other text. Only JSON."""


async def classify_kud_for_lt(lt: dict, client: Any) -> list[dict]:
    bands_text = ""
    for band in BANDS:
        stmt = lt["band_statements"].get(band)
        if stmt:
            bands_text += f"\nBand {band} ({BAND_LABELS[band]}): {stmt}"
        else:
            bands_text += f"\nBand {band}: N/A"

    user_msg = (
        f"LT ID: {lt['lt_id']}\n"
        f"LT Name: {lt['lt_name']}\n"
        f"Definition: {lt['lt_definition']}\n"
        f"Type: {lt['knowledge_type']}\n"
        f"Assessment: {lt['assessment_route']}\n"
        f"\nBand statements:{bands_text}"
    )

    stream = client.messages.stream(
        model=SONNET_MODEL,
        max_tokens=2048,
        system=KUD_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    async with stream as s:
        text = await s.get_final_text()
        msg = await s.get_final_message()
    LEDGER.record(
        label="refauth_kud",
        model=SONNET_MODEL,
        input_tokens=msg.usage.input_tokens,
        output_tokens=msg.usage.output_tokens,
    )

    parsed = extract_json_object(text)
    if not parsed:
        print(f"  WARNING: KUD parse failed for {lt['lt_id']}")
        return []
    return parsed.get("kud_items", [])


async def classify_all_kud(client: Any) -> dict:
    print("Phase 2: KUD classification...")
    all_items: list[dict] = []
    for lt in LEARNING_TARGETS:
        print(f"  Classifying KUD for {lt['lt_id']} ({lt['lt_name']})...")
        items = await classify_kud_for_lt(lt, client)
        all_items.extend(items)

    # Organise by competency → band
    by_comp_band: dict[str, dict[str, dict]] = {}
    for comp in COMPETENCIES:
        cid = comp["competency_id"]
        by_comp_band[cid] = {band: {"lt_items": {}} for band in BANDS}

    for item in all_items:
        lt_id = item.get("lt_id", "")
        band = item.get("band", "")
        if not lt_id or band not in BANDS:
            continue
        lt = LT_BY_ID.get(lt_id)
        if not lt:
            continue
        comp_id = lt["competency_id"]
        if comp_id not in by_comp_band:
            continue
        if lt_id not in by_comp_band[comp_id][band]["lt_items"]:
            by_comp_band[comp_id][band]["lt_items"][lt_id] = {
                "lt_name": lt["lt_name"],
                "items": [],
            }
        by_comp_band[comp_id][band]["lt_items"][lt_id]["items"].append(item)

    # Count stats
    source_derived = sum(1 for i in all_items if i.get("provenance") == "source-derived")
    ai_inferred = sum(1 for i in all_items if i.get("provenance") == "AI-inferred-from-LT")

    output = {
        "source_slug": SOURCE_SLUG,
        "schema_version": SCHEMA_VERSION,
        "total_kud_items": len(all_items),
        "source_derived_count": source_derived,
        "ai_inferred_count": ai_inferred,
        "by_competency": {},
    }

    for comp in COMPETENCIES:
        cid = comp["competency_id"]
        output["by_competency"][cid] = {
            "competency_name": comp["name"],
            "bands": by_comp_band[cid],
        }

    return output, all_items


# ── Phase 3: LT Gate-Check ────────────────────────────────────────────────────

# Observable verbs from existing harness gate
OBSERVABLE_VERBS = {
    "identify", "describe", "compare", "explain", "justify", "analyse", "analyze",
    "evaluate", "create", "apply", "interpret", "construct", "communicate",
    "demonstrate", "recognise", "recognize", "use", "develop", "design",
    "produce", "present", "reflect", "discuss", "investigate", "explore",
    "assess", "examine", "synthesise", "synthesize", "articulate", "name",
    "distinguish", "classify", "recall", "state", "list", "define", "track",
    "plan", "set", "manage", "notice", "select", "choose", "seek", "support",
    "respond", "adjust", "maintain", "direct", "sustain", "retell", "show",
    "propose", "complete", "work", "enact", "practise", "practice",
    # Added for REAL wellbeing framework (domain-appropriate observable verbs):
    "build", "contribute", "repair", "volunteer", "refer", "ask",
    "understand",  # flagged by harness — not directly observable; kept here
    # for flag-not-halt behaviour; gate produces a warning below
}

# Verbs that technically pass observable_verb gate but carry a soft flag in
# wellbeing contexts because they name mental states rather than actions.
MENTAL_STATE_VERBS = {"understand"}


def _normalise_verbs(words: set[str]) -> set[str]:
    """Strip common English verb inflections to match base forms."""
    normalised = set(words)
    for w in words:
        if w.endswith("s") and len(w) > 3:
            normalised.add(w[:-1])  # repairs → repair, enacts → enact
        if w.endswith("es") and len(w) > 4:
            normalised.add(w[:-2])  # describes → describ (imperfect but acceptable)
        if w.endswith("ing") and len(w) > 5:
            normalised.add(w[:-3])  # noticing → notic (imperfect)
    return normalised

INLINE_EXAMPLE_PATTERNS = [r"\bsuch as\b", r"\bfor example\b", r"\be\.g\.", r"\bi\.e\.", r"\bincluding\b"]

COMPETENT_DEFICIT_PHRASES = [
    r"\bsome\b", r"\bbasic\b", r"\battempts? to\b", r"\btries? to\b",
    r"\bpartial\b", r"\blimited\b", r"\bwith help\b", r"\bwith guidance\b",
    r"\bbeginning to\b", r"\bstarting to\b",
]


def gate_check_lt(lt: dict) -> dict:
    definition = lt["lt_definition"].lower()
    lt_id = lt["lt_id"]
    failures = []
    warnings = []

    # Gate 1: observable verb (with morphological normalisation)
    words = set(re.findall(r"\b[a-z]+\b", definition))
    norm_words = _normalise_verbs(words)
    matched_verbs = norm_words & OBSERVABLE_VERBS
    if not matched_verbs:
        failures.append({
            "gate": "observable_verb",
            "detail": f"No observable verb found in definition: '{lt['lt_definition']}'",
        })
    elif matched_verbs & MENTAL_STATE_VERBS:
        warnings.append({
            "gate": "observable_verb_mental_state",
            "detail": (
                f"Definition uses '{matched_verbs & MENTAL_STATE_VERBS}' — a mental state verb. "
                "Consider revising to a directly observable action (e.g. 'explain', 'apply', 'demonstrate')."
            ),
        })

    # Gate 2: inline examples in definition
    for pat in INLINE_EXAMPLE_PATTERNS:
        if re.search(pat, definition):
            warnings.append({
                "gate": "no_inline_examples",
                "detail": f"Inline example pattern '{pat}' found in definition. Review for over-specification.",
            })
            break

    # Gate 3: band progression coherence — check verbs increase in cognitive demand
    band_verbs = []
    for band in BANDS:
        stmt = lt["band_statements"].get(band)
        if stmt:
            v = set(re.findall(r"\b[a-z]+\b", stmt.lower())) & OBSERVABLE_VERBS
            band_verbs.append((band, v))

    # Simple heuristic: Band D should have at least one higher-order verb
    higher_order = {"evaluate", "analyse", "analyze", "justify", "synthesise", "synthesize",
                    "assess", "compare", "explain", "create", "design"}
    if band_verbs:
        band_d_verbs = dict(band_verbs).get("D", set())
        if band_d_verbs and not (band_d_verbs & higher_order):
            warnings.append({
                "gate": "progression_coherence",
                "detail": "Band D statement does not contain a higher-order cognitive verb.",
            })

    # Gate 4: N/A band check (LT 4.2 Band A is intentionally N/A — document it)
    na_bands = [band for band in BANDS if lt["band_statements"].get(band) is None]
    if na_bands:
        warnings.append({
            "gate": "band_coverage",
            "detail": f"Bands {na_bands} are N/A — intentional? Source note: 'not applicable at this developmental stage'",
            "severity": "informational",
        })

    return {
        "lt_id": lt_id,
        "lt_name": lt["lt_name"],
        "knowledge_type": lt["knowledge_type"],
        "gate_passed": len(failures) == 0,
        "failures": failures,
        "warnings": warnings,
        "flag_for_teacher_review": len(failures) > 0,
    }


def gate_check_band_statement(lt: dict, band: str) -> dict:
    stmt = lt["band_statements"].get(band)
    lt_id = lt["lt_id"]
    failures = []
    warnings = []

    if stmt is None:
        return {
            "lt_id": lt_id,
            "band": band,
            "statement": None,
            "gate_passed": True,
            "status": "na_by_design",
            "failures": [],
            "warnings": [],
        }

    stmt_lower = stmt.lower()
    words = set(re.findall(r"\b[a-z]+\b", stmt_lower))
    norm_words = _normalise_verbs(words)

    # Gate 1: observable verb (with morphological normalisation)
    if not norm_words & OBSERVABLE_VERBS:
        failures.append({
            "gate": "observable_verb",
            "detail": f"No observable verb in band {band} statement.",
        })

    # Gate 2: inline examples
    for pat in INLINE_EXAMPLE_PATTERNS:
        if re.search(pat, stmt_lower):
            warnings.append({
                "gate": "no_inline_examples",
                "detail": f"Inline example pattern '{pat}' found. Check whether examples are scope illustrations or separate sub-skills.",
            })
            break

    # Gate 3: T3 observation indicators — should describe observable behaviour, not reasoning
    if lt.get("is_observation_indicators"):
        reasoning_verbs = {"analyse", "analyze", "evaluate", "justify", "explain"}
        if words & reasoning_verbs:
            warnings.append({
                "gate": "t3_observable",
                "detail": (
                    f"T3 observation indicator contains reasoning-quality verb ({words & reasoning_verbs}). "
                    "Verify this is observable behaviour, not hidden reasoning quality."
                ),
            })

    return {
        "lt_id": lt_id,
        "band": band,
        "statement": stmt[:120] + "..." if len(stmt) > 120 else stmt,
        "gate_passed": len(failures) == 0,
        "failures": failures,
        "warnings": warnings,
    }


def run_all_gate_checks() -> dict:
    print("Phase 3: LT and band-statement gate checks...")
    lt_results = []
    band_results = []
    lt_fail_count = 0
    band_fail_count = 0

    for lt in LEARNING_TARGETS:
        lt_result = gate_check_lt(lt)
        lt_results.append(lt_result)
        if not lt_result["gate_passed"]:
            lt_fail_count += 1
            print(f"  LT GATE FAIL: {lt['lt_id']} — {[f['gate'] for f in lt_result['failures']]}")

        for band in BANDS:
            band_result = gate_check_band_statement(lt, band)
            band_results.append(band_result)
            if not band_result["gate_passed"]:
                band_fail_count += 1

    # Organise lt-by-band output
    lt_by_band: dict[str, dict] = {}
    for lt in LEARNING_TARGETS:
        lt_id = lt["lt_id"]
        lt_gate = next(r for r in lt_results if r["lt_id"] == lt_id)
        lt_by_band[lt_id] = {
            "lt_id": lt_id,
            "lt_name": lt["lt_name"],
            "competency_id": lt["competency_id"],
            "competency_name": COMP_BY_ID[lt["competency_id"]]["name"],
            "knowledge_type": lt["knowledge_type"],
            "assessment_route": lt["assessment_route"],
            "is_observation_indicators": lt["is_observation_indicators"],
            "prerequisite_lts": lt["prerequisite_lts"],
            "lt_gate": lt_gate,
            "bands": {},
        }
        for band in BANDS:
            stmt = lt["band_statements"].get(band)
            band_gate = next(
                (r for r in band_results if r["lt_id"] == lt_id and r["band"] == band), {}
            )
            lt_by_band[lt_id]["bands"][band] = {
                "band": band,
                "band_label": BAND_LABELS[band],
                "statement": stmt,
                "gate": band_gate,
            }

    print(f"  LT gate: {lt_fail_count}/{len(LEARNING_TARGETS)} failures")
    print(f"  Band gate: {band_fail_count}/{len(LEARNING_TARGETS) * len(BANDS)} failures")

    return {
        "source_slug": SOURCE_SLUG,
        "schema_version": SCHEMA_VERSION,
        "lt_gate_fail_count": lt_fail_count,
        "band_gate_fail_count": band_fail_count,
        "lts": lt_by_band,
    }


# ── Phase 4: Criterion Bank — Pass 1 (per LT × band decomposition) ────────────

DECOMPOSITION_RULES = """
CRITERION DECOMPOSITION RULES (apply strictly):

For TYPE 1 (Hierarchical) LTs:
  - Decompose into K (know) and U (understand) criteria
  - Each discrete concept or mechanism is a separate criterion
  - K and U at different bands are distinct criteria with prerequisite edges

For TYPE 2 (Horizontal) LTs:
  - Apply standard horizontal-domain decomposition
  - ONE criterion when: single cognitive act applied to a class of inputs
  - DECOMPOSE when: compound verbs at different cognitive levels, or distinct
    cognitive operations (describe vs evaluate vs justify)
  - Do NOT decompose on enumerated examples within a single act
  - Capture observable reasoning quality only — not dispositional orientation

For TYPE 3 (Dispositional) LTs:
  - Produce EXACTLY ONE observation-level criterion per band
  - The criterion_statement summarises the dispositional behaviour observable at that band
  - Use descriptors that are OBSERVABLE, not trait-based
  - Competency-level descriptors use single-point rubric language (observed/not yet observed scale):
      no_evidence: behaviour not yet observed
      emerging: behaviour observed occasionally with prompting
      developing: behaviour observed sometimes without prompting
      competent: behaviour consistently observed without prompting
      extending: behaviour consistently observed and student can articulate/model it

GENERAL RULES:
  - Each criterion must be independently demonstrable in its own task
  - Band scope: each criterion applies to ONE band's statement only
  - Criterion_label: 3–5 words
  - Decomposition_rationale: 1–2 sentences explaining why this many criteria
  - source_kud_item_ids: use "kud_{lt_id}_{band}_{n:02d}" format (reference KUD items)
"""

PASS1_SYSTEM = f"""You are a curriculum analyst producing a criterion bank for an
adaptive tutoring system. Your task is to decompose a Learning Target band statement
into one or more individually assessable criteria.

{DECOMPOSITION_RULES}

For competency-level descriptors use these word limits:
  no_evidence: ≤10 words
  emerging: ≤15 words
  developing: ≤20 words
  competent: ≤25 words (frame as success, never as "acceptable-but-deficient")
  extending: ≤20 words

Output ONLY valid JSON:
{{
  "criteria": [
    {{
      "criterion_statement": "one clear sentence stating what the learner can do",
      "criterion_label": "3-5 word label",
      "source_kud_item_ids": ["kud_ltid_band_01"],
      "competency_level_descriptors": {{
        "no_evidence": "...",
        "emerging": "...",
        "developing": "...",
        "competent": "...",
        "extending": "..."
      }},
      "decomposition_rationale": "why this many criteria (1-2 sentences)"
    }}
  ]
}}
Produce no other text. Only JSON."""


async def generate_criteria_for_lt_band(
    lt: dict,
    band: str,
    client: Any,
) -> list[dict]:
    stmt = lt["band_statements"].get(band)
    if stmt is None:
        return []

    lt_id = lt["lt_id"]
    lt_type = lt["knowledge_type"]

    # Build context: adjacent bands for progression context
    context_parts = []
    for b in BANDS:
        s = lt["band_statements"].get(b)
        marker = "← THIS BAND" if b == band else ""
        if s:
            context_parts.append(f"  Band {b} ({BAND_LABELS[b]}): {s} {marker}")
        else:
            context_parts.append(f"  Band {b}: N/A")

    user_msg = (
        f"LT ID: {lt_id} | Band: {band} ({BAND_LABELS[band]})\n"
        f"LT Name: {lt['lt_name']}\n"
        f"LT Definition: {lt['lt_definition']}\n"
        f"Type: {lt_type}\n\n"
        f"TARGET BAND STATEMENT (decompose this):\n{stmt}\n\n"
        f"PROGRESSION CONTEXT (adjacent bands, for coherence):\n"
        + "\n".join(context_parts)
    )

    stream = client.messages.stream(
        model=SONNET_MODEL,
        max_tokens=2048,
        system=PASS1_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    async with stream as s:
        text = await s.get_final_text()
        msg = await s.get_final_message()
    LEDGER.record(
        label="refauth_criterion",
        model=SONNET_MODEL,
        input_tokens=msg.usage.input_tokens,
        output_tokens=msg.usage.output_tokens,
    )

    parsed = extract_json_object(text)
    if not parsed:
        print(f"  WARNING: Criterion parse failed for {lt_id} Band {band}")
        return []

    raw_criteria = parsed.get("criteria", [])
    # Assign IDs and metadata
    result = []
    for i, crit in enumerate(raw_criteria, start=1):
        result.append({
            **crit,
            "_lt_id": lt_id,
            "_band": band,
            "_lt_type": lt_type,
        })
    return result


async def generate_all_criteria(client: Any) -> list[dict]:
    print("Phase 4: Criterion bank Pass 1 (per-LT × band decomposition)...")

    # Run concurrently per LT (sequential within LT for band ordering)
    async def process_lt(lt: dict) -> list[dict]:
        lt_criteria = []
        for band in BANDS:
            if lt["band_statements"].get(band) is None:
                continue
            crits = await generate_criteria_for_lt_band(lt, band, client)
            lt_criteria.extend(crits)
        return lt_criteria

    tasks = [process_lt(lt) for lt in LEARNING_TARGETS]
    results = await asyncio.gather(*tasks)

    all_raw = []
    for lt_crits in results:
        all_raw.extend(lt_crits)

    # Assign global criterion IDs
    criteria = []
    for n, crit in enumerate(all_raw, start=1):
        criterion_id = f"{SOURCE_SLUG}_crit_{n:04d}"
        criteria.append({
            "criterion_id": criterion_id,
            "associated_lt_ids": [crit["_lt_id"]],
            "band": crit["_band"],
            "band_label": BAND_LABELS[crit["_band"]],
            "lt_type": crit["_lt_type"],
            "strand": crit.get("_competency_id", "single_strand"),
            "criterion_statement": crit["criterion_statement"],
            "criterion_label": crit["criterion_label"],
            "source_kud_item_ids": crit.get("source_kud_item_ids", []),
            "competency_level_descriptors": crit["competency_level_descriptors"],
            "decomposition_rationale": crit.get("decomposition_rationale", ""),
            "prerequisite_criterion_ids": [],
            "prerequisite_edges_detail": [],
            "schema_version": SCHEMA_VERSION,
        })

    print(f"  Pass 1 complete: {len(criteria)} criteria generated")
    return criteria


# ── Phase 5: Criterion Bank — Pass 2 (Prerequisite Edges) ─────────────────────

# Cross-LT prerequisite pairs: (prerequisite_lt_id, dependent_lt_id)
# Source-stated in the framework document.
CROSS_LT_PREREQS = [
    ("lt_6_1", "lt_1_1"),  # C6 knowledge-contingency for C1 (source-stated)
    ("lt_6_1", "lt_3_1"),  # C6 knowledge-contingency for C3 (source-stated)
    ("lt_6_1", "lt_3_2"),  # C6 knowledge-contingency for C3 (inferred from comp-level)
    ("lt_6_1", "lt_6_2"),  # LT 6.1 explicit prerequisite for LT 6.2 (source-stated)
    ("lt_7_1", "lt_7_2"),  # LT 7.1 explicit prerequisite for LT 7.2 (source-stated)
]


async def add_prerequisite_edges(criteria: list[dict], client: Any = None) -> list[dict]:
    """Compute prerequisite edges deterministically.

    Pass 2 uses algorithmic edge computation rather than LLM for two reasons:
    1. The prerequisite structure is fully specified in the source document.
    2. LLM-generated edges for 107 criteria exceed reliable JSON output limits.

    Rules implemented:
    A. Within-LT band chain: for each LT, criteria at band X are prerequisites
       of ALL criteria at band X+1 for the same LT.
    B. Cross-LT source-stated: for each (prereq_lt, dep_lt) pair in CROSS_LT_PREREQS,
       criteria at band X for prereq_lt are prerequisites of criteria at band X
       for dep_lt (same-band only).
    """
    print("Phase 5: Criterion bank Pass 2 (prerequisite edges — deterministic)...")

    # Build index: (lt_id, band) → list of criterion_ids
    lt_band_index: dict[tuple[str, str], list[str]] = {}
    for c in criteria:
        lt_id = c["associated_lt_ids"][0] if c["associated_lt_ids"] else None
        band = c.get("band")
        if lt_id and band:
            key = (lt_id, band)
            lt_band_index.setdefault(key, []).append(c["criterion_id"])

    # Build prerequisite map: criterion_id → set of prerequisite criterion_ids
    prereq_map: dict[str, set[str]] = {c["criterion_id"]: set() for c in criteria}
    edge_details: dict[str, list[dict]] = {c["criterion_id"]: [] for c in criteria}

    # Rule A: within-LT band chain
    for lt in LEARNING_TARGETS:
        lt_id = lt["lt_id"]
        for i, band in enumerate(BANDS[:-1]):
            next_band = BANDS[i + 1]
            prev_crits = lt_band_index.get((lt_id, band), [])
            next_crits = lt_band_index.get((lt_id, next_band), [])
            for dep_crit in next_crits:
                for prereq_crit in prev_crits:
                    if prereq_crit != dep_crit:
                        prereq_map[dep_crit].add(prereq_crit)
                        edge_details[dep_crit].append({
                            "from": prereq_crit,
                            "to": dep_crit,
                            "edge_type": "within_lt_band",
                        })

    # Rule B: cross-LT source-stated prerequisites (same band)
    for prereq_lt, dep_lt in CROSS_LT_PREREQS:
        for band in BANDS:
            prereq_crits = lt_band_index.get((prereq_lt, band), [])
            dep_crits = lt_band_index.get((dep_lt, band), [])
            for dep_crit in dep_crits:
                for prereq_crit in prereq_crits:
                    if prereq_crit != dep_crit:
                        prereq_map[dep_crit].add(prereq_crit)
                        edge_details[dep_crit].append({
                            "from": prereq_crit,
                            "to": dep_crit,
                            "edge_type": "cross_lt_source_stated",
                        })

    # Apply to criteria
    for c in criteria:
        cid = c["criterion_id"]
        c["prerequisite_criterion_ids"] = sorted(prereq_map.get(cid, set()))
        c["prerequisite_edges_detail"] = edge_details.get(cid, [])

    total_edges = sum(len(c["prerequisite_criterion_ids"]) for c in criteria)
    print(f"  Pass 2 complete: {total_edges} prerequisite edges added (deterministic)")
    return criteria


# ── Phase 6: DAG Validation ───────────────────────────────────────────────────


def detect_cycles(criteria: list[dict]) -> list[list[str]]:
    graph: dict[str, list[str]] = {c["criterion_id"]: [] for c in criteria}
    for c in criteria:
        for prereq in c.get("prerequisite_criterion_ids", []):
            if prereq in graph:
                graph[prereq].append(c["criterion_id"])

    visited: set[str] = set()
    rec_stack: set[str] = set()
    cycles: list[list[str]] = []

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path + [neighbor])
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor) if neighbor in path else 0
                cycles.append(path[cycle_start:] + [neighbor])
        rec_stack.discard(node)

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node, [node])

    return cycles


def detect_self_loops(criteria: list[dict]) -> list[str]:
    return [
        c["criterion_id"]
        for c in criteria
        if c["criterion_id"] in c.get("prerequisite_criterion_ids", [])
    ]


def detect_unresolved_ids(criteria: list[dict]) -> list[dict]:
    valid_ids = {c["criterion_id"] for c in criteria}
    unresolved = []
    for c in criteria:
        for prereq in c.get("prerequisite_criterion_ids", []):
            if prereq not in valid_ids:
                unresolved.append({
                    "criterion_id": c["criterion_id"],
                    "unresolved_prereq": prereq,
                })
    return unresolved


def run_dag_validation(criteria: list[dict]) -> dict:
    print("Phase 6: DAG validation...")
    cycles = detect_cycles(criteria)
    self_loops = detect_self_loops(criteria)
    unresolved = detect_unresolved_ids(criteria)
    total_edges = sum(len(c.get("prerequisite_criterion_ids", [])) for c in criteria)

    dag_pass = not cycles and not self_loops and not unresolved
    status = "PASS" if dag_pass else "FAIL"
    print(f"  DAG validation: {status}")
    if cycles:
        print(f"  Cycles: {cycles}")
    if self_loops:
        print(f"  Self-loops: {self_loops}")
    if unresolved:
        print(f"  Unresolved IDs: {unresolved}")

    return {
        "dag_valid": dag_pass,
        "status": status,
        "total_criteria": len(criteria),
        "total_edges": total_edges,
        "cycles": cycles,
        "self_loops": self_loops,
        "unresolved_ids": unresolved,
    }


# ── Phase 7: Quality Report ───────────────────────────────────────────────────


def make_quality_report(
    lt_by_band: dict,
    kud_output: dict,
    dag_result: dict,
    criteria: list[dict],
) -> dict:
    lts_data = lt_by_band["lts"]

    # Count gate failures
    lt_failures = [lt for lt in lts_data.values() if not lt["lt_gate"]["gate_passed"]]
    lt_warnings = [
        lt for lt in lts_data.values()
        if lt["lt_gate"].get("warnings")
    ]

    # Band statement gate failures
    band_failures = []
    band_warnings = []
    for lt in lts_data.values():
        for band, bdata in lt["bands"].items():
            gate = bdata.get("gate", {})
            if gate.get("gate_passed") is False:
                band_failures.append({"lt_id": lt["lt_id"], "band": band, "failures": gate.get("failures", [])})
            if gate.get("warnings"):
                band_warnings.append({"lt_id": lt["lt_id"], "band": band, "warnings": gate.get("warnings", [])})

    # Criterion coverage
    t1_criteria = [c for c in criteria if c["lt_type"] == "Type 1"]
    t2_criteria = [c for c in criteria if c["lt_type"] == "Type 2"]
    t3_criteria = [c for c in criteria if c["lt_type"] == "Type 3"]

    # Flag for teacher review: LTs with gate failures
    flagged_for_review = []
    for lt in lts_data.values():
        if lt["lt_gate"]["gate_passed"] is False:
            flagged_for_review.append({
                "lt_id": lt["lt_id"],
                "lt_name": lt["lt_name"],
                "reason": "LT gate failure",
                "detail": lt["lt_gate"]["failures"],
            })

    lt_warnings_detail = [
        {
            "lt_id": lt["lt_id"],
            "lt_name": lt["lt_name"],
            "warnings": lt["lt_gate"]["warnings"],
        }
        for lt in lts_data.values()
        if lt["lt_gate"].get("warnings")
    ]

    return {
        "source_slug": SOURCE_SLUG,
        "session": "REAL-1",
        "generated_at": "2026-04-20",
        "lt_gate_summary": {
            "total_lts": len(lts_data),
            "gate_passed": len(lts_data) - len(lt_failures),
            "gate_failed": len(lt_failures),
            "has_warnings": len(lt_warnings),
            "failed_lts": [lt["lt_id"] for lt in lt_failures],
        },
        "band_statement_gate_summary": {
            "total_band_slots": sum(
                len(lt["bands"]) for lt in lts_data.values()
            ),
            "gate_failed": len(band_failures),
            "has_warnings": len(band_warnings),
        },
        "kud_summary": {
            "total_items": kud_output.get("total_kud_items", 0),
            "source_derived": kud_output.get("source_derived_count", 0),
            "ai_inferred": kud_output.get("ai_inferred_count", 0),
        },
        "criterion_bank_summary": {
            "total_criteria": len(criteria),
            "t1_criteria": len(t1_criteria),
            "t2_criteria": len(t2_criteria),
            "t3_criteria": len(t3_criteria),
            "total_edges": dag_result["total_edges"],
        },
        "dag_validation": dag_result,
        "flagged_for_teacher_review": flagged_for_review,
        "lt_gate_failures_detail": lt_failures,
        "lt_gate_warnings_detail": lt_warnings_detail,
        "band_gate_failures_detail": band_failures,
        "band_gate_warnings_detail": band_warnings,
    }


# ── Phase 8: Readable Outputs ─────────────────────────────────────────────────


def write_readable_outputs(
    lt_by_band: dict,
    kud_output: dict,
    criteria: list[dict],
    quality_report: dict,
) -> None:
    print("Phase 8: Writing readable outputs...")
    READABLE_DIR.mkdir(parents=True, exist_ok=True)

    # KUD table
    lines = ["# REAL School Budapest — KUD by Competency by Band\n\n"]
    for comp in COMPETENCIES:
        cid = comp["competency_id"]
        comp_data = kud_output.get("by_competency", {}).get(cid, {})
        lines.append(f"## {comp['name']}\n")
        lines.append(f"*{comp['definition']}*\n\n")
        for band in BANDS:
            band_data = comp_data.get("bands", {}).get(band, {})
            lt_items_map = band_data.get("lt_items", {})
            lines.append(f"### Band {band} — {BAND_LABELS[band]}\n\n")
            if not lt_items_map:
                lines.append("*No items classified for this band.*\n\n")
                continue
            for lt_id, lt_data in lt_items_map.items():
                lines.append(f"**{lt_data['lt_name']}**\n\n")
                items = lt_data.get("items", [])
                for item in items:
                    prov = "📌" if item.get("provenance") == "AI-inferred-from-LT" else "·"
                    lines.append(f"- {prov} [{item['category']}] {item['statement']}\n")
                lines.append("\n")
    with open(READABLE_DIR / "kud-charts.md", "w") as f:
        f.writelines(lines)

    # LT gate-check table
    lines = ["# REAL School Budapest — LT Gate-Check Results\n\n"]
    lts_data = lt_by_band["lts"]
    lines.append("| LT | Name | Type | Gate | Issues |\n")
    lines.append("|---|---|---|---|---|\n")
    for lt_id, lt_data in lts_data.items():
        gate = lt_data["lt_gate"]
        status = "✅ PASS" if gate["gate_passed"] else "❌ FAIL"
        issues = "; ".join(f["gate"] for f in gate.get("failures", []))
        issues += (" + " if issues and gate.get("warnings") else "") + "; ".join(
            w["gate"] for w in gate.get("warnings", [])
        )
        lines.append(f"| {lt_id} | {lt_data['lt_name']} | {lt_data['knowledge_type']} | {status} | {issues or '—'} |\n")
    lines.append("\n## Flagged for Teacher Review\n\n")
    flagged = quality_report.get("flagged_for_teacher_review", [])
    if flagged:
        for item in flagged:
            lines.append(f"- **{item['lt_id']}** ({item['lt_name']}): {item['reason']}\n")
            for d in item.get("detail", []):
                lines.append(f"  - {d['gate']}: {d['detail']}\n")
    else:
        lines.append("*No LTs flagged for teacher review.*\n")
    with open(READABLE_DIR / "lt-gate-check.md", "w") as f:
        f.writelines(lines)

    # Criterion bank markdown
    lines = ["# REAL School Budapest — Criterion Bank\n\n"]
    lines.append(f"Total criteria: {len(criteria)} | ")
    lines.append(f"T1: {quality_report['criterion_bank_summary']['t1_criteria']} | ")
    lines.append(f"T2: {quality_report['criterion_bank_summary']['t2_criteria']} | ")
    lines.append(f"T3 (observation): {quality_report['criterion_bank_summary']['t3_criteria']} | ")
    lines.append(f"Total edges: {quality_report['criterion_bank_summary']['total_edges']}\n\n")
    lines.append(f"DAG: {quality_report['dag_validation']['status']}\n\n")

    # Group by LT
    by_lt: dict[str, list[dict]] = {}
    for c in criteria:
        lt_id = c["associated_lt_ids"][0] if c["associated_lt_ids"] else "unknown"
        by_lt.setdefault(lt_id, []).append(c)

    for lt in LEARNING_TARGETS:
        lt_id = lt["lt_id"]
        comp_name = COMP_BY_ID[lt["competency_id"]]["name"]
        lt_criteria = by_lt.get(lt_id, [])
        lines.append(f"## {lt_id} — {lt['lt_name']} ({lt['knowledge_type']})\n")
        lines.append(f"*Competency: {comp_name}*\n\n")
        for c in lt_criteria:
            band = c.get("band", "?")
            lines.append(f"### {c['criterion_id']} — Band {band}: {c['criterion_label']}\n\n")
            lines.append(f"**Statement:** {c['criterion_statement']}\n\n")
            descrs = c.get("competency_level_descriptors", {})
            lines.append("| Level | Descriptor |\n|---|---|\n")
            for level in ["no_evidence", "emerging", "developing", "competent", "extending"]:
                lines.append(f"| {level.replace('_', ' ').title()} | {descrs.get(level, '—')} |\n")
            prereqs = c.get("prerequisite_criterion_ids", [])
            if prereqs:
                lines.append(f"\n**Prerequisite criteria:** {', '.join(prereqs)}\n")
            lines.append("\n")

    with open(READABLE_DIR / "criterion-bank.md", "w") as f:
        f.writelines(lines)

    print(f"  Readable outputs written to {READABLE_DIR}")


# ── Main ──────────────────────────────────────────────────────────────────────


async def main(phase: str = "all") -> None:
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    READABLE_DIR.mkdir(parents=True, exist_ok=True)

    client = get_async_client()

    # ── Phase 1: Architecture Diagnosis ───────────────────────────────────────
    if phase in ("all", "diagnosis"):
        print("\n=== Phase 1: Architecture Diagnosis ===")
        diagnosis = make_architecture_diagnosis()
        out = CORPUS_DIR / "architecture-diagnosis.json"
        out.write_text(json.dumps(diagnosis, indent=2, ensure_ascii=False))
        print(f"  Written: {out}")

    # ── Phase 2: KUD Classification ───────────────────────────────────────────
    if phase in ("all", "kud"):
        print("\n=== Phase 2: KUD Classification ===")
        kud_output, all_kud_items = await classify_all_kud(client)
        out = CORPUS_DIR / "kud-by-competency-by-band.json"
        out.write_text(json.dumps(kud_output, indent=2, ensure_ascii=False))
        print(f"  Written: {out} ({kud_output['total_kud_items']} items, "
              f"{kud_output['source_derived_count']} source-derived, "
              f"{kud_output['ai_inferred_count']} AI-inferred)")

    # ── Phase 3: Gate Checks ──────────────────────────────────────────────────
    if phase in ("all", "lt-gate"):
        print("\n=== Phase 3: LT & Band Statement Gate Checks ===")
        lt_by_band = run_all_gate_checks()
        out = CORPUS_DIR / "lt-by-band.json"
        out.write_text(json.dumps(lt_by_band, indent=2, ensure_ascii=False))
        print(f"  Written: {out}")

    # ── Phases 4–6: Criterion Bank ────────────────────────────────────────────
    if phase in ("all", "criteria"):
        print("\n=== Phase 4: Criterion Bank (Pass 1) ===")
        criteria = await generate_all_criteria(client)

        print("\n=== Phase 5: Criterion Bank (Pass 2 — Edges) ===")
        criteria = await add_prerequisite_edges(criteria, client)

        print("\n=== Phase 6: DAG Validation ===")
        dag_result = run_dag_validation(criteria)

        # Build criterion bank output
        by_comp: dict[str, list[dict]] = {}
        for c in criteria:
            lt_id = c["associated_lt_ids"][0] if c["associated_lt_ids"] else "unknown"
            lt = LT_BY_ID.get(lt_id)
            comp_id = lt["competency_id"] if lt else "unknown"
            by_comp.setdefault(comp_id, []).append(c)

        strand_summaries = []
        for comp in COMPETENCIES:
            cid = comp["competency_id"]
            comp_criteria = by_comp.get(cid, [])
            strand_summaries.append({
                "strand": cid,
                "strand_name": comp["name"],
                "criteria_count": len(comp_criteria),
            })

        criterion_bank = {
            "schema_version": SCHEMA_VERSION,
            "source_slug": SOURCE_SLUG,
            "source_name": SOURCE_NAME,
            "total_criteria": len(criteria),
            "dag_validation": dag_result,
            "strand_summaries": strand_summaries,
            "criteria": criteria,
        }

        out = CORPUS_DIR / "criterion-bank.json"
        out.write_text(json.dumps(criterion_bank, indent=2, ensure_ascii=False))
        print(f"  Written: {out} ({len(criteria)} criteria, {dag_result['total_edges']} edges)")

        if not dag_result["dag_valid"]:
            print("  ⚠️  DAG VALIDATION FAILED — review criterion-bank.json before committing")

    # ── Phase 7: Quality Report & Readable Outputs ────────────────────────────
    if phase in ("all", "quality"):
        # Load previously generated files if running quality phase alone
        def load_json(p: Path) -> Any:
            return json.loads(p.read_text()) if p.exists() else {}

        lt_by_band_loaded = load_json(CORPUS_DIR / "lt-by-band.json")
        kud_output_loaded = load_json(CORPUS_DIR / "kud-by-competency-by-band.json")
        cb_loaded = load_json(CORPUS_DIR / "criterion-bank.json")
        criteria_loaded = cb_loaded.get("criteria", [])
        dag_loaded = cb_loaded.get("dag_validation", {"dag_valid": False, "total_edges": 0})

        # If running inline from "all", use variables already in scope
        if phase == "all":
            lt_by_band_loaded = lt_by_band
            kud_output_loaded = kud_output
            criteria_loaded = criteria
            dag_loaded = dag_result

        quality = make_quality_report(
            lt_by_band_loaded, kud_output_loaded, dag_loaded, criteria_loaded
        )
        out = CORPUS_DIR / "quality-report.json"
        out.write_text(json.dumps(quality, indent=2, ensure_ascii=False))
        print(f"\nWritten: {out}")

        print("\n=== Phase 8: Readable Outputs ===")
        write_readable_outputs(
            lt_by_band_loaded, kud_output_loaded, criteria_loaded, quality
        )

    # ── Token usage summary ───────────────────────────────────────────────────
    summary = LEDGER.summary_line()
    print("\n=== Token Usage ===")
    print(f"  {summary}")


if __name__ == "__main__":
    arg_phase = "all"
    if len(sys.argv) > 2 and sys.argv[1] == "--phase":
        arg_phase = sys.argv[2]
    elif len(sys.argv) > 1:
        arg_phase = sys.argv[1]

    asyncio.run(main(phase=arg_phase))
