"""Detect a curriculum source's native progression structure.

DESIGN PRINCIPLE — DOMAIN-AGNOSTIC

The reference-authoring pipeline does NOT impose any specific school's
band framework (such as REAL School Budapest's A-D bands across ages
5-14) on the outputs it produces from external curriculum sources.
Each source has its own native progression structure — Welsh
Curriculum for Wales uses Progression Steps 1-5; US Common Core uses
US grade levels; Scottish CfE uses Early/First/Second/Third/Fourth
Levels; English National Curriculum uses Key Stages 1-4; New Zealand
Curriculum uses Levels 1-8; Ontario uses Canadian grade levels. The
LT authoring skill's "typically A-D across ages 5-14" example is a
REAL-School calibration, not a mandatory output format.

This module reads the source (via its ``SourceInventory``) and returns
a ``ProgressionStructure`` describing the source's own bands. Single-
band sources (a single Common Core grade, a single Ontario grade) are
first-class — ``band_count = 1`` and downstream stages produce a single
statement per LT rather than a band progression.

DETECTION ORDER

1. Lookup by ``source_reference`` URL host + path against a curated
   table of known jurisdictions. This is the high-confidence path. Age
   ranges in the lookup are taken from each issuing body's own
   published documentation, not guessed.
2. Lookup by ``source_slug`` pattern as a backup signal.
3. Source-text inspection: scan ``content_blocks`` for explicit
   progression markers ("Progression Step", "Grade", "Key Stage",
   "Level"). This is the medium-confidence path; it sets
   ``progression_structure_uncertain`` downstream.
4. If nothing matches, raise ``ProgressionDetectionError`` with a
   diagnostic. The pipeline must NOT silently default to A-D.

DETECTION CONFIDENCE → STABILITY FLAG

- ``high``: the structure is taken from the curated lookup. Outputs
  are emitted without a progression-structure-uncertainty flag.
- ``medium``: the structure was inferred from source-text markers.
  Outputs are flagged ``progression_structure_uncertain`` so a
  reviewer knows the band framework itself may need verification.
- ``low``: a permissive fallback was applied because nothing
  authoritative matched. The pipeline normally halts before this; if
  it ever fires, the same uncertainty flag applies.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urlparse

from curriculum_harness.reference_authoring.types import SourceInventory

PROGRESSION_DETECTION_VERSION = "0.1.0"

DETECTION_CONFIDENCE_LEVELS = ("high", "medium", "low")

PROGRESSION_STRUCTURE_UNCERTAIN_FLAG = "progression_structure_uncertain"


class ProgressionDetectionError(RuntimeError):
    """Raised when no progression structure can be detected for a source.

    The pipeline does NOT default to A-D. A halt with a specific
    diagnostic is the correct behaviour; the operator must add the
    source to the lookup table or correct its source_reference / slug.
    """


@dataclass
class ProgressionStructure:
    """The native progression structure of a single curriculum source.

    For a multi-band source (Welsh CfW, Scottish CfE, etc.)
    ``band_labels`` lists the source's own band names in developmental
    order and ``band_count`` matches its length.

    For a single-band source (one Common Core grade, one Ontario
    grade, etc.) ``band_count == 1`` and ``band_labels`` is a single-
    element list with the grade label. Downstream generators interpret
    this as "no progression sequence inside the source — produce a
    single statement per LT at this grade level".

    ``band_details`` holds per-band developmental-indexing metadata (one
    dict per band, in the same order as ``band_labels``). Each dict has:
      - ``label``: the band label (matches ``band_labels[i]``).
      - ``approximate_age_range``: source-specified age range, or null.
      - ``approximate_grade_year``: source-specified grade/year, or null.
      - ``developmental_descriptor``: brief text from the source's own
        documentation describing what learners at this band are
        developmentally expected to do.

    ``progression_philosophy`` describes how progression should be
    interpreted for this source — is it a set of annual grade targets, a
    set of developmental waypoints, a phase-based curriculum, etc.? This
    text is drawn from the issuing jurisdiction's own guidance so that
    any reader — including someone unfamiliar with the jurisdiction — can
    understand the source's progression model without prior knowledge.
    """

    band_labels: list[str]
    band_count: int
    age_range_hint: str
    source_type: str
    detection_confidence: str
    detection_rationale: str
    band_self_reflection_prompts: dict[str, str] = field(default_factory=dict)
    band_details: list[dict] = field(default_factory=list)
    progression_philosophy: str = ""
    source_reference: str = ""
    source_slug: str = ""
    detection_module_version: str = PROGRESSION_DETECTION_VERSION

    def is_single_band(self) -> bool:
        return self.band_count == 1

    def uncertain(self) -> bool:
        return self.detection_confidence in ("medium", "low")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Curated jurisdiction lookup. Each entry's ``age_range_hint`` is taken
# from the issuing jurisdiction's own published documentation, not
# guessed. Citations:
#
# - Welsh Curriculum for Wales: Progression Steps 1-5 across ages 3 to
#   16 — Welsh Government, Curriculum for Wales overview, including the
#   "Designing your curriculum" guidance and the Progression Code 2022
#   (statutory under the Curriculum and Assessment (Wales) Act 2021),
#   published at hwb.gov.wales.
# - US Common Core State Standards: K-12 grade-level standards
#   (Council of Chief State School Officers, CCSSO; Common Core State
#   Standards Initiative). Grade 7 = US Grade 7, age band 12-13 per
#   the Initiative's age/grade alignment.
# - Ontario K-8 curriculum, Grade 7: ages 12-13 per the Ontario
#   Ministry of Education's K-12 schedule.
# - Scottish CfE: Early / First / Second / Third / Fourth Levels +
#   Senior Phase — Education Scotland, "Building the Curriculum" and
#   the CfE benchmarks. Age guidance per Education Scotland: Early
#   3-6, First 5/6-8/9, Second 8/9-11/12, Third 11/12-13/14,
#   Fourth 13/14-14/15, Senior Phase 15-18.
# - England National Curriculum: Key Stages 1-4 per DfE statutory
#   framework. KS1 5-7, KS2 7-11, KS3 11-14, KS4 14-16.
# - New Zealand Curriculum: Levels 1-8 per Ministry of Education NZ
#   "The New Zealand Curriculum"; ages roughly 5-18 across Levels.
# ---------------------------------------------------------------------------

WELSH_CFW_PS_LABELS = [
    "Progression Step 1",
    "Progression Step 2",
    "Progression Step 3",
    "Progression Step 4",
    "Progression Step 5",
]

# Self-reflection prompts for Welsh CfW Progression Steps. Calibrated
# to the cognitive demand expected at each Step in the Welsh
# Government's own Descriptions of Learning across Areas of Learning
# and Experience: PS1 names a single observation; PS2 notices simple
# patterns; PS3 compares own and others' perspectives; PS4 analyses
# patterns across two or more contexts; PS5 articulates developmental
# trajectories and reasoned values.
WELSH_CFW_PS_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Progression Step 1": (
        "Tell me about a time this term when you tried something new. What did you do, and how did it feel?"
    ),
    "Progression Step 2": (
        "Describe one thing you have noticed about yourself this term. When does it happen, and when does it not?"
    ),
    "Progression Step 3": (
        "Compare what you have noticed in yourself with what your teacher or family has noticed. Where do these accounts agree, and where do they differ?"
    ),
    "Progression Step 4": (
        "Analyse a pattern you can see in yourself across two or more different settings this term. What changes across settings, and why do you think it changes?"
    ),
    "Progression Step 5": (
        "Trace how your understanding of yourself in this area has developed over time. What values now guide how you act, and what would you still like to develop?"
    ),
}

# Per-band developmental-indexing metadata for Welsh CfW Progression Steps.
# Approximate ages and developmental descriptors drawn from the Welsh
# Government's statutory Descriptions of Learning and the Curriculum for
# Wales guidance published at hwb.gov.wales. The "up to age X" framing
# is the Welsh Government's own: each PS is a reference waypoint for
# what learners are typically expected to achieve by the associated age,
# not a year-group gate. Descriptions are rendered from the AoLE-spanning
# conceptual language in the statutory guidance, not from any single AoLE.
WELSH_CFW_PS_BAND_DETAILS: list[dict] = [
    {
        "label": "Progression Step 1",
        "approximate_age_range": "up to age 5",
        "approximate_grade_year": None,
        "developmental_descriptor": (
            "Learners explore and experience the world through play, sensory "
            "engagement, and adult-supported activity. They begin to develop "
            "awareness of themselves and their immediate environment."
        ),
    },
    {
        "label": "Progression Step 2",
        "approximate_age_range": "up to age 8",
        "approximate_grade_year": None,
        "developmental_descriptor": (
            "Learners develop confidence and work with increasing independence. "
            "They make connections between experiences and begin to articulate "
            "thoughts about themselves and others."
        ),
    },
    {
        "label": "Progression Step 3",
        "approximate_age_range": "up to age 11",
        "approximate_grade_year": None,
        "developmental_descriptor": (
            "Learners build capacity to manage change and transition. They "
            "consider different perspectives, manage emotions with growing "
            "skill, and act with increasing autonomy."
        ),
    },
    {
        "label": "Progression Step 4",
        "approximate_age_range": "up to age 14",
        "approximate_grade_year": None,
        "developmental_descriptor": (
            "Learners demonstrate increasing maturity in navigating complex "
            "relationships and situations. They develop resilience, critical "
            "thinking, and awareness of their impact on others."
        ),
    },
    {
        "label": "Progression Step 5",
        "approximate_age_range": "up to age 16",
        "approximate_grade_year": None,
        "developmental_descriptor": (
            "Learners evaluate their own learning, act ethically and "
            "sustainably, and engage with wider society. They exercise "
            "independent judgement and articulate reasoned values."
        ),
    },
]

# Progression philosophy for Welsh CfW — drawn from the Welsh Government's
# Curriculum and Assessment (Wales) Act 2021 and the Curriculum for Wales
# framework guidance published at hwb.gov.wales.
WELSH_CFW_PROGRESSION_PHILOSOPHY = (
    "Progression Steps are reference waypoints, not annual targets. Learners "
    "progress at different rates and may be at different Progression Steps for "
    "different Areas of Learning and Experience. Each Step describes what "
    "learners are typically expected to achieve by the associated age; they are "
    "not grade-level checklists. Per Welsh Government statutory specification "
    "under the Curriculum and Assessment (Wales) Act 2021."
)

# Scottish CfE Levels. Self-reflection prompts mapped by analogous
# cognitive demand bands.
SCOTTISH_CFE_LEVEL_LABELS = [
    "Early Level",
    "First Level",
    "Second Level",
    "Third Level",
    "Fourth Level",
    "Senior Phase",
]
SCOTTISH_CFE_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Early Level": (
        "Tell me about a time you tried something at school. What did you do, and how did it feel?"
    ),
    "First Level": (
        "Describe one thing you have noticed about yourself this term. When does it happen most?"
    ),
    "Second Level": (
        "Compare what you have noticed about yourself with what your teacher or family has noticed."
    ),
    "Third Level": (
        "Analyse a pattern you can see in yourself across two or more settings. What changes, and why?"
    ),
    "Fourth Level": (
        "Trace how your understanding of yourself in this area has developed across this stage of your learning."
    ),
    "Senior Phase": (
        "Articulate the values that now guide how you act in this area, the evidence those values rest on, and what you still want to develop."
    ),
}

# Per-band developmental metadata for Scottish CfE.
# Age ranges per Education Scotland's "Building the Curriculum" documentation
# and CfE benchmarks (education.gov.scot). P = primary year, S = secondary year.
SCOTTISH_CFE_BAND_DETAILS: list[dict] = [
    {
        "label": "Early Level",
        "approximate_age_range": "ages 3-6",
        "approximate_grade_year": "Pre-school to P1",
        "developmental_descriptor": (
            "Learners are exploring and developing through play and first "
            "structured experiences. They are building foundational literacy, "
            "numeracy, and awareness of the world immediately around them."
        ),
    },
    {
        "label": "First Level",
        "approximate_age_range": "ages 5/6-8/9",
        "approximate_grade_year": "P2-P4",
        "developmental_descriptor": (
            "Learners develop confidence and begin working more independently. "
            "They build core skills across literacy, numeracy, and the sciences, "
            "and develop growing awareness of themselves and others."
        ),
    },
    {
        "label": "Second Level",
        "approximate_age_range": "ages 7/8-10/11",
        "approximate_grade_year": "P4-P7",
        "developmental_descriptor": (
            "Learners engage with increasingly complex concepts and begin to "
            "apply skills across different contexts. They develop analytical "
            "thinking and a broader understanding of their community and world."
        ),
    },
    {
        "label": "Third Level",
        "approximate_age_range": "ages 10/11-13/14",
        "approximate_grade_year": "S1-S3",
        "developmental_descriptor": (
            "Learners apply skills and knowledge with increasing sophistication. "
            "They develop critical thinking, independent inquiry, and the capacity "
            "to understand multiple perspectives."
        ),
    },
    {
        "label": "Fourth Level",
        "approximate_age_range": "ages 12/13-14/15",
        "approximate_grade_year": "S1-S3",
        "developmental_descriptor": (
            "Learners engage with challenging and abstract content, demonstrating "
            "depth of understanding and the ability to evaluate, synthesise, and "
            "transfer learning across contexts."
        ),
    },
    {
        "label": "Senior Phase",
        "approximate_age_range": "ages 15-18",
        "approximate_grade_year": "S4-S6",
        "developmental_descriptor": (
            "Learners pursue qualifications and specialised study aligned to "
            "post-school ambitions. They exercise high-level critical thinking, "
            "self-direction, and articulation of developed values and capabilities."
        ),
    },
]

SCOTTISH_CFE_PROGRESSION_PHILOSOPHY = (
    "Curriculum for Excellence levels are broad developmental bands, each spanning "
    "approximately 2-3 years. Progression within a level is described through "
    "Experiences and Outcomes; learners may progress through a level at different "
    "rates and some may continue to develop within a level across more than one year. "
    "The levels are not tied to specific calendar years; ages shown are indicative "
    "guidance, not prescription. Per Education Scotland's Building the Curriculum "
    "and CfE benchmarks documentation."
)

# England NC Key Stages.
ENGLAND_KS_LABELS = ["Key Stage 1", "Key Stage 2", "Key Stage 3", "Key Stage 4"]
# Per-band developmental metadata for England NC Key Stages.
# Ages and year groups per DfE statutory national curriculum framework.
ENGLAND_KS_BAND_DETAILS: list[dict] = [
    {
        "label": "Key Stage 1",
        "approximate_age_range": "ages 5-7",
        "approximate_grade_year": "Years 1-2",
        "developmental_descriptor": (
            "Learners develop foundational skills in reading, writing, and "
            "mathematics. They explore the world through structured play and "
            "guided inquiry and begin to develop awareness of themselves and others."
        ),
    },
    {
        "label": "Key Stage 2",
        "approximate_age_range": "ages 7-11",
        "approximate_grade_year": "Years 3-6",
        "developmental_descriptor": (
            "Learners build fluency in core subjects and develop growing capacity "
            "for independent learning. They engage with increasingly complex ideas "
            "and develop analytical and problem-solving skills."
        ),
    },
    {
        "label": "Key Stage 3",
        "approximate_age_range": "ages 11-14",
        "approximate_grade_year": "Years 7-9",
        "developmental_descriptor": (
            "Learners engage with a broad curriculum across specialised subject "
            "disciplines. They develop critical thinking, abstract reasoning, and "
            "the capacity to work independently and collaboratively."
        ),
    },
    {
        "label": "Key Stage 4",
        "approximate_age_range": "ages 14-16",
        "approximate_grade_year": "Years 10-11",
        "developmental_descriptor": (
            "Learners pursue GCSE qualifications and develop depth of understanding "
            "in their chosen subjects. They apply sophisticated reasoning, extended "
            "writing, and research skills in preparation for post-16 pathways."
        ),
    },
]

ENGLAND_NC_PROGRESSION_PHILOSOPHY = (
    "Key Stages represent statutory curriculum phases defined by the DfE national "
    "curriculum framework. Progression within a Key Stage is described through "
    "programmes of study and attainment targets; detailed within-KS sequencing is "
    "a school and teacher decision. Ages shown are statutory entry points per the "
    "DfE national curriculum statutory framework (England)."
)

ENGLAND_KS_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Key Stage 1": (
        "Tell me about a time you tried something hard. What did you do, and how did it feel?"
    ),
    "Key Stage 2": (
        "Describe one thing you have noticed about yourself this term. When does it happen?"
    ),
    "Key Stage 3": (
        "Compare what you have noticed about yourself with what your teachers or family have noticed."
    ),
    "Key Stage 4": (
        "Analyse how your understanding of yourself in this area has developed, and articulate what now guides how you act."
    ),
}

# Per-band developmental metadata for NZ Curriculum Levels 1-8.
# Year groups and ages per Ministry of Education NZ, "The New Zealand Curriculum"
# (2007, revised 2023). Ages are indicative ranges from the MoE documentation.
NZ_BAND_DETAILS: list[dict] = [
    {
        "label": "Level 1",
        "approximate_age_range": "ages 5-7",
        "approximate_grade_year": "Years 1-2",
        "developmental_descriptor": (
            "Learners explore the world through play and structured first "
            "experiences, developing foundational literacy, numeracy, and "
            "awareness of their immediate environment and community."
        ),
    },
    {
        "label": "Level 2",
        "approximate_age_range": "ages 7-9",
        "approximate_grade_year": "Years 3-4",
        "developmental_descriptor": (
            "Learners develop confidence in core skills and begin to work "
            "with greater independence. They make connections across subjects "
            "and grow in their understanding of community and relationships."
        ),
    },
    {
        "label": "Level 3",
        "approximate_age_range": "ages 9-11",
        "approximate_grade_year": "Years 5-6",
        "developmental_descriptor": (
            "Learners engage with more complex concepts and develop analytical "
            "thinking. They build capacity to investigate questions and consider "
            "multiple perspectives."
        ),
    },
    {
        "label": "Level 4",
        "approximate_age_range": "ages 11-13",
        "approximate_grade_year": "Years 7-8",
        "developmental_descriptor": (
            "Learners apply knowledge and skills across increasingly abstract "
            "contexts. They develop critical inquiry, self-management, and "
            "growing awareness of local and global issues."
        ),
    },
    {
        "label": "Level 5",
        "approximate_age_range": "ages 13-15",
        "approximate_grade_year": "Years 9-10",
        "developmental_descriptor": (
            "Learners engage with specialised subject disciplines and develop "
            "sophisticated analytical and evaluative skills. They begin to "
            "exercise more autonomous learning and judgment."
        ),
    },
    {
        "label": "Level 6",
        "approximate_age_range": "ages 15-17",
        "approximate_grade_year": "Years 11-12",
        "developmental_descriptor": (
            "Learners pursue qualifications and specialised study. They apply "
            "complex reasoning, extended research, and strong self-direction."
        ),
    },
    {
        "label": "Level 7",
        "approximate_age_range": "ages 16-18",
        "approximate_grade_year": "Years 12-13",
        "developmental_descriptor": (
            "Learners demonstrate high-level conceptual understanding and "
            "independent inquiry. They evaluate, synthesise, and transfer "
            "learning across domains."
        ),
    },
    {
        "label": "Level 8",
        "approximate_age_range": "ages 17-18",
        "approximate_grade_year": "Year 13",
        "developmental_descriptor": (
            "Learners exercise the highest level of critical thinking, "
            "intellectual independence, and values articulation in preparation "
            "for tertiary education and adult participation."
        ),
    },
]

NZ_CURRICULUM_PROGRESSION_PHILOSOPHY = (
    "The New Zealand Curriculum organises achievement objectives into eight levels, "
    "each spanning approximately two school years. Levels represent expected "
    "achievement rather than age-locked gates; learners may progress at different "
    "rates. Year groups shown are indicative, per Ministry of Education NZ guidance. "
    "Within each level, progression is described through achievement objectives and "
    "increasingly complex learning contexts."
)

# NZ Curriculum Levels 1-8.
NZ_LEVEL_LABELS = [f"Level {i}" for i in range(1, 9)]


def _nz_self_reflection_prompts() -> dict[str, str]:
    base = {
        1: "Tell me about a time you tried something at school. What did you do?",
        2: "Tell me about a time you tried something hard. What did you do, and how did it feel?",
        3: "Describe one thing you have noticed about yourself this term.",
        4: "Compare what you have noticed about yourself with what your teacher or family has noticed.",
        5: "Compare what you have noticed in yourself across two settings.",
        6: "Analyse a pattern you can see in yourself across two or more settings.",
        7: "Trace how your understanding of yourself in this area has developed over time.",
        8: "Articulate the values that now guide how you act in this area, and what you still want to develop.",
    }
    return {f"Level {i}": text for i, text in base.items()}


def _common_core_grade_band_details(grade: int) -> list[dict]:
    """Per-band details for a single Common Core grade.

    Common Core State Standards (CCSSO) publish at grade-level granularity.
    Age range calculated as grade+5 to grade+6 per CCSSO alignment guidance.
    Descriptor draws from the Common Core Mathematics progressions documents
    and the Standards' own grade-level introductory text.
    """
    label = f"Grade {grade}"
    age_low = grade + 5
    age_high = grade + 6
    descriptors: dict[int, str] = {
        7: (
            "Grade 7 learners extend proportional reasoning from Grades 5-6 to "
            "analyse proportional relationships using equations, tables, and graphs, "
            "and apply them to multi-step ratio and percent problems. This domain "
            "is foundational for linear algebra and functional thinking in Grade 8."
        ),
    }
    descriptor = descriptors.get(
        grade,
        (
            f"Grade {grade} learners work toward end-of-year mastery of the "
            f"standards specified for this grade. Common Core publishes at "
            f"grade-level granularity; within-year progression is a school and "
            f"teacher decision."
        ),
    )
    return [
        {
            "label": label,
            "approximate_age_range": f"ages {age_low}-{age_high}",
            "approximate_grade_year": label,
            "developmental_descriptor": descriptor,
        }
    ]


def _common_core_progression_philosophy() -> str:
    """Progression philosophy for Common Core single-grade sources.

    Drawn from the CCSSO Common Core State Standards Initiative documentation
    and the Mathematics Progressions documents (Progressions for the Common
    Core State Standards in Mathematics, Institute for Mathematics and
    Education).
    """
    return (
        "Grade-level standards published at grade-level granularity only. Each "
        "standard is expected to be mastered by the end of the named grade. "
        "Sub-grade progression (quarterly, monthly) is a pedagogical decision made "
        "by districts and schools, not by the standards themselves. The presence of "
        "a single band in this reference output reflects the source's own "
        "granularity, not an absence of internal structure within the teaching year."
    )


def _ontario_grade_band_details(grade: int) -> list[dict]:
    """Per-band details for a single Ontario grade.

    Age range per Ontario Ministry of Education K-12 schedule. Grade 7 is
    the first year of the Intermediate level (Grades 7-8), following the
    Junior level (Grades 4-6). Descriptor draws from the Ministry's
    K-12 Social Studies, History and Geography curriculum documentation
    and from the Ontario Curriculum framework overview.
    """
    label = f"Grade {grade}"
    age_low = grade + 5
    age_high = grade + 6
    descriptors: dict[int, str] = {
        7: (
            "Grade 7 learners are in the first year of the Intermediate level "
            "(Grades 7-8). In History, they examine social, political, economic, "
            "and legal changes in Canada between 1713 and 1850, including New France "
            "and British North America. They apply disciplinary historical-thinking "
            "concepts (Continuity and Change, Cause and Consequence, Historical "
            "Perspective, Historical Significance) and inquiry skills to analyse "
            "primary and secondary sources."
        ),
    }
    descriptor = descriptors.get(
        grade,
        (
            f"Grade {grade} learners work toward year-end expectations specified "
            f"in the Ontario curriculum. Ontario publishes at grade-level "
            f"granularity; within-year progression is a school and teacher decision."
        ),
    )
    return [
        {
            "label": label,
            "approximate_age_range": f"ages {age_low}-{age_high}",
            "approximate_grade_year": label,
            "developmental_descriptor": descriptor,
        }
    ]


def _ontario_progression_philosophy() -> str:
    """Progression philosophy for Ontario single-grade sources.

    Drawn from the Ontario Ministry of Education's curriculum framework
    overview and the K-8 Social Studies, History and Geography curriculum
    documentation.
    """
    return (
        "Grade-level expectations published at grade-level granularity. Each "
        "grade's curriculum is designed to be met by learners in that grade by "
        "year's end. Ontario does not define sub-grade progression bands within "
        "curriculum documents; within-year sequencing is a school and teacher "
        "decision. Single-band output reflects the source's own granularity."
    )


def _single_grade_self_reflection_prompt(grade_label: str) -> dict[str, str]:
    """Generic single-grade self-reflection prompt for a grade-level source.

    Single-band sources (one Common Core grade, one Ontario grade) do
    not progress across bands inside the source. The Mode 3 prompt is
    a single grade-appropriate reflection prompt rather than a
    progression. Calibration to the grade's own developmental band is
    deliberately conservative — the pipeline does not have access to
    cross-grade Common Core or Ontario "developmental" wording, so the
    prompt is held at "describe one thing you have noticed" middle-
    grade level.
    """

    return {
        grade_label: (
            f"Describe one thing you have noticed about yourself this term in this area. "
            f"When does it happen, and when does it not? "
            f"(Single-grade source: {grade_label}.)"
        )
    }


def _welsh_cfw_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(WELSH_CFW_PS_LABELS),
        band_count=len(WELSH_CFW_PS_LABELS),
        age_range_hint="ages 3-16 (Welsh Government Curriculum for Wales overview, statutory under the Curriculum and Assessment (Wales) Act 2021)",
        source_type="welsh_cfw_aole",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=dict(WELSH_CFW_PS_SELF_REFLECTION_PROMPTS),
        band_details=list(WELSH_CFW_PS_BAND_DETAILS),
        progression_philosophy=WELSH_CFW_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _common_core_grade_structure(
    *, grade: int, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    label = f"Grade {grade}"
    age_low = grade + 5
    age_high = grade + 6
    return ProgressionStructure(
        band_labels=[label],
        band_count=1,
        age_range_hint=(
            f"ages {age_low}-{age_high} (Common Core State Standards Initiative; CCSSO grade alignment)"
        ),
        source_type="us_common_core_grade",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_single_grade_self_reflection_prompt(label),
        band_details=_common_core_grade_band_details(grade),
        progression_philosophy=_common_core_progression_philosophy(),
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _ontario_grade_structure(
    *, grade: int, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    label = f"Grade {grade}"
    age_low = grade + 5
    age_high = grade + 6
    return ProgressionStructure(
        band_labels=[label],
        band_count=1,
        age_range_hint=(
            f"ages {age_low}-{age_high} (Ontario Ministry of Education K-12 schedule)"
        ),
        source_type="ontario_grade",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_single_grade_self_reflection_prompt(label),
        band_details=_ontario_grade_band_details(grade),
        progression_philosophy=_ontario_progression_philosophy(),
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _scottish_cfe_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(SCOTTISH_CFE_LEVEL_LABELS),
        band_count=len(SCOTTISH_CFE_LEVEL_LABELS),
        age_range_hint=(
            "ages 3-18 (Education Scotland; Building the Curriculum; CfE benchmarks)"
        ),
        source_type="scottish_cfe",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=dict(SCOTTISH_CFE_SELF_REFLECTION_PROMPTS),
        band_details=list(SCOTTISH_CFE_BAND_DETAILS),
        progression_philosophy=SCOTTISH_CFE_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _england_nc_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(ENGLAND_KS_LABELS),
        band_count=len(ENGLAND_KS_LABELS),
        age_range_hint=(
            "ages 5-16 (DfE statutory National Curriculum framework; KS1 5-7, KS2 7-11, KS3 11-14, KS4 14-16)"
        ),
        source_type="england_national_curriculum",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=dict(ENGLAND_KS_SELF_REFLECTION_PROMPTS),
        band_details=list(ENGLAND_KS_BAND_DETAILS),
        progression_philosophy=ENGLAND_NC_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


def _nz_curriculum_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> ProgressionStructure:
    return ProgressionStructure(
        band_labels=list(NZ_LEVEL_LABELS),
        band_count=len(NZ_LEVEL_LABELS),
        age_range_hint=(
            "ages 5-18 (Ministry of Education NZ; The New Zealand Curriculum)"
        ),
        source_type="nz_curriculum",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_nz_self_reflection_prompts(),
        band_details=list(NZ_BAND_DETAILS),
        progression_philosophy=NZ_CURRICULUM_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


# ---------------------------------------------------------------------------
# AP US Government and Politics CED — single-unit band.
#
# College Board AP US Government and Politics Course and Exam Description
# (CED). The course is organised into 9 units. Each unit is a standalone
# content scope, analogous to a single Common Core grade domain. The AP
# course is designed for Grade 11-12 (ages 16-18) per College Board
# grade-level alignment guidance.
#
# Unit 1: Foundations of American Democracy. Big Ideas 1-2 (Constitutionalism,
# Liberal Democracy), approximately 15-22% of AP exam weighting.
# Per College Board CED V.1 (2023).
# ---------------------------------------------------------------------------

_AP_USGOV_UNIT_BAND_DETAILS: list[dict] = [
    {
        "label": "Unit 1",
        "approximate_age_range": "ages 16-18",
        "approximate_grade_year": "Grade 11-12",
        "developmental_descriptor": (
            "AP US Government and Politics learners in Unit 1 establish the "
            "constitutional foundations of American democracy: Enlightenment "
            "principles, Articles of Confederation limitations, Constitutional "
            "Convention compromises, Federalist and Anti-Federalist arguments, "
            "and the structure of constitutional government. They apply political "
            "science concepts to primary-source analysis and argument construction "
            "at a college-preparatory level."
        ),
    }
]

_AP_USGOV_PROGRESSION_PHILOSOPHY = (
    "AP US Government and Politics is a college-level course, typically taken in "
    "Grades 11-12. The Course and Exam Description (CED) organises content into 9 "
    "units; this source covers Unit 1 only. Within-unit progression is a teacher "
    "and district decision; the CED specifies learning objectives and essential "
    "knowledge, not a week-by-week sequence. Single-band output reflects the "
    "source's own unit granularity, not an absence of internal structure within "
    "the teaching period. Per College Board AP US Government and Politics CED V.1 "
    "(2023)."
)

_AP_USGOV_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Unit 1": (
        "Describe one constitutional principle you have studied in this unit. "
        "How does it connect to debates happening in the news today, and where "
        "do you see tension between the principle as written and its application?"
    )
}


def _ap_usgov_unit_structure(
    *, unit: int, source_reference: str, source_slug: str, rationale: str
) -> "ProgressionStructure":
    label = f"Unit {unit}"
    return ProgressionStructure(
        band_labels=[label],
        band_count=1,
        age_range_hint=(
            "ages 16-18 (College Board AP US Government and Politics; "
            "typically Grades 11-12)"
        ),
        source_type="us_ap_course_unit",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_AP_USGOV_SELF_REFLECTION_PROMPTS,
        band_details=_AP_USGOV_UNIT_BAND_DETAILS,
        progression_philosophy=_AP_USGOV_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


# ---------------------------------------------------------------------------
# DfE England National Curriculum — KS3-only single-band.
#
# The DfE publishes subject-specific programmes of study for individual Key
# Stages. When the source is a single-KS document (e.g. the KS3 Mathematics
# programme of study), the correct structure is a single band for that Key
# Stage, not the full KS1-4 sequence. The source text typically references
# adjacent Key Stages (e.g. "building on Key Stage 2"), which would mislead
# the source-text-inspection fallback into producing a multi-KS structure.
# This curated entry prevents that false-positive.
#
# Age range per DfE statutory national curriculum framework: KS3 ages 11-14
# (Years 7-9). Source reference URL pattern: assets.publishing.service.gov.uk.
# ---------------------------------------------------------------------------

_DFE_KS3_BAND_DETAILS: list[dict] = [
    {
        "label": "Key Stage 3",
        "approximate_age_range": "ages 11-14",
        "approximate_grade_year": "Years 7-9",
        "developmental_descriptor": (
            "Key Stage 3 learners engage with a broad curriculum across specialised "
            "subject disciplines. They develop critical thinking, abstract reasoning, "
            "and the capacity to work independently and collaboratively, building on "
            "Key Stage 2 foundations toward Key Stage 4 qualifications."
        ),
    }
]

_DFE_KS3_PROGRESSION_PHILOSOPHY = (
    "Key Stage 3 is a statutory curriculum phase defined by the DfE national "
    "curriculum framework, covering ages 11-14 (Years 7-9). Programmes of study "
    "specify what pupils should be taught; progression within KS3 (year-by-year "
    "sequencing) is a school and teacher decision. Single-band output reflects "
    "the source's own Key Stage granularity. Per DfE statutory national curriculum "
    "framework (England)."
)

_DFE_KS3_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "Key Stage 3": (
        "Describe one thing you have noticed about how you approach this subject this "
        "term. When does your approach work well, and when does it not?"
    )
}


def _dfe_ks3_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> "ProgressionStructure":
    return ProgressionStructure(
        band_labels=["Key Stage 3"],
        band_count=1,
        age_range_hint=(
            "ages 11-14 (DfE statutory national curriculum framework, England; KS3 = Years 7-9)"
        ),
        source_type="england_nc_ks3_only",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_DFE_KS3_SELF_REFLECTION_PROMPTS,
        band_details=_DFE_KS3_BAND_DETAILS,
        progression_philosophy=_DFE_KS3_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


# ---------------------------------------------------------------------------
# DfE England — RSHE statutory guidance (secondary).
#
# The RSHE statutory guidance sets terminal outcomes framed as "by the end of
# secondary school" — a single developmental endpoint, not a multi-level
# progression. It covers the full secondary phase (ages 11–16, Years 7–11,
# KS3 + KS4). There are no Key Stage sub-divisions within the secondary
# content; KS3 and KS4 outcomes are interleaved under topic headings.
#
# This curated entry prevents the source-text-inspection fallback from
# producing a multi-KS structure because the document text references
# "Key Stage 3" and "Key Stage 4" in the same paragraphs.
#
# Source: DfE "Relationships Education, Relationships and Sex Education (RSE)
# and Health Education (for introduction 1 September 2026)".
# Published: assets.publishing.service.gov.uk.
# Statutory authority: Children and Social Work Act 2017.
# ---------------------------------------------------------------------------

_ENGLAND_RSHE_SECONDARY_BAND_DETAILS: list[dict] = [
    {
        "label": "End of Secondary",
        "approximate_age_range": "ages 11-16",
        "approximate_grade_year": "Years 7-11 (KS3 and KS4)",
        "developmental_descriptor": (
            "Secondary pupils develop the knowledge, values and personal qualities "
            "needed to navigate relationships, health and wellbeing across the full "
            "secondary phase. Outcomes are framed as terminal goals for all secondary "
            "pupils; year-group sequencing is a school decision."
        ),
    }
]

_ENGLAND_RSHE_SECONDARY_PROGRESSION_PHILOSOPHY = (
    "The DfE RSHE statutory guidance sets outcomes as 'by the end of secondary school' "
    "terminal statements. Unlike the National Curriculum, which has Key Stage progression, "
    "RSHE uses a single secondary-phase endpoint. Single-band output reflects the "
    "guidance's own structure. Per DfE statutory RSHE guidance (England), "
    "Children and Social Work Act 2017."
)

_ENGLAND_RSHE_SECONDARY_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "End of Secondary": (
        "Think about a situation this term where you had to make a decision about "
        "a relationship or your own wellbeing. What did you consider, and what would "
        "you do differently now?"
    )
}


def _england_rshe_secondary_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> "ProgressionStructure":
    return ProgressionStructure(
        band_labels=["End of Secondary"],
        band_count=1,
        age_range_hint=(
            "ages 11-16 (DfE RSHE statutory guidance; secondary phase = Years 7-11, "
            "KS3 + KS4; outcomes framed as 'by the end of secondary school')"
        ),
        source_type="england_rshe_secondary",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=_ENGLAND_RSHE_SECONDARY_SELF_REFLECTION_PROMPTS,
        band_details=_ENGLAND_RSHE_SECONDARY_BAND_DETAILS,
        progression_philosophy=_ENGLAND_RSHE_SECONDARY_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


# ---------------------------------------------------------------------------
# DfE England — RSHE statutory guidance (full programme, primary + secondary).
#
# The full RSHE statutory guidance covers both phases:
#   - Relationships Education (Primary): "content to be covered by the end of primary"
#     Pages 9-12 of the July 2025 statutory guidance.
#   - Primary Health and Wellbeing: "content to be covered by the end of primary"
#     Pages 22-26 of the July 2025 statutory guidance.
#   - Secondary RSE: "content to be covered by the end of secondary"
#     Pages 14-20 of the July 2025 statutory guidance.
#   - Secondary Health and Wellbeing: "content to be covered by the end of secondary"
#     Pages 28-32 of the July 2025 statutory guidance.
#
# The document uses "primary" and "secondary" phases, NOT individual Key Stages.
# There is no KS1/KS2 subdivision within primary content, and no KS3/KS4
# subdivision within secondary content. The two-band structure faithfully
# represents the document's own architecture.
#
# Source: DfE "Relationships Education, RSE and Health Education" (July 2025).
# Statutory authority: Children and Social Work Act 2017.
# Slug: uk-statutory-rshe
# ---------------------------------------------------------------------------

_ENGLAND_RSHE_FULL_BAND_DETAILS: list[dict] = [
    {
        "label": "End of Primary",
        "approximate_age_range": "ages 5-11",
        "approximate_grade_year": "Years 1-6 (KS1 and KS2)",
        "developmental_descriptor": (
            "Primary pupils develop the foundational skills and knowledge needed "
            "for positive relationships, personal safety, and health. Outcomes are "
            "framed as terminal goals for all primary pupils; year-group and KS1/KS2 "
            "sequencing is a school decision. Primary relationships education does "
            "not include RSE content; sex education in primary is non-statutory."
        ),
    },
    {
        "label": "End of Secondary",
        "approximate_age_range": "ages 11-16",
        "approximate_grade_year": "Years 7-11 (KS3 and KS4)",
        "developmental_descriptor": (
            "Secondary pupils develop the knowledge, values and personal qualities "
            "needed to navigate relationships, sex and health across the full "
            "secondary phase. Outcomes are framed as terminal goals for all secondary "
            "pupils; KS3/KS4 and year-group sequencing is a school decision."
        ),
    },
]

_ENGLAND_RSHE_FULL_PROGRESSION_PHILOSOPHY = (
    "The DfE RSHE statutory guidance (July 2025) uses a two-phase architecture: "
    "'content to be covered by the end of primary' and 'content to be covered by "
    "the end of secondary'. Neither phase is subdivided into individual Key Stages "
    "within the curriculum content sections. Two-band output reflects the guidance's "
    "own structure. Per DfE statutory RSHE guidance (England), Children and Social "
    "Work Act 2017."
)

_ENGLAND_RSHE_FULL_SELF_REFLECTION_PROMPTS: dict[str, str] = {
    "End of Primary": (
        "Think about one relationship in your life — with a friend, family member, "
        "or classmate. What makes it feel safe and kind? Is there anything you would "
        "like to be different?"
    ),
    "End of Secondary": (
        "Think about a situation this term where you had to make a decision about "
        "a relationship or your own wellbeing. What did you consider, and what would "
        "you do differently now?"
    ),
}


def _england_rshe_full_structure(
    *, source_reference: str, source_slug: str, rationale: str
) -> "ProgressionStructure":
    return ProgressionStructure(
        band_labels=["End of Primary", "End of Secondary"],
        band_count=2,
        age_range_hint=(
            "ages 5-16 (DfE RSHE statutory guidance July 2025; primary phase = Years 1-6, "
            "secondary phase = Years 7-11; two-phase structure, no within-phase KS subdivision)"
        ),
        source_type="england_rshe_full",
        detection_confidence="high",
        detection_rationale=rationale,
        band_self_reflection_prompts=dict(_ENGLAND_RSHE_FULL_SELF_REFLECTION_PROMPTS),
        band_details=list(_ENGLAND_RSHE_FULL_BAND_DETAILS),
        progression_philosophy=_ENGLAND_RSHE_FULL_PROGRESSION_PHILOSOPHY,
        source_reference=source_reference,
        source_slug=source_slug,
    )


# ---------------------------------------------------------------------------
# URL- and slug-based dispatch
# ---------------------------------------------------------------------------


def _match_url(source_reference: str) -> tuple[str, str] | None:
    """Return (host_lower, path_lower) tuple if the URL parses cleanly."""
    if not source_reference:
        return None
    try:
        parsed = urlparse(source_reference.strip())
    except ValueError:
        return None
    host = (parsed.netloc or "").lower().lstrip("www.")
    path = (parsed.path or "").lower()
    return host, path


_GRADE_FROM_SLUG = re.compile(r"(?:^|[-_])g(?:rade)?[-_]?(\d{1,2})(?:[-_]|$)")


def _grade_from_slug(slug: str) -> int | None:
    if not slug:
        return None
    m = _GRADE_FROM_SLUG.search(slug.lower())
    if not m:
        return None
    g = int(m.group(1))
    if 1 <= g <= 12:
        return g
    return None


def _lookup_high_confidence(
    *, source_reference: str, source_slug: str
) -> ProgressionStructure | None:
    matched = _match_url(source_reference)
    slug_lower = (source_slug or "").lower()

    # --- Welsh CfW (any AOLE) --------------------------------------------------
    if matched is not None:
        host, path = matched
        if host.endswith("hwb.gov.wales") and "curriculum-for-wales" in path:
            return _welsh_cfw_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    "URL host hwb.gov.wales with /curriculum-for-wales path — "
                    "Welsh Curriculum for Wales uses Progression Steps 1-5 across "
                    "ages 3-16 per Welsh Government statutory specification."
                ),
            )
    if "wales-cfw" in slug_lower or "welsh-cfw" in slug_lower or slug_lower.startswith("wales-"):
        return _welsh_cfw_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches Welsh CfW pattern — "
                "Welsh Curriculum for Wales uses Progression Steps 1-5."
            ),
        )

    # --- US Common Core (single-grade) ----------------------------------------
    if matched is not None:
        host, path = matched
        if "corestandards.org" in host or "commoncore" in slug_lower:
            grade = _grade_from_slug(slug_lower)
            # Common Core 7.RP slug contains "common-core-7rp" or similar.
            m_rp = re.search(r"(\d{1,2})\.rp", path) if path else None
            if grade is None and m_rp:
                grade = int(m_rp.group(1))
            m_slug_rp = re.search(r"(\d{1,2})rp", slug_lower)
            if grade is None and m_slug_rp:
                grade = int(m_slug_rp.group(1))
            if grade is None:
                grade = _grade_from_slug(slug_lower)
            if grade is not None:
                return _common_core_grade_structure(
                    grade=grade,
                    source_reference=source_reference,
                    source_slug=source_slug,
                    rationale=(
                        f"Common Core source detected (host={host}, slug={source_slug}); "
                        f"grade {grade} extracted. Single-grade source — band_count=1."
                    ),
                )
    if slug_lower.startswith("common-core-") or "common-core-" in slug_lower:
        grade = _grade_from_slug(slug_lower)
        m = re.search(r"(\d{1,2})rp", slug_lower)
        if grade is None and m:
            grade = int(m.group(1))
        if grade is not None:
            return _common_core_grade_structure(
                grade=grade,
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"Source slug '{source_slug}' matches Common Core pattern; "
                    f"grade {grade} extracted. Single-grade source — band_count=1."
                ),
            )

    # --- Ontario K-8 (single-grade) -------------------------------------------
    if matched is not None:
        host, path = matched
        if "edu.gov.on.ca" in host or "ontario.ca" in host:
            grade = _grade_from_slug(slug_lower) or _grade_from_slug(path)
            if grade is not None:
                return _ontario_grade_structure(
                    grade=grade,
                    source_reference=source_reference,
                    source_slug=source_slug,
                    rationale=(
                        f"Ontario Ministry of Education source (host={host}); "
                        f"grade {grade} extracted. Single-grade source — band_count=1."
                    ),
                )
    if slug_lower.startswith("ontario-") or "ontario" in slug_lower:
        grade = _grade_from_slug(slug_lower)
        if grade is not None:
            return _ontario_grade_structure(
                grade=grade,
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"Source slug '{source_slug}' matches Ontario pattern; "
                    f"grade {grade} extracted. Single-grade source — band_count=1."
                ),
            )

    # --- Scottish CfE ---------------------------------------------------------
    if matched is not None:
        host, _path = matched
        if "education.gov.scot" in host or "scotland.gov.uk" in host:
            return _scottish_cfe_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"Scottish source detected (host={host}); CfE uses Early / "
                    "First / Second / Third / Fourth Levels + Senior Phase."
                ),
            )
    if "scottish-cfe" in slug_lower or "scotland-cfe" in slug_lower:
        return _scottish_cfe_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches Scottish CfE pattern."
            ),
        )

    # --- England NC -----------------------------------------------------------
    if matched is not None:
        host, path = matched
        if "gov.uk" in host and "national-curriculum" in path:
            return _england_nc_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"England National Curriculum source detected (host={host}, "
                    f"path includes /national-curriculum). Key Stages 1-4."
                ),
            )
    if slug_lower.startswith("dfe-") or "national-curriculum" in slug_lower or "uk-national-curriculum" in slug_lower:
        return _england_nc_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches England National Curriculum pattern."
            ),
        )

    # --- NZ Curriculum --------------------------------------------------------
    if matched is not None:
        host, _path = matched
        if "education.govt.nz" in host or "tki.org.nz" in host:
            return _nz_curriculum_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"New Zealand Curriculum source (host={host}). Levels 1-8."
                ),
            )
    if "nz-curriculum" in slug_lower or "new-zealand-curriculum" in slug_lower:
        return _nz_curriculum_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches NZ Curriculum pattern."
            ),
        )

    # --- AP US Government and Politics CED (unit-scoped source) --------------
    # Matches slugs containing 'ap-usgov' or 'ap-us-gov'. The unit number is
    # extracted from the slug (e.g. 'ap-usgov-ced-unit1' → unit=1). Defaults
    # to unit 1 if no unit number is found. URL match: ap.collegeboard.org.
    if matched is not None:
        host, path = matched
        if "collegeboard.org" in host and ("usgov" in path or "us-gov" in path or "government" in path):
            m_unit = re.search(r"unit[-_]?(\d+)", slug_lower)
            unit = int(m_unit.group(1)) if m_unit else 1
            return _ap_usgov_unit_structure(
                unit=unit,
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"AP US Government and Politics CED detected (host={host}); "
                    f"unit {unit} extracted. Single-unit source — band_count=1."
                ),
            )
    if "ap-usgov" in slug_lower or "ap-us-gov" in slug_lower:
        m_unit = re.search(r"unit[-_]?(\d+)", slug_lower)
        unit = int(m_unit.group(1)) if m_unit else 1
        return _ap_usgov_unit_structure(
            unit=unit,
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches AP US Government and Politics "
                f"pattern; unit {unit} extracted. Single-unit source — band_count=1."
            ),
        )

    # --- DfE England NC — KS3-only single-band --------------------------------
    # Matches slugs containing 'dfe-ks3' or 'ks3-maths' / 'ks3-english', etc.
    # Also matches the assets.publishing.service.gov.uk URL pattern for DfE
    # subject-specific KS3 PDFs. This prevents the source-text-inspection
    # fallback from producing a multi-KS structure because KS3 documents
    # typically reference Key Stage 2 (as prior stage) in their introductory text.
    if matched is not None:
        host, path = matched
        if "assets.publishing.service.gov.uk" in host and "secondary_national_curriculum" in path.replace("-", "_"):
            return _dfe_ks3_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"DfE assets.publishing.service.gov.uk source with secondary NC "
                    f"path detected (host={host}). KS3-only single-band structure."
                ),
            )
    if "dfe-ks3" in slug_lower or ("ks3" in slug_lower and ("dfe" in slug_lower or "maths" in slug_lower or "english" in slug_lower)):
        return _dfe_ks3_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches DfE KS3 single-subject pattern. "
                "KS3-only single-band structure (prevents multi-KS false positive from "
                "source-text inspection on documents that reference KS2 as prior stage)."
            ),
        )

    # --- DfE England RSHE (full programme, primary + secondary) ---------------
    # Matches slugs containing 'uk-statutory-rshe' or 'rshe-full'. Two-band
    # structure: End of Primary + End of Secondary. Must be checked BEFORE the
    # secondary-only RSHE entry below, which also matches 'rshe' in the slug.
    if "uk-statutory-rshe" in slug_lower or "rshe-full" in slug_lower or "uk-rshe-full" in slug_lower:
        return _england_rshe_full_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches DfE RSHE full-programme pattern. "
                "Two-band structure: End of Primary (ages 5-11) + End of Secondary "
                "(ages 11-16). DfE statutory RSHE guidance (July 2025)."
            ),
        )

    # --- DfE England RSHE (secondary) -----------------------------------------
    # Matches the assets.publishing.service.gov.uk URL for the RSHE statutory
    # guidance, or slugs containing 'rshe'. Single-band 'End of Secondary'
    # structure (ages 11-16). Prevents the source-text fallback from producing
    # a multi-KS structure because the document references both KS3 and KS4.
    # NOTE: the full-programme check above fires first for 'uk-statutory-rshe'.
    if matched is not None:
        host, path = matched
        if "assets.publishing.service.gov.uk" in host and "relationships" in path:
            return _england_rshe_secondary_structure(
                source_reference=source_reference,
                source_slug=source_slug,
                rationale=(
                    f"DfE RSHE statutory guidance detected (host={host}, "
                    "path contains 'relationships'). Single-band End-of-Secondary "
                    "structure (ages 11-16)."
                ),
            )
    if "rshe" in slug_lower or "secondary-rshe" in slug_lower:
        return _england_rshe_secondary_structure(
            source_reference=source_reference,
            source_slug=source_slug,
            rationale=(
                f"Source slug '{source_slug}' matches RSHE pattern. "
                "Single-band End-of-Secondary structure (ages 11-16)."
            ),
        )

    return None


# ---------------------------------------------------------------------------
# Source-text inspection fallback (medium confidence)
# ---------------------------------------------------------------------------


_PROGRESSION_STEP_RE = re.compile(
    r"\bProgression Step ?(\d+)\b", re.IGNORECASE
)
_GRADE_TEXT_RE = re.compile(r"\bGrade ?(\d{1,2})\b", re.IGNORECASE)
_KEY_STAGE_RE = re.compile(r"\bKey Stage ?(\d)\b", re.IGNORECASE)
_LEVEL_RE = re.compile(r"\bLevel ?(\d{1,2})\b", re.IGNORECASE)
_CFE_LEVEL_RE = re.compile(
    r"\b(Early|First|Second|Third|Fourth)\s+Level\b", re.IGNORECASE
)


def _inspect_source_text(
    inventory: SourceInventory, *, source_reference: str, source_slug: str
) -> ProgressionStructure | None:
    text = "\n".join(b.raw_text for b in inventory.content_blocks)

    ps_matches = sorted({int(m.group(1)) for m in _PROGRESSION_STEP_RE.finditer(text)})
    if ps_matches:
        labels = [f"Progression Step {i}" for i in sorted(set(ps_matches))]
        if all(1 <= n <= 5 for n in ps_matches) and len(labels) >= 2:
            # Looks Welsh-CfW-shaped but the URL/slug didn't match.
            return ProgressionStructure(
                band_labels=labels,
                band_count=len(labels),
                age_range_hint="age range unverified — source-text inspection only",
                source_type="welsh_cfw_aole_inferred",
                detection_confidence="medium",
                detection_rationale=(
                    f"Source text contains explicit 'Progression Step' markers "
                    f"({sorted(set(ps_matches))}); structure inferred without "
                    "URL/slug match."
                ),
                band_self_reflection_prompts={
                    label: WELSH_CFW_PS_SELF_REFLECTION_PROMPTS.get(label, "")
                    for label in labels
                },
                source_reference=source_reference,
                source_slug=source_slug,
            )

    cfe_matches = sorted(
        {m.group(1).capitalize() + " Level" for m in _CFE_LEVEL_RE.finditer(text)}
    )
    if cfe_matches and len(cfe_matches) >= 2:
        ordered = [
            label
            for label in SCOTTISH_CFE_LEVEL_LABELS
            if label in cfe_matches
        ]
        return ProgressionStructure(
            band_labels=ordered,
            band_count=len(ordered),
            age_range_hint="age range unverified — source-text inspection only",
            source_type="scottish_cfe_inferred",
            detection_confidence="medium",
            detection_rationale=(
                f"Source text contains CfE Level markers ({ordered}); "
                "structure inferred without URL/slug match."
            ),
            band_self_reflection_prompts={
                label: SCOTTISH_CFE_SELF_REFLECTION_PROMPTS.get(label, "")
                for label in ordered
            },
            source_reference=source_reference,
            source_slug=source_slug,
        )

    ks_matches = sorted({int(m.group(1)) for m in _KEY_STAGE_RE.finditer(text)})
    if ks_matches and all(1 <= n <= 4 for n in ks_matches) and len(ks_matches) >= 2:
        labels = [f"Key Stage {i}" for i in sorted(set(ks_matches))]
        return ProgressionStructure(
            band_labels=labels,
            band_count=len(labels),
            age_range_hint="age range unverified — source-text inspection only",
            source_type="england_national_curriculum_inferred",
            detection_confidence="medium",
            detection_rationale=(
                f"Source text contains explicit Key Stage markers ({ks_matches})."
            ),
            band_self_reflection_prompts={
                label: ENGLAND_KS_SELF_REFLECTION_PROMPTS.get(label, "")
                for label in labels
            },
            source_reference=source_reference,
            source_slug=source_slug,
        )

    grade_matches = sorted({int(m.group(1)) for m in _GRADE_TEXT_RE.finditer(text)})
    if grade_matches and len(grade_matches) == 1 and 1 <= grade_matches[0] <= 12:
        grade = grade_matches[0]
        label = f"Grade {grade}"
        return ProgressionStructure(
            band_labels=[label],
            band_count=1,
            age_range_hint="age range unverified — single-grade source-text inspection",
            source_type="single_grade_inferred",
            detection_confidence="medium",
            detection_rationale=(
                f"Source text contains a single Grade marker ({grade}); "
                "treated as a single-grade source — band_count=1."
            ),
            band_self_reflection_prompts=_single_grade_self_reflection_prompt(label),
            source_reference=source_reference,
            source_slug=source_slug,
        )

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_progression(inventory: SourceInventory) -> ProgressionStructure:
    """Detect the source's native progression structure.

    Tries (1) the curated jurisdiction lookup, then (2) source-text
    inspection. Raises ``ProgressionDetectionError`` if neither
    produces a usable structure — the pipeline is required to halt
    rather than silently default to A-D.
    """

    source_reference = inventory.source_reference or ""
    source_slug = inventory.source_slug or ""

    high = _lookup_high_confidence(
        source_reference=source_reference, source_slug=source_slug
    )
    if high is not None:
        return high

    medium = _inspect_source_text(
        inventory, source_reference=source_reference, source_slug=source_slug
    )
    if medium is not None:
        return medium

    raise ProgressionDetectionError(
        "Could not detect a native progression structure for source "
        f"slug='{source_slug}' reference='{source_reference}'. The "
        "reference-authoring pipeline does NOT default to A-D; add this "
        "source to curriculum_harness.reference_authoring.progression."
        "detect_progression's curated lookup table, or correct its "
        "source_reference / source_slug so an existing entry matches. "
        "Source-text inspection found no Progression Step / Key Stage / "
        "Level / single-Grade markers either."
    )


def load_progression_structure(path: str) -> ProgressionStructure:
    """Load a ``ProgressionStructure`` previously written to JSON."""

    import json

    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return ProgressionStructure(
        band_labels=list(raw.get("band_labels") or []),
        band_count=int(raw.get("band_count") or 0),
        age_range_hint=str(raw.get("age_range_hint") or ""),
        source_type=str(raw.get("source_type") or ""),
        detection_confidence=str(raw.get("detection_confidence") or "low"),
        detection_rationale=str(raw.get("detection_rationale") or ""),
        band_self_reflection_prompts=dict(raw.get("band_self_reflection_prompts") or {}),
        band_details=list(raw.get("band_details") or []),
        progression_philosophy=str(raw.get("progression_philosophy") or ""),
        source_reference=str(raw.get("source_reference") or ""),
        source_slug=str(raw.get("source_slug") or ""),
        detection_module_version=str(
            raw.get("detection_module_version") or PROGRESSION_DETECTION_VERSION
        ),
    )


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def band_label_slug(label: str) -> str:
    """Convert a band label to a CSV-safe lowercase slug.

    "Progression Step 1" -> "progression_step_1"
    "Grade 7"            -> "grade_7"
    "Early Level"        -> "early_level"
    """

    s = (label or "").strip().lower()
    s = _SLUG_RE.sub("_", s)
    return s.strip("_")
