"""Adversarial test set for criterion_gates — Session 4c-2b.

Each case is hand-constructed to exercise a specific gate in isolation.
The purpose is two-fold:

1. Baseline: run against the CURRENT gate logic to record which cases
   fail and which pass before any changes.

2. Regression guard: after each gate-calibration commit, re-run this
   suite. A case that SHOULD fail must keep failing; a case identified
   as a false positive should start passing.

Cases
-----
CASE_A — observable_verb TRUE POSITIVE
    Competent descriptor uses "appreciates the complexity of" — a
    mental-state verb, not an observable action. This should fail the
    observable_verb gate both before and after fixes.

CASE_B — single_construct TRUE POSITIVE
    A genuine cross-level construct shift: Emerging assesses a student's
    ability to recall a historical date, while Competent assesses their
    ability to design a survey methodology. These are different cognitive
    constructs, not deeper engagement with the same one. Should fail
    single_construct both before and after fixes.

CASE_C — all-gates PASS (clean baseline)
    A well-formed five-level rubric on a single unambiguous construct
    with observable verbs at every level. Should pass all gates.

CASE_D — observable_verb TRUE POSITIVE (hierarchical context)
    The strict observable-verb rule should apply in hierarchical domains
    too. Extending descriptor uses "grasps", a non-observable mental-
    state verb. This is not a false positive — "grasps" should remain
    a failure after fixes because it genuinely isn't observable.

CASE_E — single_construct FALSE POSITIVE (lemmatisation bug)
    Adjacent levels use "victim" and "victims" to describe the same
    construct. Currently fails single_construct because _topic_lemmas
    returns raw strings with no lemmatisation. Should PASS after Commit B
    (lemmatisation fix) and Commit C (adjacency-with-lemmatisation fix).

    This is the documented false-positive from RSHE 2025 cluster_13_lt_02.

CASE_F — observable_verb FALSE POSITIVE (transfer verb, horizontal domain)
    Extending descriptor uses "transfers understanding to novel contexts
    and guides peers". "transfers" and "guides" are genuinely observable
    but absent from the pre-fix OBSERVABLE_VERBS. Should fail BEFORE
    Commit A and pass AFTER Commit A.

CASE_G — single_construct FALSE POSITIVE (vocabulary depth-shift)
    Adjacent levels describe the same construct (evaluating source
    credibility) but shift vocabulary from concrete ("checks author
    credentials") to abstract ("evaluates epistemological warrant").
    Pairwise lemma overlap is zero. Should still fail BEFORE Commit C
    and pass AFTER Commit C, because extending shares lemmas with
    developing via the adjacency chain.

    NOTE: this case is borderline — it tests that the Commit C logic
    (adjacency-with-lemmatisation) is more permissive than the current
    pairwise check, but not so permissive that CASE_B also passes.
"""

from __future__ import annotations

import pytest

from curriculum_harness.reference_authoring.gates.criterion_gates import (
    _gate_observable_verb,
    _gate_single_construct,
    _run_rubric_gates,
)
from curriculum_harness.reference_authoring.types import Rubric, RubricLevel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rubric(lt_id: str, levels: list[tuple[str, str]], kt: str = "Type 1") -> Rubric:
    """Build a minimal Rubric for gate testing."""
    level_objects = [
        RubricLevel(name=name, descriptor=desc)
        for name, desc in levels
    ]
    return Rubric(
        lt_id=lt_id,
        knowledge_type=kt,
        levels=level_objects,
        competent_framing_flag="pass",
    )


def _passes_observable_verb(rubric: Rubric) -> bool:
    return _gate_observable_verb(rubric).passed


def _passes_single_construct(rubric: Rubric) -> bool:
    return _gate_single_construct(rubric).passed


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

