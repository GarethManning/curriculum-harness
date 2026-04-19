"""Adversarial tests for strand detection.

Five adversarial cases spanning single-strand and multi-strand sources across
hierarchical and horizontal domains. All should produce expected results.

Test design:
- Cases are constructed from realistic curriculum text patterns, not
  from the three ground-truth sources already verified in the main detection run.
- Each case tests a specific edge condition or failure mode.
- Single-strand cases are labelled SS; multi-strand cases are labelled MS.
"""

import pytest

from curriculum_harness.reference_authoring.strand.detect_strands import (
    StrandDetectionUncertain,
    detect_strands,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def run_and_check_single_strand(content: str, context: str = ""):
    """Assert detection returns single_strand, not multi-strand."""
    result = detect_strands(content)
    assert not result.is_multi_strand, (
        f"{context}: expected single_strand but got multi_strand with "
        f"{len(result.strands)} strands: {[s.name for s in result.strands]}"
    )
    return result


def run_and_check_strands(content: str, expected_names: list[str], context: str = ""):
    """Assert detection returns exactly the expected strand names (case-insensitive)."""
    result = detect_strands(content)
    assert result.is_multi_strand, (
        f"{context}: expected multi_strand ({expected_names}) but got single_strand. "
        f"Rationale: {result.single_strand_rationale}"
    )
    detected = [s.name.lower().strip() for s in result.strands]
    expected = [e.lower().strip() for e in expected_names]
    assert detected == expected, (
        f"{context}: strand names mismatch.\n"
        f"  Expected: {expected}\n"
        f"  Detected: {detected}"
    )
    return result


# ---------------------------------------------------------------------------
# Case A (SS-1): Ontario-style single-grade horizontal source
#
# Ontario DCP Grade 7 History uses two strands (Heritage/Identity,
# Change/Continuity) but a single-grade source with no structural strand
# split in its extracted text looks like a single-strand source.
# This simulates a curriculum source where all content appears under one
# grade/strand heading with no repeated structural template.
# ---------------------------------------------------------------------------

ONTARIO_SINGLE_GRADE_CONTENT = """
Grade 7 History — Social Studies

Strand: Heritage and Identity

Overall Expectations
By the end of Grade 7, students will:
- analyse aspects of the development of French-speaking communities outside Quebec
- demonstrate an understanding of the contributions of diverse groups

Specific Expectations
Communities and their Connections
Students will:
- describe some of the main French-speaking communities outside Quebec in Canada
- explain the social and political factors that affect French-speaking communities
- analyse the contributions of individual French Canadians to Canadian history

Heritage Preservation
Students will:
- identify examples of heritage preservation in French-speaking communities
- explain why communities preserve their cultural heritage
"""


def test_case_a_ontario_single_strand_no_split():
    """Case A (SS-1): Source with one strand heading should be single-strand.

    The Ontario Grade 7 History source as ingested covers one strand section.
    Detection should not hallucinate a second strand.
    """
    result = run_and_check_single_strand(
        ONTARIO_SINGLE_GRADE_CONTENT,
        context="Case A: Ontario single-grade"
    )
    assert result.overall_confidence >= 0.60


# ---------------------------------------------------------------------------
# Case B (MS-1): Scottish CfE — hierarchical multi-strand
#
# Scottish Curriculum for Excellence Maths has strands: Number/Money/Measure,
# Shape/Position/Movement, Information Handling. Each has "I can..." outcomes
# and "Pupils should be taught to:" equivalents. Tests detection of a
# hierarchical multi-strand source with a different teaching-point phrase.
# ---------------------------------------------------------------------------

SCOTTISH_CFE_MATHS_CONTENT = """
Mathematics and Numeracy — Second Level
Curriculum for Excellence

Number, Money and Measure
Pupils should be taught to:
- count forwards and backwards in steps of various sizes
- read, write, and order whole numbers to 1,000,000
- use mental and written strategies for addition and subtraction of whole numbers
- understand and use decimal fractions including money in real-life contexts

Shape, Position and Movement
Pupils should be taught to:
- name and classify 2D shapes and 3D objects by their properties
- describe, follow, and record routes using compass directions and coordinates
- identify and describe line symmetry in 2D shapes
- understand rotation and reflection in real-life contexts

Information Handling
Pupils should be taught to:
- collect, organise, and display data using tally charts, bar charts, and pictograms
- read and interpret information from a variety of graphs and charts
- describe and interpret results from data displays
- understand the concept of probability on a 0–1 scale
"""


def test_case_b_scottish_cfe_hierarchical_multi_strand():
    """Case B (MS-1): Scottish CfE Maths — three hierarchical strands detected.

    Hierarchical domain. Teaching-point phrase used: 'Pupils should be taught to:'.
    Expected strands: Number/Money/Measure, Shape/Position/Movement,
    Information Handling.
    """
    run_and_check_strands(
        SCOTTISH_CFE_MATHS_CONTENT,
        expected_names=[
            "Number, Money and Measure",
            "Shape, Position and Movement",
            "Information Handling",
        ],
        context="Case B: Scottish CfE Maths"
    )


# ---------------------------------------------------------------------------
# Case C (SS-2): Welsh CfW Expressive Arts — single-strand with rich sub-topics
#
# The Expressive Arts AoLE in the Welsh Curriculum for Wales has four
# "disciplines" (Art and Design, Dance, Drama, Music) but at the top level
# presents as a single unified area. The ingested scope (statements of what
# matters) contains no repeating structural template beneath the discipline
# names. Sub-topic content does not have a "pupils should be taught to:"-style
# marker immediately after the discipline heading.
# ---------------------------------------------------------------------------

WELSH_EXPRESSIVE_ARTS_CONTENT = """
Expressive Arts
Area of Learning and Experience
Welsh Curriculum for Wales

Statements of what matters
Creating and communicating through the expressive arts.
This AoLE can help learners explore, understand and communicate their feelings and
ideas about the world through artistic expression. Learners engage with a range of
art forms to create and communicate meaning.

Exploring and responding to expressive arts.
The skills and dispositions developed through this AoLE support learners to observe,
describe, and respond to artistic works. Engagement with artistic works from a variety
of cultural contexts helps learners to develop aesthetic sensibilities.

Art and Design
The discipline of Art and Design supports learners to develop their visual literacy.
Colour, form, texture, and composition are explored through a range of media.

Dance
The discipline of Dance enables learners to use movement as a language.
Through choreography, performance, and appreciation, learners develop physical
literacy alongside artistic expression.

Drama
The discipline of Drama allows learners to explore human experience through role
and performance. Learners develop empathy through dramatic contexts.

Music
The discipline of Music enables learners to create, perform and respond to music.
Rhythm, pitch, texture and structure are explored through both performing and
listening.
"""


def test_case_c_welsh_expressive_arts_single_strand():
    """Case C (SS-2): Welsh Expressive Arts — single-strand despite discipline sub-headings.

    The discipline headings (Art and Design, Dance, Drama, Music) are
    sub-topics of a unified AoLE, not independently-runnable strands.
    They lack immediate teaching-point confirmation. The top-level headings
    are conceptual lenses ("Creating and communicating...", "Exploring and
    responding..."). Expected: single_strand.
    """
    result = run_and_check_single_strand(
        WELSH_EXPRESSIVE_ARTS_CONTENT,
        context="Case C: Welsh Expressive Arts"
    )


# ---------------------------------------------------------------------------
# Case D (MS-2): New Zealand Curriculum Science — horizontal multi-strand
#
# NZ Science Learning Area has four strands: Living World, Material World,
# Physical World, Planet Earth and Beyond. Each has Knowledge and Practices
# sub-sections — the same structural template as Social Sciences.
# Tests that the detector generalises to a horizontal science domain.
# ---------------------------------------------------------------------------

NZ_SCIENCE_CONTENT = """
Science Learning Area — NZ Curriculum (Phase 2, Years 4–6)

Living World
Knowledge
The facts, concepts, principles, and theories to teach.
Practices
The skills, strategies, and applications to teach.

Living World covers ecosystems, biodiversity, and life processes.
Organisms and their environments, adaptation, and life cycles.

Material World
Knowledge
The facts, concepts, principles, and theories to teach.
Practices
The skills, strategies, and applications to teach.

Material World covers matter, its properties, and chemical processes.
Substances and materials, their properties and changes.

Physical World
Knowledge
The facts, concepts, principles, and theories to teach.
Practices
The skills, strategies, and applications to teach.

Physical World covers physical phenomena: forces, motion, energy, and waves.
Mechanics, electricity, and optics.

Planet Earth and Beyond
Knowledge
The facts, concepts, principles, and theories to teach.
Practices
The skills, strategies, and applications to teach.

Planet Earth and Beyond covers earth systems and astronomy.
Geology, meteorology, and solar system.
"""


def test_case_d_nz_science_horizontal_multi_strand():
    """Case D (MS-2): NZ Science — four horizontal strands detected.

    Same structural template as NZ Social Sciences (Knowledge/Practices
    immediately after strand heading). Expected strands: Living World,
    Material World, Physical World, Planet Earth and Beyond.
    """
    run_and_check_strands(
        NZ_SCIENCE_CONTENT,
        expected_names=[
            "Living World",
            "Material World",
            "Physical World",
            "Planet Earth and Beyond",
        ],
        context="Case D: NZ Science"
    )


# ---------------------------------------------------------------------------
# Case E (SS-3): US Common Core — single grade, no strand split
#
# Common Core Standards are organised by grade then domain. A single-grade
# scope (e.g., Grade 7 Ratios and Proportional Relationships) is a single-
# strand source. Tests that a standards document with clear numbered standards
# but no strand-level headings produces a single-strand result.
# ---------------------------------------------------------------------------

COMMON_CORE_GRADE7_RP_CONTENT = """
Common Core State Standards — Mathematics
Grade 7: Ratios and Proportional Relationships

Cluster: Analyze proportional relationships and use them to solve real-world problems.

7.RP.A.1
Compute unit rates associated with ratios of fractions, including ratios of lengths,
areas, and other quantities measured in like or different units.

7.RP.A.2
Recognize and represent proportional relationships between quantities.
a. Decide whether two quantities are in a proportional relationship.
b. Identify the constant of proportionality (unit rate) in tables, graphs,
   equations, diagrams, and verbal descriptions.
c. Represent proportional relationships by equations.
d. Explain what a point (x, y) on the graph of a proportional relationship
   means in terms of the situation.

7.RP.A.3
Use proportional relationships to solve multistep ratio and percent problems.
Examples: simple interest, tax, markups and markdowns, gratuities and
commissions, fees, percent increase and decrease, percent error.
"""


def test_case_e_common_core_single_grade_single_strand():
    """Case E (SS-3): Common Core Grade 7 RP — single-strand source.

    A single-grade, single-domain Common Core scope has numbered standards
    but no strand-level heading structure. Expected: single_strand.
    """
    result = run_and_check_single_strand(
        COMMON_CORE_GRADE7_RP_CONTENT,
        context="Case E: Common Core Grade 7 RP"
    )


# ---------------------------------------------------------------------------
# Case F (EDGE): Source with exactly 2 strands should not raise Uncertain
# when each strand has strong teaching-point confirmation
# ---------------------------------------------------------------------------

TWO_STRAND_STRONG_CONTENT = """
Subject content

Biology
Pupils should be taught to:
- understand cell structure and function
- explain how organisms are classified into kingdoms
- describe the processes of photosynthesis and respiration

Chemistry
Pupils should be taught to:
- understand atomic structure and the periodic table
- explain chemical bonding and reactions
- describe acids, bases, and salts
"""


def test_case_f_two_strong_strands_not_uncertain():
    """Case F (EDGE): Two strands with strong evidence should not raise Uncertain.

    The uncertainty path is for exactly-2-strand cases with WEAK mean
    confidence. With strong explicit markers, 2 strands should confirm cleanly.
    """
    result = run_and_check_strands(
        TWO_STRAND_STRONG_CONTENT,
        expected_names=["Biology", "Chemistry"],
        context="Case F: Two strong strands"
    )
    assert result.overall_confidence >= 0.80


# ---------------------------------------------------------------------------
# Case G (EDGE): Wrapped PDF bullet does NOT become a strand
#
# Simulates the "Venn diagrams" false positive that occurred during development.
# A line that continues a bullet (starting with an uppercase proper noun)
# should not be detected as a strand because no teaching-point marker follows
# within the tight lookahead window.
# ---------------------------------------------------------------------------

PDF_WRAPPED_BULLET_CONTENT = """
Subject content

Probability
Pupils should be taught to:
 enumerate sets and unions/intersections of sets systematically, using tables, grids and
Venn diagrams
 generate theoretical sample spaces for single and combined events

Statistics
Pupils should be taught to:
 describe distributions of a variable through appropriate graphical representation
 construct and interpret tables, charts, and diagrams
"""


def test_case_g_wrapped_bullet_not_a_strand():
    """Case G (EDGE): 'Venn diagrams' continuation line is not a strand.

    The line 'Venn diagrams' continues the preceding bullet about enumeration.
    It starts with uppercase and is short, but no teaching-point marker
    follows within 2 lines. Expected strands: only Probability and Statistics.
    """
    result = run_and_check_strands(
        PDF_WRAPPED_BULLET_CONTENT,
        expected_names=["Probability", "Statistics"],
        context="Case G: PDF wrapped bullet"
    )


# ---------------------------------------------------------------------------
# Case H (EDGE): Cross-cutting section before strands is excluded
#
# "Working mathematically" appears before the strand-level content. It
# must not be detected as a strand even though it has teaching-point content.
# ---------------------------------------------------------------------------

DFE_STYLE_WITH_CROSSCUTTING_CONTENT = """
Working mathematically
Through the mathematics content, pupils should be taught to:
Develop fluency
 consolidate their numerical and mathematical capability

Reason mathematically
 extend their understanding of the number system

Subject content

Number
Pupils should be taught to:
 understand and use place value for decimals and integers
 use the four operations with integers and fractions

Algebra
Pupils should be taught to:
 use and interpret algebraic notation
 substitute numerical values into formulae
"""


def test_case_h_cross_cutting_excluded():
    """Case H (EDGE): 'Working mathematically' is excluded as a cross-cutting section.

    Even though 'Working mathematically' is followed by teaching-point content,
    it appears before the 'Subject content' anchor and is in CROSS_CUTTING_PATTERNS.
    Expected strands: only Number and Algebra.
    """
    result = run_and_check_strands(
        DFE_STYLE_WITH_CROSSCUTTING_CONTENT,
        expected_names=["Number", "Algebra"],
        context="Case H: Cross-cutting excluded"
    )
    for s in result.strands:
        assert "Working" not in s.name, (
            f"'Working mathematically' should not be a strand, got: {s.name}"
        )
