"""Deterministic tests that band/indicator prompt builders adapt to source-native bands.

The system prompts, user prompts, and output validators MUST be
parameterised on the source's ``ProgressionStructure`` rather than
hardcoding A-D. These tests confirm that:

- The Welsh CfW Progression Step labels appear in the system prompt
  and the user prompt.
- A single-band source (Common Core Grade 7) emits a single-statement
  schema and rejects multi-band output via the validator.
- The validator round-trips well-formed JSON for both shapes.
"""

from __future__ import annotations

from curriculum_harness.reference_authoring.lt.band_prompts import (
    build_system_prompt as build_band_system_prompt,
    build_user_prompt as build_band_user_prompt,
)
from curriculum_harness.reference_authoring.lt.generate_band_statements import (
    _validate_run as validate_band_run,
)
from curriculum_harness.reference_authoring.lt.indicator_prompts import (
    build_system_prompt as build_indicator_system_prompt,
)
from curriculum_harness.reference_authoring.lt.generate_observation_indicators import (
    _validate_run as validate_indicator_run,
)
from curriculum_harness.reference_authoring.progression import (
    ProgressionStructure,
)


def _welsh_progression() -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=[
            "Progression Step 1",
            "Progression Step 2",
            "Progression Step 3",
            "Progression Step 4",
            "Progression Step 5",
        ],
        band_count=5,
        age_range_hint="ages 3-16",
        source_type="welsh_cfw_aole",
        detection_confidence="high",
        detection_rationale="test fixture",
        band_self_reflection_prompts={
            "Progression Step 1": "ps1 prompt",
            "Progression Step 2": "ps2 prompt",
            "Progression Step 3": "ps3 prompt",
            "Progression Step 4": "ps4 prompt",
            "Progression Step 5": "ps5 prompt",
        },
    )


def _grade7_progression() -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=["Grade 7"],
        band_count=1,
        age_range_hint="ages 12-13",
        source_type="us_common_core_grade",
        detection_confidence="high",
        detection_rationale="test fixture",
        band_self_reflection_prompts={"Grade 7": "g7 prompt"},
    )


def test_band_system_prompt_welsh_lists_all_progression_steps() -> None:
    sp = build_band_system_prompt(_welsh_progression())
    for label in [
        "Progression Step 1",
        "Progression Step 2",
        "Progression Step 3",
        "Progression Step 4",
        "Progression Step 5",
    ]:
        assert label in sp, f"missing band label {label!r} in system prompt"
    assert "A-D" not in sp
    assert "ages 5-14" not in sp
    assert "Exactly 5 band statements" in sp


def test_band_system_prompt_single_grade_collapses_to_one_statement() -> None:
    sp = build_band_system_prompt(_grade7_progression())
    assert "Grade 7" in sp
    assert "single grade level" in sp
    assert "Exactly 1 band statement entry" in sp
    assert "Exactly 5 band statements" not in sp


def test_band_user_prompt_includes_progression_summary() -> None:
    up = build_band_user_prompt(
        lt_name="Identifying Healthy Choices",
        lt_definition="I can identify which everyday choices support health.",
        knowledge_type="Type 1",
        competency_name="Healthy Choices",
        progression=_welsh_progression(),
    )
    assert "welsh_cfw_aole" in up
    assert "Progression Step 1, Progression Step 2" in up


def test_band_validator_accepts_welsh_progression_step_run() -> None:
    welsh = _welsh_progression()
    obj = {
        "band_statements": [
            {"band": "Progression Step 1", "statement": "I can name one healthy everyday choice with prompting."},
            {"band": "Progression Step 2", "statement": "I can describe healthy everyday choices in familiar settings."},
            {"band": "Progression Step 3", "statement": "I can compare healthy and unhealthy choices in different settings."},
            {"band": "Progression Step 4", "statement": "I can analyse choices and explain how they support my long-term health."},
            {"band": "Progression Step 5", "statement": "I can evaluate complex choices, justify decisions, and apply reasoning across unfamiliar settings."},
        ]
    }
    validated = validate_band_run(obj, progression=welsh)
    assert validated is not None
    assert [v["band"] for v in validated] == welsh.band_labels


def test_band_validator_rejects_a_d_run_against_welsh_progression() -> None:
    welsh = _welsh_progression()
    obj = {
        "band_statements": [
            {"band": "A", "statement": "I can identify with prompting in familiar settings always."},
            {"band": "B", "statement": "I can describe with some independence in familiar contexts often."},
            {"band": "C", "statement": "I can compare independently in typical contexts and explain reasoning."},
            {"band": "D", "statement": "I can justify across unfamiliar contexts using reasoning and transfer skills."},
        ]
    }
    validated = validate_band_run(obj, progression=welsh)
    assert validated is None


def test_band_validator_accepts_single_grade_run() -> None:
    g7 = _grade7_progression()
    obj = {
        "band_statements": [
            {"band": "Grade 7", "statement": "I can apply unit-rate reasoning to solve grade-appropriate proportional problems."}
        ]
    }
    validated = validate_band_run(obj, progression=g7)
    assert validated is not None
    assert validated[0]["band"] == "Grade 7"


def test_band_validator_single_grade_rejects_multi_band_run() -> None:
    g7 = _grade7_progression()
    obj = {
        "band_statements": [
            {"band": "Grade 7", "statement": "I can apply unit-rate reasoning to solve proportional problems carefully."},
            {"band": "Grade 8", "statement": "I can apply unit-rate reasoning to grade 8 contexts as well too."},
        ]
    }
    assert validate_band_run(obj, progression=g7) is None


def test_indicator_system_prompt_welsh_lists_all_progression_steps() -> None:
    sp = build_indicator_system_prompt(_welsh_progression())
    for label in [
        "Progression Step 1",
        "Progression Step 2",
        "Progression Step 3",
        "Progression Step 4",
        "Progression Step 5",
    ]:
        assert label in sp
    assert "Exactly 5 band entries" in sp


def test_indicator_system_prompt_single_grade_collapses() -> None:
    sp = build_indicator_system_prompt(_grade7_progression())
    assert "Grade 7" in sp
    assert "Exactly 1 band entry" in sp
    assert "Exactly 5 band entries" not in sp


def test_indicator_validator_accepts_single_grade_run() -> None:
    g7 = _grade7_progression()
    obj = {
        "bands": [
            {
                "band": "Grade 7",
                "observable_behaviours": [
                    "The student initiates discussion of unit-rate reasoning when a relevant context appears.",
                    "The student persists in checking proportional reasoning before accepting an answer.",
                ],
            }
        ],
        "parent_prompts": [
            "What have you noticed when your child is checking calculations at home?",
            "When does your child stop to compare answers to estimates?",
            "Where do you see your child using ratios in everyday tasks?",
        ],
        "developmental_conversation_protocol": "Teacher-student conversation reviews evidence of orientation across contexts.",
    }
    validated = validate_indicator_run(obj, progression=g7)
    assert validated is not None
    assert validated["bands"][0]["band"] == "Grade 7"


def test_indicator_validator_rejects_a_d_run_against_welsh() -> None:
    welsh = _welsh_progression()
    obj = {
        "bands": [
            {"band": "A", "observable_behaviours": ["The student tries.", "The student tries again."]},
        ],
        "parent_prompts": ["a", "b", "c"],
        "developmental_conversation_protocol": "x",
    }
    assert validate_indicator_run(obj, progression=welsh) is None