CASE_A = _rubric(
    "adversarial_case_a",
    [
        ("no_evidence", "No attempt to engage with democratic participation."),
        ("emerging", "With support, identifies some obvious features of democratic participation."),
        ("developing", "Describes key features of democratic participation but omits how they interact."),
        # Only mental-state verbs here: "appreciates", "understands", "interact".
        # None of these are in OBSERVABLE_VERBS — gate must fail.
        # "recognises" deliberately excluded; it IS observable and would save this level.
        ("competent", "Appreciates the complexity of democratic participation and understands how different elements interact."),
        ("extending", "Evaluates competing perspectives on democratic participation and justifies a reasoned position."),
    ],
)

CASE_B = _rubric(
    "adversarial_case_b",
    [
        ("no_evidence", "No attempt."),
        # Emerging: recall a date (declarative retrieval construct)
        ("emerging", "With support, recalls the date of the Battle of Hastings from memory."),
        # Developing stays on recall/timeline
        ("developing", "Independently recalls key dates and places them in chronological order."),
        # Competent: SHIFTS to survey design — a different cognitive construct entirely
        ("competent", "Designs a survey methodology, selects a representative sample, and justifies the sampling strategy."),
        ("extending", "Refines survey instruments based on pilot data and evaluates sampling bias systematically."),
    ],
)

CASE_C = _rubric(
    "adversarial_case_c",
    [
        ("no_evidence", "No attempt to identify ratio relationships."),
        ("emerging", "With support, identifies a ratio relationship but applies the procedure inconsistently."),
        ("developing", "Independently calculates unit rates but struggles with multi-step ratio problems."),
        ("competent", "Independently solves multi-step ratio problems and explains the solution strategy."),
        ("extending", "Solves complex ratio problems in novel contexts and evaluates alternative solution strategies."),
    ],
)

CASE_D = _rubric(
    "adversarial_case_d",
    [
        ("no_evidence", "No attempt to examine primary source documents."),
        ("emerging", "With support, identifies the author and date of a primary source."),
        ("developing", "Independently identifies author, date, and purpose of a primary source."),
        ("competent", "Independently analyses a primary source for bias, context, and purpose."),
        # "grasps" is a mental-state verb — NOT observable. Should fail even after fixes.
        ("extending", "Grasps the broader historiographical significance of primary source evidence."),
    ],
)

CASE_E = _rubric(
    "adversarial_case_e",
    [
        ("no_evidence", "No attempt to engage with the scenario."),
        # Emerging: topic lemmas = {specific, victims, incident, report}
        # Deliberately narrow vocabulary so "victims" is the ONLY potential bridge
        # to the developing level. No other shared topic words.
        ("emerging", "With support, recalls specific victims named in the incident report."),
        # Developing: topic lemmas = {victim, documents, sequence, events}
        # "victim" (singular) is the only word that lemmatises to the same stem as
        # "victims" in emerging. Raw string comparison gives zero overlap → gate fails.
        # Lemmatised comparison: "victims" → {"victims","victim"} matches "victim" → gate passes.
        ("developing", "Independently identifies the victim and documents the sequence of events."),
        ("competent", "Independently explains the harm experienced by the victim and analyses contributing factors."),
        ("extending", "Evaluates systemic harm patterns affecting victims and constructs arguments for preventive policy."),
    ],
)

CASE_F = _rubric(
    "adversarial_case_f",
    [
        ("no_evidence", "No attempt to evaluate online safety risks."),
        ("emerging", "With support, identifies some obvious online safety risks."),
        ("developing", "Independently identifies common online threats and describes appropriate responses."),
        ("competent", "Independently evaluates online threats and selects appropriate safety strategies."),
        # "transfers" and "guides" are observable but not in pre-fix OBSERVABLE_VERBS
        ("extending", "Transfers online safety evaluation skills to novel contexts and guides peers through threat assessment."),
    ],
)

CASE_G = _rubric(
    "adversarial_case_g",
    [
        ("no_evidence", "No attempt to assess source quality."),
        # Emerging: concrete surface vocabulary
        ("emerging", "With support, checks whether an author is named on the website."),
        # Developing: shared vocabulary with emerging (author, source)
        ("developing", "Independently checks author credentials and identifies the source organisation."),
        # Competent: shifts to more abstract vocabulary — still same construct
        ("competent", "Independently evaluates source credibility using author expertise, publication context, and evidence quality."),
        # Extending: abstract vocabulary shift — "epistemological warrant" shares no raw lemma with emerging
        # but developing→competent→extending is a continuous vocabulary path
        ("extending", "Evaluates epistemological warrant of sources and constructs reasoned arguments about evidential hierarchy."),
    ],
)


# ---------------------------------------------------------------------------
# CASE_A — observable_verb TRUE POSITIVE
# ---------------------------------------------------------------------------

class TestCaseA:
    """'Appreciates the complexity of' is not observable — must fail observable_verb."""

    def test_observable_verb_fails(self):
        assert not _passes_observable_verb(CASE_A), (
            "CASE_A: 'appreciates' is a mental-state verb; observable_verb gate must fail"
        )

    def test_single_construct_passes(self):
        # The construct is consistent — this is a single-construct rubric.
        assert _passes_single_construct(CASE_A), (
            "CASE_A: single construct preserved across levels — single_construct gate must pass"
        )


# ---------------------------------------------------------------------------
# CASE_B — single_construct TRUE POSITIVE (genuine construct shift)
# ---------------------------------------------------------------------------

class TestCaseB:
    """Emerging = date recall; Competent = survey design. Genuinely different constructs."""

    def test_single_construct_fails(self):
        result = _gate_single_construct(CASE_B)
        assert not result.passed, (
            f"CASE_B: Emerging assesses recall, Competent assesses survey design — "
            f"genuine construct shift must fail single_construct. "
            f"Pairs without overlap: {result.details['pairs_without_overlap']}"
        )

    def test_observable_verb_passes(self):
        # "recalls", "designs", "selects", "justifies", "refines", "evaluates" are observable.
        assert _passes_observable_verb(CASE_B), (
            "CASE_B: all descriptors use observable verbs — observable_verb gate must pass"
        )


# ---------------------------------------------------------------------------
# CASE_C — all-gates PASS (clean baseline)
# ---------------------------------------------------------------------------

class TestCaseC:
    """Well-formed ratio rubric — all gates should pass."""

    def test_observable_verb_passes(self):
        assert _passes_observable_verb(CASE_C)

    def test_single_construct_passes(self):
        assert _passes_single_construct(CASE_C)

    def test_all_gates_pass(self):
        _, passed, failures = _run_rubric_gates(CASE_C)
        # word_limit and level_progression may fire on our hand-crafted text;
        # we only assert on the two gates this session calibrates.
        assert "observable_verb" not in failures, (
            f"CASE_C: observable_verb gate should not fire on clean rubric. Failures: {failures}"
        )
        assert "single_construct" not in failures, (
            f"CASE_C: single_construct gate should not fire on clean rubric. Failures: {failures}"
        )


# ---------------------------------------------------------------------------
# CASE_D — observable_verb TRUE POSITIVE in hierarchical context
# ---------------------------------------------------------------------------

class TestCaseD:
    """'Grasps' at Extending is a mental-state verb — must fail before AND after fixes."""

    def test_observable_verb_fails(self):
        result = _gate_observable_verb(CASE_D)
        assert not result.passed, (
            f"CASE_D: 'grasps' is not observable; must fail even after OBSERVABLE_VERBS expansion. "
            f"Failing levels: {result.details['levels_missing_verb']}"
        )

    def test_extends_is_the_failing_level(self):
        result = _gate_observable_verb(CASE_D)
        assert "extending" in result.details["levels_missing_verb"], (
            "CASE_D: the failing level should be 'extending' (where 'grasps' appears)"
        )


# ---------------------------------------------------------------------------
# CASE_E — single_construct FALSE POSITIVE (lemmatisation bug)
# ---------------------------------------------------------------------------

class TestCaseE:
    """
    'victims' vs 'victim' — same construct, different surface form.

    BEFORE Commit B (lemmatisation fix): this test DOCUMENTS the false positive
    by asserting that the gate CURRENTLY fails. After Commit B, the assertion
    flips — see test_passes_after_lemmatisation_fix.
    """

    def test_passes_after_commit_b(self):
        """
        After Commit B: 'victims' and 'victim' lemmatise to the same stem.
        Gate must pass — no false positive on plural-only mismatch.
        """
        result = _gate_single_construct(CASE_E)
        assert result.passed, (
            f"CASE_E: 'victims'/'victim' share lemma 'victim' after Commit B — gate must pass. "
            f"Pairs without overlap: {result.details['pairs_without_overlap']}"
        )

    def test_observable_verb_passes(self):
        assert _passes_observable_verb(CASE_E), (
            "CASE_E: 'recalls', 'identifies', 'explains', 'evaluates' are observable — observable_verb gate must pass"
        )


# ---------------------------------------------------------------------------
# CASE_F — observable_verb FALSE POSITIVE (transfer verb)
# ---------------------------------------------------------------------------

class TestCaseF:
    """
    'transfers' and 'guides' at Extending are observable but absent from
    pre-fix OBSERVABLE_VERBS.

    BEFORE Commit A: documents the false positive (gate currently fails).
    AFTER Commit A: gate should pass.
    """

    def test_passes_after_commit_a(self):
        """After Commit A: 'transfers' and 'guides' are in OBSERVABLE_VERBS — gate must pass."""
        assert _passes_observable_verb(CASE_F), (
            "CASE_F: 'transfers'/'guides' are now in OBSERVABLE_VERBS — gate must pass"
        )

    def test_single_construct_passes(self):
        assert _passes_single_construct(CASE_F), (
            "CASE_F: single construct (online safety evaluation) preserved — must pass"
        )


# ---------------------------------------------------------------------------
# CASE_G — single_construct FALSE POSITIVE (vocabulary depth-shift)
# ---------------------------------------------------------------------------

class TestCaseG:
    """
    Source credibility rubric: emerging uses concrete vocabulary ('author named'),
    extending uses abstract vocabulary ('epistemological warrant').

    The construct is continuous — developing bridges emerging and competent,
    competent bridges developing and extending. No level is disconnected from
    the sequence as a whole.

    BEFORE Commit C: gate currently fails on at least one adjacent pair due
    to vocabulary depth-shift.
    AFTER Commit C (adjacency-with-lemmatisation): gate should pass because
    each level shares at least one lemma with an adjacent (not arbitrary) level.

    This case also verifies CASE_B still fails after Commit C — the adjacency
    requirement is not so loose that genuinely different constructs pass.
    """

    def test_passes_after_commit_b(self):
        """
        After Commit B: 'source' (competent) and 'sources' (extending) lemmatise
        to the same stem. Gate must pass — no false positive on plural-only mismatch.

        Note: the 'vocabulary depth-shift' in CASE_G turned out to be a lemmatisation
        bug (source/sources), not a true vocabulary shift. Commit B (lemmatisation in
        _topic_lemmas) resolved it without needing a separate logic change.
        """
        result = _gate_single_construct(CASE_G)
        assert result.passed, (
            f"CASE_G: 'source'/'sources' share lemma after Commit B — gate must pass. "
            f"Pairs without overlap: {result.details['pairs_without_overlap']}"
        )

    def test_observable_verb_passes(self):
        assert _passes_observable_verb(CASE_G), (
            "CASE_G: 'checks', 'identifies', 'evaluates', 'constructs' are all observable"
        )

    def test_case_b_still_fails_after_commit_c_would_apply(self):
        """
        Regression guard: CASE_B (genuine construct shift) must still fail
        single_construct even under the more permissive Commit C logic.
        This test should pass both before and after Commit C.
        """
        result = _gate_single_construct(CASE_B)
        assert not result.passed, (
            "CASE_B must still fail single_construct even after Commit C. "
            "If it passes, Commit C is too permissive."
        )
